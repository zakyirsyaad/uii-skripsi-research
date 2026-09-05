#!/usr/bin/env python3
"""Cari kata di basis data KBBI SQLite lokal milik pengguna.

    kbbi_lookup.py --word kualitatif
    kbbi_lookup.py --check "analisa,sistim,praktek,metodologi"
    kbbi_lookup.py --db ~/data/kbbi.sqlite --word implementasi

Hanya untuk validasi bahasa Indonesia. **Tidak pernah** dipakai sebagai bukti
klaim teknis atau ilmiah — ini kamus, bukan sumber penelitian.

Basis datanya tidak disertakan plugin; pengguna menyediakannya sendiri dan
menunjuk jalurnya lewat `kbbi_db_path` di `.skripsi.yaml`.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skripsi.config import load_config  # noqa: E402

# Skema hulu (dyazincahya/KBBI-SQL-database) memakai tabel `dictionary`
# berkolom word/arti/type, tapi salinan lokal bisa berbeda — jadi diintrospeksi.
# KBBI mencatat bentuk TIDAK BAKU sebagai lema tersendiri yang hanya merujuk ke
# bentuk bakunya — "ana·li·sa ? analisis", "prak.tek Lihat praktik". Karena itu
# "ada di kamus" TIDAK berarti baku; tanpa mendeteksi rujukan silang ini, sebuah
# pemeriksa justru meloloskan analisa, praktek, obyek, dan sistim.
#
# Tanda panah aslinya (→) hilang menjadi "?" saat data ini di-scrape dari KBBI,
# jadi keduanya diterima.
_CROSSREF = re.compile(
    r"^\S+(?:\s*/[^/]*/)?\s*(?:\?|→|->)\s*([\w'-]+)\s*$", re.UNICODE)
_LIHAT = re.compile(r"^\S+(?:\s*/[^/]*/)?\s*Lihat\s+([\w'-]+)\s*$", re.I | re.UNICODE)

WORD_COLUMNS = ("word", "kata", "lema", "entri")
MEANING_COLUMNS = ("arti", "meaning", "definisi", "makna")
TYPE_COLUMNS = ("type", "jenis", "kelas", "kelas_kata")


def discover_schema(conn: sqlite3.Connection) -> tuple[str, str, str, str]:
    """Temukan (tabel, kolom_kata, kolom_arti, kolom_jenis) dari basis data apa adanya."""
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    if not tables:
        raise SystemExit("Basis data tidak punya tabel apa pun.")

    for table in sorted(tables, key=lambda t: t != "dictionary"):
        cols = [r[1].lower() for r in conn.execute(f"PRAGMA table_info('{table}')")]
        word = next((c for c in WORD_COLUMNS if c in cols), None)
        if not word:
            continue
        meaning = next((c for c in MEANING_COLUMNS if c in cols), "")
        kind = next((c for c in TYPE_COLUMNS if c in cols), "")
        return table, word, meaning, kind

    raise SystemExit(
        f"Tidak menemukan tabel dengan kolom kata. Tabel tersedia: {', '.join(tables)}")


def standard_form(arti: str) -> str | None:
    """Bila definisi ini hanya rujukan silang, kembalikan bentuk bakunya."""
    for pattern in (_CROSSREF, _LIHAT):
        m = pattern.match((arti or "").strip())
        if m:
            return m.group(1)
    return None


def classify(hits: list[dict]) -> tuple[str, str]:
    """Kembalikan (status, bentuk_baku).

    status: `baku` | `tidak_baku` | `tidak_ada`

    Sebuah lema dinilai tidak baku hanya bila SELURUH entrinya berupa rujukan
    silang. Satu entri berdefinisi sungguhan sudah cukup membuatnya sah — kata
    seperti `bisa` punya makna sendiri di samping rujukan.
    """
    if not hits:
        return "tidak_ada", ""
    forms = [standard_form(h["arti"]) for h in hits]
    if all(forms):
        return "tidak_baku", forms[0] or ""
    return "baku", ""


def lookup(conn, schema, word: str, exact: bool = True) -> list[dict]:
    table, wcol, mcol, tcol = schema
    select = [f'"{wcol}" AS kata']
    select.append(f'"{mcol}" AS arti' if mcol else "'' AS arti")
    select.append(f'"{tcol}" AS jenis' if tcol else "'' AS jenis")
    op, value = ("=", word) if exact else ("LIKE", f"{word}%")
    rows = conn.execute(
        f'SELECT {", ".join(select)} FROM "{table}" '
        f'WHERE lower(trim("{wcol}")) {op} lower(?) LIMIT 25', (value,),
    ).fetchall()
    return [{"kata": r[0], "arti": r[1], "jenis": r[2]} for r in rows]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", help="jalur SQLite KBBI (default dari .skripsi.yaml)")
    ap.add_argument("--word", help="satu kata yang dicari")
    ap.add_argument("--check", help="daftar kata dipisah koma; laporkan yang tidak ditemukan")
    ap.add_argument("--prefix", action="store_true", help="cocokkan awalan, bukan persis")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.word and not args.check:
        ap.error("butuh --word atau --check")

    cfg = load_config()
    db_path = Path(args.db).expanduser() if args.db else cfg.resolved_kbbi_path()
    if db_path is None:
        print(
            "KBBI belum dikonfigurasi, jadi kebakuan kata TIDAK BISA diverifikasi.\n"
            "Jangan menyimpulkan baku/tidak-baku dari ingatan — periksa manual di "
            "https://kbbi.kemdikbud.go.id dan tandai sebagai belum terverifikasi.\n"
            "Untuk mengaktifkan: /plugin configure uii-skripsi-research "
            "(isi kbbi_db_path), atau berikan --db.",
            file=sys.stderr)
        return 2
    if not db_path.is_file():
        print(f"Basis data KBBI tidak ditemukan: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    schema = discover_schema(conn)

    if args.word:
        hits = lookup(conn, schema, args.word, exact=not args.prefix)
        if args.json:
            print(json.dumps(hits, indent=2, ensure_ascii=False))
        elif not hits:
            print(f"'{args.word}' tidak ditemukan di KBBI. "
                  "Periksa ejaannya, atau ini istilah serapan yang belum baku.")
        else:
            for h in hits:
                jenis = f" [{h['jenis']}]" if h["jenis"] else ""
                print(f"{h['kata']}{jenis}: {h['arti']}")
        return 0 if hits else 1

    words = [w.strip() for w in args.check.split(",") if w.strip()]
    hasil = []
    for w in words:
        status, baku = classify(lookup(conn, schema, w))
        hasil.append({"kata": w, "status": status, "bentuk_baku": baku})

    bermasalah = [h for h in hasil if h["status"] != "baku"]
    if args.json:
        print(json.dumps({"hasil": hasil}, indent=2, ensure_ascii=False))
    else:
        print(f"Diperiksa {len(words)} kata; {len(bermasalah)} bermasalah.")
        for h in hasil:
            if h["status"] == "tidak_baku":
                print(f"  TIDAK BAKU  {h['kata']} -> pakai: {h['bentuk_baku']}")
            elif h["status"] == "tidak_ada":
                print(f"  TIDAK ADA   {h['kata']} (bukan lema KBBI; "
                      "bisa jadi salah eja atau istilah asing)")
        if not bermasalah:
            print("  Semua baku.")
    return 1 if bermasalah else 0


if __name__ == "__main__":
    sys.exit(main())
