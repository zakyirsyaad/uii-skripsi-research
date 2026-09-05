#!/usr/bin/env python3
"""Analisis bentuk skripsi UII dari PDF, untuk dijadikan rujukan kerangka.

    analisis_dspace.py ~/Downloads/22523174.pdf
    analisis_dspace.py ~/Downloads/skripsi-uii/          # seluruh PDF di folder
    analisis_dspace.py *.pdf --json

Melaporkan BENTUK, bukan isi: kerangka bab, proporsi halaman, struktur subbab,
statistik panjang kalimat, metode yang disebut, dan ukuran daftar pustaka.

Skrip ini sengaja TIDAK pernah mencetak kalimat dari sumbernya. Kemiripan
kerangka wajar dan memang tujuannya; kemiripan kalimat adalah plagiarisme.

Cara memperoleh PDF-nya: DSpace UII berada di balik proteksi bot Cloudflare,
jadi unduh sendiri lewat peramban biasa — buka tautannya, simpan PDF-nya, lalu
tunjuk foldernya ke skrip ini.

Butuh pypdf. Ini satu-satunya bagian plugin yang memakai pustaka pihak ketiga,
dan sifatnya opsional: seluruh perkakas inti tetap berjalan tanpanya.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

BAB = re.compile(r"(?m)^\s*BAB\s+([IVX]+)\s*$")
SUB = re.compile(r"(?m)^\s*(\d\.\d(?:\.\d)?)\s+([A-Z][^\n]{2,64}?)\s*$")
TAHUN = re.compile(r"\(\d{4}\)")
DOI = re.compile(r"10\.\d{4,9}/")

METODE = [
    "prototyping", "waterfall", "agile", "scrum", "design science", "DSRM",
    "RAD", "extreme programming", "SDLC", "incremental", "spiral",
    "user centered", "UCD", "kanban", "lean",
]


def butuh_pypdf():
    try:
        from pypdf import PdfReader
        return PdfReader
    except ImportError:
        print(
            "Butuh pypdf, dan itu belum terpasang.\n\n"
            "Cara paling gampang, tanpa memasang apa pun secara permanen:\n"
            f"    uv run --with pypdf {Path(__file__).name} <berkas.pdf>\n\n"
            "Atau pasang sekali: pip install pypdf",
            file=sys.stderr)
        raise SystemExit(2)


def baca(path: Path, PdfReader) -> list[str]:
    return [(p.extract_text() or "") for p in PdfReader(str(path)).pages]


def bersihkan(text: str) -> str:
    """Buang nomor subbab dan baris pendek (header, footer, nomor halaman)."""
    text = re.sub(r"\b\d+\.\d+(\.\d+)?\b", " ", text)
    text = re.sub(r"(?m)^.{0,3}$", " ", text)
    return re.sub(r"\s+", " ", text)


def hitung_kata(text: str) -> int:
    """Kata yang mengandung huruf — nomor halaman dan penanda tidak ikut."""
    return sum(1 for w in re.sub(r"\s+", " ", text).split() if any(c.isalpha() for c in w))


def peta_bab(pages: list[str]) -> list[dict]:
    """Halaman mulai tiap BAB. Kemunculan pertama menang — sisanya daftar isi."""
    ketemu, urut = {}, []
    for i, t in enumerate(pages):
        m = BAB.search(t)
        if not m:
            continue
        nomor = m.group(1)
        if nomor in ketemu:
            continue
        sisa = [l.strip() for l in t[m.end():].strip().splitlines() if l.strip()]
        ketemu[nomor] = True
        urut.append({"bab": nomor, "mulai": i + 1, "judul": (sisa[0] if sisa else "")[:48]})

    for i, b in enumerate(urut):
        b["akhir"] = urut[i + 1]["mulai"] - 1 if i + 1 < len(urut) else len(pages)
        b["halaman"] = b["akhir"] - b["mulai"] + 1
        b["kata"] = hitung_kata("\n".join(pages[b["mulai"] - 1:b["akhir"]]))
        b["kata_per_halaman"] = b["kata"] // max(b["halaman"], 1)
    total = sum(b["halaman"] for b in urut) or 1
    for b in urut:
        b["persen"] = round(b["halaman"] / total * 100)
    return urut


def subbab(pages: list[str], hanya: set[int] | None = None) -> dict[str, str]:
    hasil: dict[str, str] = {}
    for m in SUB.finditer("\n".join(pages)):
        nomor, judul = m.group(1), " ".join(m.group(2).split())
        if judul.isupper() or len(judul) < 4 or nomor in hasil:
            continue
        if hanya and int(nomor.split(".")[0]) not in hanya:
            continue
        hasil[nomor] = judul
    return hasil


def statistik_bahasa(pages: list[str], mulai: int) -> dict:
    teks = bersihkan("\n".join(pages[mulai - 1:]))
    kal = [s for s in re.split(r"\.\s+", teks) if 4 <= len(s.split()) <= 120]
    if not kal:
        return {}
    p = [len(s.split()) for s in kal]
    return {
        "kalimat": len(kal),
        "rata_rata": round(statistics.mean(p), 1),
        "median": int(statistics.median(p)),
        "persen_lebih_25": round(sum(1 for x in p if x > 25) / len(p) * 100),
        "persen_lebih_35": round(sum(1 for x in p if x > 35) / len(p) * 100),
    }


def analisis(path: Path, PdfReader) -> dict:
    pages = baca(path, PdfReader)
    penuh = " ".join(pages)
    bab = peta_bab(pages)
    mulai_isi = bab[0]["mulai"] if bab else 1

    i = penuh.upper().rfind("DAFTAR PUSTAKA")
    pustaka = penuh[i:i + 12000] if i > 0 else ""

    metode = {m: len(re.findall(m, penuh, re.I)) for m in METODE}
    return {
        "berkas": path.name,
        "halaman": len(pages),
        "judul": " ".join(pages[0].split())[:90] if pages else "",
        "bab": bab,
        "subbab": subbab(pages, hanya={1, 3}),
        "bahasa": statistik_bahasa(pages, mulai_isi),
        "metode": {k: v for k, v in sorted(metode.items(), key=lambda x: -x[1]) if v},
        "pustaka": {"entri": len(TAHUN.findall(pustaka)), "doi": len(DOI.findall(pustaka))},
    }


def cetak(a: dict) -> None:
    print(f"\n{'=' * 68}\n{a['berkas']}  ({a['halaman']} halaman)\n{'=' * 68}")
    print(f"  {a['judul']}\n")

    if a["bab"]:
        print("  Kerangka bab")
        for b in a["bab"]:
            bar = "#" * max(1, round(b["persen"] / 3))
            print(f"    BAB {b['bab']:<4} hal {b['mulai']:>3}-{b['akhir']:<3} "
                  f"{b['halaman']:>3} hal  {b['kata']:>6,} kata  "
                  f"{b['kata_per_halaman']:>3}/hal  {b['persen']:>3}%  {bar}")
            print(f"    {'':>13}{b['judul']}")
        print(f"    {'TOTAL':<8} {'':>13}{sum(b['halaman'] for b in a['bab']):>3} hal  "
              f"{sum(b['kata'] for b in a['bab']):>6,} kata isi")
    else:
        print("  Kerangka bab tidak terdeteksi — mungkin PDF hasil pindaian "
              "tanpa lapisan teks.")

    if a["subbab"]:
        print("\n  Subbab BAB I dan BAB III")
        for n in sorted(a["subbab"], key=lambda s: [int(x) for x in s.split(".")]):
            print(f"    {'  ' * (n.count('.') - 1)}{n} {a['subbab'][n][:56]}")

    b = a["bahasa"]
    if b:
        print(f"\n  Bahasa: {b['kalimat']} kalimat | rata-rata {b['rata_rata']} kata | "
              f"median {b['median']} | >25 kata {b['persen_lebih_25']}% | "
              f">35 kata {b['persen_lebih_35']}%")

    if a["metode"]:
        print("  Metode disebut: " + ", ".join(
            f"{k} ({v}x)" for k, v in list(a["metode"].items())[:5]))
    p = a["pustaka"]
    print(f"  Daftar pustaka: ~{p['entri']} entri, {p['doi']} DOI")


def ringkasan(semua: list[dict]) -> None:
    print(f"\n{'=' * 68}\nRINGKASAN {len(semua)} SKRIPSI\n{'=' * 68}")
    per_bab: dict[str, list[int]] = {}
    for a in semua:
        for b in a["bab"]:
            per_bab.setdefault(b["bab"], []).append(b["persen"])
    if per_bab:
        print("  Proporsi halaman per bab (persen isi)")
        for n in ("I", "II", "III", "IV", "V"):
            if n in per_bab:
                v = per_bab[n]
                print(f"    BAB {n:<4} {min(v):>3}-{max(v):<3}%   median {int(statistics.median(v))}%")

    per_kata: dict[str, list[int]] = {}
    total_isi = []
    for a in semua:
        for b in a["bab"]:
            per_kata.setdefault(b["bab"], []).append(b["kata"])
        if a["bab"]:
            total_isi.append(sum(b["kata"] for b in a["bab"]))
    if per_kata:
        print("\n  Kata per bab")
        for n in ("I", "II", "III", "IV", "V"):
            if n in per_kata:
                v = sorted(per_kata[n])
                print(f"    BAB {n:<4} {min(v):>6,} - {max(v):<6,}  median {int(statistics.median(v)):,}")
    if total_isi:
        print(f"    {'TOTAL':<8} {min(total_isi):>6,} - {max(total_isi):<6,}  "
              f"median {int(statistics.median(total_isi)):,} kata isi")
        print("\n  Jumlah kata lebih andal daripada jumlah halaman: halaman berubah")
        print("  kalau font, spasi, atau ukuran gambar diubah.")

    rr = [a["bahasa"]["rata_rata"] for a in semua if a["bahasa"]]
    if rr:
        print(f"\n  Panjang kalimat rata-rata: {min(rr)}-{max(rr)} kata")
        print("  Pakai ini sebagai patokan ragam yang diterima, bukan target kaku.")

    print("\n  Ini rujukan BENTUK. Jangan menyalin prosa, abstrak, tabel, atau")
    print("  daftar pustakanya, dan jangan memasukkan skripsi DSpace ke daftar")
    print("  pustakamu. Metode yang dipakai orang lain juga bukan bukti bahwa")
    print("  metode itu cocok untuk penelitianmu.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="+", help="berkas PDF atau folder berisi PDF")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    berkas: list[Path] = []
    for t in args.target:
        p = Path(t).expanduser()
        if p.is_dir():
            berkas += sorted(p.glob("*.pdf"))
        elif p.is_file():
            berkas.append(p)
        else:
            print(f"Dilewati, tidak ditemukan: {p}", file=sys.stderr)
    if not berkas:
        print("Tidak ada PDF untuk dianalisis.", file=sys.stderr)
        return 1

    PdfReader = butuh_pypdf()
    semua = []
    for f in berkas:
        try:
            semua.append(analisis(f, PdfReader))
        except Exception as exc:
            print(f"Gagal membaca {f.name}: {exc}", file=sys.stderr)

    if not semua:
        return 1
    if args.json:
        print(json.dumps(semua, indent=2, ensure_ascii=False))
        return 0
    for a in semua:
        cetak(a)
    if len(semua) > 1:
        ringkasan(semua)
    return 0


if __name__ == "__main__":
    sys.exit(main())
