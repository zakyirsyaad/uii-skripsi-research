#!/usr/bin/env python3
"""Unduh dan siapkan basis data KBBI Edisi IV untuk validasi bahasa.

    setup_kbbi.py              # unduh ke lokasi bawaan, minta konfirmasi
    setup_kbbi.py --yes        # tanpa konfirmasi
    setup_kbbi.py --dest ~/kbbi.sqlite --force

HAK CIPTA — baca sebelum memakai. Data kamus ini dimiliki sepenuhnya oleh Badan
Pengembangan dan Pembinaan Bahasa (Kemendikbud). Sumber yang diunduh menyatakan
penggunaan komersial dilarang dan tunduk pada UU No. 28 Tahun 2014 tentang Hak
Cipta. Skrip ini TIDAK mendistribusikan ulang data itu; ia mengunduhkannya atas
namamu, untuk keperluan penulisan skripsimu sendiri. Kamu yang bertanggung jawab
atas pemakaiannya.

Hanya `edisi-IV` yang diambil — itu turunan KBBI Edisi IV yang sahih. Berkas
`baku-nonbaku`, `sinonim`, dan `antonim` di repositori yang sama sebagian
DIHASILKAN AI dan sengaja TIDAK diunduh, karena memperlakukannya sebagai standar
KBBI justru memberi rasa aman palsu.
"""
from __future__ import annotations

import argparse
import html
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

DUMP_URL = ("https://raw.githubusercontent.com/dyazincahya/KBBI-SQL-database/"
            "main/edisi-IV/dictionary__SQLite.sql")
DEFAULT_DEST = Path.home() / ".skripsi" / "kbbi-edisi-iv.sqlite"
EXPECTED_MIN_ROWS = 100_000          # repositori menyebut ~115.978 lema
_TAG = re.compile(r"<[^>]+>")

NOTICE = """\
Akan mengunduh basis data KBBI Edisi IV (~26 MB) dari:
  {url}

HAK CIPTA. Isi kamus ini milik Badan Pengembangan dan Pembinaan Bahasa
(Kemendikbud). Sumbernya melarang penggunaan komersial, mengacu pada UU No. 28
Tahun 2014. Unduhan ini untuk menulis skripsimu sendiri, dan kamu yang
bertanggung jawab atas pemakaiannya.

Yang diunduh hanya kamus utamanya. Tabel baku/tidak-baku, sinonim, dan antonim
di sumber yang sama sebagian dibuat AI, jadi tidak dipakai.

Disimpan ke: {dest}
"""


def download(url: str, timeout: int = 120) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "uii-skripsi-research/1.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = int(resp.headers.get("Content-Length") or 0)
        chunks, seen = [], 0
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
            seen += len(chunk)
            if total:
                print(f"\r  mengunduh… {seen / 1048576:.1f}/{total / 1048576:.1f} MB",
                      end="", file=sys.stderr)
        print(file=sys.stderr)
    return b"".join(chunks).decode("utf-8")


def clean(text: str) -> str:
    """Buang markup dan entitas HTML dari definisi agar terbaca di terminal."""
    return re.sub(r"\s+", " ", _TAG.sub("", html.unescape(text or ""))).strip()


def build(dump: str, dest: Path) -> int:
    """Bangun SQLite yang dinormalkan. Kembalikan jumlah lema."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    tmp.unlink(missing_ok=True)

    conn = sqlite3.connect(tmp)
    try:
        # Dump-nya INSERT saja, tanpa CREATE TABLE — skemanya kita yang buat.
        conn.execute('CREATE TABLE dictionary (word TEXT, arti TEXT, "type" INTEGER)')
        conn.executescript(dump)

        # Lema di dump punya spasi di belakang ('a ', 'ab '), sehingga pencarian
        # persis tidak akan pernah cocok. Definisinya pun masih ber-entitas HTML.
        rows = conn.execute("SELECT rowid, word, arti FROM dictionary").fetchall()
        conn.executemany(
            "UPDATE dictionary SET word = ?, arti = ? WHERE rowid = ?",
            [(w.strip() if w else "", clean(a), rid) for rid, w, a in rows],
        )
        conn.execute("DELETE FROM dictionary WHERE word = ''")
        conn.execute("CREATE INDEX idx_word ON dictionary (word COLLATE NOCASE)")
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
    finally:
        conn.close()

    if count < EXPECTED_MIN_ROWS:
        tmp.unlink(missing_ok=True)
        raise SystemExit(
            f"Hanya {count:,} lema terbaca, seharusnya minimal "
            f"{EXPECTED_MIN_ROWS:,}. Unduhan kemungkinan rusak; ulangi.")

    tmp.replace(dest)
    return count


def verify(dest: Path) -> bool:
    """Pastikan basis datanya benar-benar bisa dipakai mencari kata."""
    conn = sqlite3.connect(f"file:{dest}?mode=ro", uri=True)
    try:
        probes = ["analisis", "sistem", "praktik", "metode"]
        missing = [w for w in probes if not conn.execute(
            "SELECT 1 FROM dictionary WHERE word = ? COLLATE NOCASE LIMIT 1",
            (w,)).fetchone()]
    finally:
        conn.close()
    if missing:
        print(f"  PERINGATAN: kata umum tidak ditemukan: {', '.join(missing)}",
              file=sys.stderr)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    ap.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    ap.add_argument("--yes", action="store_true", help="lewati konfirmasi")
    args = ap.parse_args()

    dest = args.dest.expanduser()
    if dest.exists() and not args.force:
        print(f"Sudah ada: {dest}\nPakai --force untuk mengunduh ulang.")
        print(f"\nAktifkan dengan:\n  /plugin configure uii-skripsi-research\n"
              f"  kbbi_db_path = {dest}")
        return 0

    print(NOTICE.format(url=DUMP_URL, dest=dest))
    if not args.yes:
        try:
            if input("Lanjutkan? [y/N] ").strip().lower() not in ("y", "ya", "yes"):
                print("Dibatalkan.")
                return 1
        except EOFError:
            print("Tidak ada masukan interaktif; pakai --yes bila memang disengaja.",
                  file=sys.stderr)
            return 1

    try:
        dump = download(DUMP_URL)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"Unduhan gagal: {exc}", file=sys.stderr)
        return 2

    print("  menyiapkan basis data…", file=sys.stderr)
    try:
        count = build(dump, dest)
    except sqlite3.Error as exc:
        print(f"Gagal membangun basis data: {exc}", file=sys.stderr)
        return 2

    ok = verify(dest)
    print(f"\nSelesai: {count:,} lema di {dest}")
    if not ok:
        print("Basis data terbangun tapi pemeriksaan isi meragukan — "
              "periksa manual sebelum diandalkan.", file=sys.stderr)

    print(f"\nAktifkan dengan:\n  /plugin configure uii-skripsi-research\n"
          f"  kbbi_db_path = {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
