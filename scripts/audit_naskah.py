#!/usr/bin/env python3
"""Audit naskah skripsi Word terhadap template resmi Informatika UII.

    audit_naskah.py naskah.docx
    audit_naskah.py naskah.docx --json

Memeriksa sisa teks template, daftar isi basi, kelengkapan halaman awal, gaya
sitasi, jumlah kata, dan panjang kalimat.

HANYA MEMBACA. Perbaikannya kamu kerjakan sendiri di Word — menimpa berkas Word
bisa menghapus komentar pembimbing dan field Mendeley, dan hook plugin ini
memang memblokirnya.

Template resmi diunduh sekali lalu disimpan di cache.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skripsi.docx import daftar_isi, is_docx, judul, teks  # noqa: E402

TEMPLATE_URL = ("https://informatics.uii.ac.id/wp-content/uploads/2020/12/"
                "Template-skripsi-final-versi2020.docx")
CACHE = Path.home() / ".skripsi" / "template-uii-2020.docx"

# Istilah UII, bukan istilah umum. Abstrak di sini bernama SARI — mencarinya
# sebagai "ABSTRAK" menghasilkan temuan palsu.
HALAMAN_AWAL = [
    "HALAMAN JUDUL", "HALAMAN PENGESAHAN DOSEN PEMBIMBING",
    "HALAMAN PENGESAHAN DOSEN PENGUJI", "HALAMAN PERNYATAAN KEASLIAN",
    "HALAMAN PERSEMBAHAN", "HALAMAN MOTO", "KATA PENGANTAR", "SARI",
    "GLOSARIUM", "DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR",
]

# Bagian yang teksnya memang resmi dan harus tetap apa adanya.
TETAP = ("PERNYATAAN KEASLIAN", "PENGESAHAN")

# Bagian yang setelah instruksinya dihapus akan KOSONG, sehingga butuh tulisan
# sendiri. Membiarkannya kosong sama buruknya dengan meninggalkan teks template.
BUTUH_ISI = ("SARI", "GLOSARIUM", "KATA PENGANTAR", "MOTO", "PERSEMBAHAN")

# Kalimat yang isinya instruksi kepada penulis, bukan calon isi skripsi.
INSTRUKSI = re.compile(
    r"klik kanan|jangan lupa|setelah proses|harus di-?update|bagian ini bebas|"
    r"adalah bagian (yang|laporan)|memuat daftar|idealnya bagian|tata letaknya",
    re.I)

BAGIAN = re.compile(r"^(HALAMAN [A-Z ]+|KATA PENGANTAR|SARI|GLOSARIUM|"
                    r"DAFTAR [A-Z]+|BAB\s*[IVX]+.*)$")
PLACEHOLDER = re.compile(r"TULISKAN JUDUL BAB|Nama Mahasiswa|xxx+", re.I)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def ambil_template(force: bool = False) -> Path | None:
    if CACHE.is_file() and not force:
        return CACHE
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        TEMPLATE_URL, headers={"User-Agent": "uii-skripsi-research/1.8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            CACHE.write_bytes(r.read())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"Tidak bisa mengunduh template resmi: {exc}\n"
              "Pemeriksaan sisa teks template dilewati.", file=sys.stderr)
        return None
    return CACHE


def kalimat(t: str, min_kata: int = 12, max_kata: int = 60) -> set[str]:
    return {norm(s) for s in re.split(r"(?<=[.!?])\s+", t)
            if min_kata <= len(norm(s).split()) <= max_kata}


def sisa_template(naskah_teks: str, template_teks: str) -> list[dict]:
    """Kalimat template yang masih tertinggal, beserta bagian dan tindakannya."""
    dari_template = kalimat(template_teks)
    bagian, hasil, terlihat = "(awal dokumen)", [], set()

    for baris in naskah_teks.splitlines():
        b = baris.strip()
        if BAGIAN.match(b):
            bagian = b[:40]
        for s in re.split(r"(?<=[.!?])\s+", b):
            n = norm(s)
            if n not in dari_template or n in terlihat:
                continue
            terlihat.add(n)
            if any(k in bagian.upper() for k in TETAP):
                aksi, alasan = "tetap", "teks resmi, memang harus ada"
            elif INSTRUKSI.search(n):
                aksi = "hapus"
                if any(k in bagian.upper() for k in BUTUH_ISI):
                    alasan = ("instruksi template — hapus, lalu tulis isi bagian ini "
                              "sendiri agar tidak kosong")
                else:
                    alasan = "instruksi template, bukan isi skripsi"
            else:
                aksi, alasan = "ganti", "placeholder — tulis isimu sendiri"
            hasil.append({"bagian": bagian, "teks": n, "aksi": aksi, "alasan": alasan})
    return hasil


def audit(path: Path, template_teks: str | None) -> dict:
    t = teks(path)
    penuh = " ".join(t.split())
    n_kata = len([w for w in t.split() if any(c.isalpha() for c in w)])

    ada = {h: bool(re.search(re.escape(h), penuh, re.I)) for h in HALAMAN_AWAL}

    toc = daftar_isi(path)
    toc_basi = [x for x in toc if PLACEHOLDER.search(x)]

    apa = len(re.findall(r"\([A-Z][A-Za-z'’-]+(?:,| &| et al\.)[^)]{0,40}\d{4}[a-c]?\)", penuh))
    apa_nar = len(re.findall(r"[A-Z][A-Za-z'’-]+(?: (?:&|dan) [A-Z][A-Za-z'’-]+)? \(\d{4}\)", penuh))
    ieee = len(re.findall(r"\[\d{1,2}\]", penuh))

    kal = [s for s in re.split(r"\.\s+", penuh) if 4 <= len(s.split()) <= 120]
    p = [len(s.split()) for s in kal]

    sisa = sisa_template(t, template_teks) if template_teks else []

    return {
        "berkas": path.name,
        "kata": n_kata,
        "halaman_awal": ada,
        "judul_bab": [x for _, x in judul(path) if re.match(r"BAB\s*[IVX]", x)],
        "daftar_isi_basi": toc_basi,
        "sitasi": {"apa": apa, "apa_naratif": apa_nar, "ieee": ieee},
        "kalimat": {
            "jumlah": len(kal),
            "rata_rata": round(statistics.mean(p), 1) if p else 0,
            "median": int(statistics.median(p)) if p else 0,
            "persen_lebih_25": round(sum(1 for x in p if x > 25) / len(p) * 100) if p else 0,
        },
        "sisa_template": sisa,
    }


def cetak(a: dict) -> None:
    print(f"\n{'=' * 68}\n{a['berkas']}  ({a['kata']:,} kata)\n{'=' * 68}")

    hilang = [h for h, v in a["halaman_awal"].items() if not v]
    print("\n  Halaman awal")
    print("    Lengkap." if not hilang else "    HILANG: " + ", ".join(hilang))

    if a["judul_bab"]:
        print("\n  Bab")
        for b in a["judul_bab"][:8]:
            print(f"    {b[:60]}")

    if a["daftar_isi_basi"]:
        print(f"\n  DAFTAR ISI BASI — {len(a['daftar_isi_basi'])} entri masih placeholder")
        print("    Di Word: klik kanan pada daftar isi, pilih Update Field.")

    s = a["sitasi"]
    gaya = "APA" if (s["apa"] + s["apa_naratif"]) > s["ieee"] else "IEEE"
    print(f"\n  Sitasi: {gaya}  (APA {s['apa']} + naratif {s['apa_naratif']}, IEEE {s['ieee']})")
    if gaya == "IEEE":
        print("    Template resmi UII menetapkan APA 6th, bukan IEEE.")

    k = a["kalimat"]
    print(f"  Kalimat: {k['jumlah']} | rata-rata {k['rata_rata']} kata "
          f"| median {k['median']} | >25 kata {k['persen_lebih_25']}%")
    if k["rata_rata"] and not 17 <= k["rata_rata"] <= 25:
        arah = "lebih pendek" if k["rata_rata"] < 17 else "lebih panjang"
        print(f"    Terasa {arah} daripada skripsi UII yang lolos sidang (19-23 kata).")

    sisa = a["sisa_template"]
    if sisa:
        perlu = [x for x in sisa if x["aksi"] != "tetap"]
        print(f"\n  SISA TEKS TEMPLATE — {len(perlu)} lokasi perlu disentuh "
              f"({len(sisa) - len(perlu)} lainnya memang harus tetap)\n")
        for x in sisa:
            tanda = {"hapus": "HAPUS", "ganti": "GANTI", "tetap": "tetap"}[x["aksi"]]
            print(f"    [{tanda}] {x['bagian']}")
            print(f"            cari: \"{x['teks'][:76]}…\"")
            print(f"            {x['alasan']}")
    else:
        print("\n  Tidak ada sisa teks template.")

    blocker = bool([x for x in sisa if x["aksi"] != "tetap"]) or hilang or a["daftar_isi_basi"]
    print(f"\n  Vonis: {'not_ready' if blocker else 'ready_with_notes'}")
    print("  Perbaiki sendiri di Word — skrip ini tidak menyunting naskahmu.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("naskah", help="berkas .docx naskah skripsi")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--refresh-template", action="store_true",
                    help="unduh ulang template resmi")
    args = ap.parse_args()

    path = Path(args.naskah).expanduser()
    if not is_docx(path):
        print(f"Bukan berkas .docx yang bisa dibaca: {path}", file=sys.stderr)
        return 2

    tpl = ambil_template(args.refresh_template)
    tpl_teks = teks(tpl) if tpl else None

    a = audit(path, tpl_teks)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        cetak(a)

    perlu = [x for x in a["sisa_template"] if x["aksi"] != "tetap"]
    blocker = perlu or [h for h, v in a["halaman_awal"].items() if not v] or a["daftar_isi_basi"]
    return 1 if blocker else 0


if __name__ == "__main__":
    sys.exit(main())
