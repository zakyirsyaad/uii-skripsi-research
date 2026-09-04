#!/usr/bin/env python3
"""Ekspor source ledger ke BibTeX/RIS untuk diimpor Mendeley.

Hanya entri `verified` yang diekspor. Entri yang belum diverifikasi sengaja
ditahan: begitu sitasi masuk reference manager, ia cenderung dianggap sahih.

    export_mendeley.py --format bibtex > pustaka.bib
    export_mendeley.py --format ris --include-unverified > pustaka.ris
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skripsi.config import load_config  # noqa: E402
from skripsi.ledger import Source, load_sources  # noqa: E402

DEFAULT_LEDGER = "references/sources.md"

BIBTEX_TYPE = {
    "jurnal": "article", "prosiding": "inproceedings", "buku": "book",
    "standar": "techreport", "institusi": "techreport", "artikel": "misc",
}
RIS_TYPE = {
    "jurnal": "JOUR", "prosiding": "CPAPER", "buku": "BOOK",
    "standar": "STD", "institusi": "RPRT", "artikel": "ELEC",
}
BIBTEX_VENUE_FIELD = {
    "jurnal": "journal", "prosiding": "booktitle", "buku": "publisher",
    "standar": "institution", "institusi": "institution", "artikel": "howpublished",
}

# Penulis korporat harus tetap utuh. BibTeX memecah nama pada " and " dan
# membalik "Keluarga, Depan"; kurung ganda mematikan kedua perilaku itu.
_PERSONAL_NAME = re.compile(r"^[A-Z][\w'’-]+$")


def is_corporate(name: str) -> bool:
    return not _PERSONAL_NAME.match(name.strip())


def bibtex_author(name: str) -> str:
    # Satu lapis kurung saja: formatter field di bawah sudah menambah lapis luar,
    # sehingga hasil akhirnya `author = {{Nama Organisasi}}`.
    return "{" + name.strip() + "}" if is_corporate(name) else name.strip()


def cite_key(s: Source) -> str:
    base = re.sub(r"[^A-Za-z0-9]", "", s.penulis.split()[0] if s.penulis else s.id)
    return f"{base or s.id}{s.tahun or ''}"


def to_bibtex(s: Source) -> str:
    fields = [("title", s.judul), ("author", bibtex_author(s.penulis))]
    if s.tahun:
        fields.append(("year", str(s.tahun)))
    if s.venue:
        fields.append((BIBTEX_VENUE_FIELD.get(s.tipe, "publisher"), s.venue))
    if s.doi:
        fields.append(("doi", s.doi))
    elif s.doi_url:
        fields.append(("url", s.doi_url))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
    return f"@{BIBTEX_TYPE.get(s.tipe, 'misc')}{{{cite_key(s)},\n{body}\n}}"


def to_ris(s: Source) -> str:
    lines = [f"TY  - {RIS_TYPE.get(s.tipe, 'GEN')}", f"TI  - {s.judul}"]
    if s.penulis:
        # RIS tidak punya penanda korporat; nama organisasi ditulis apa adanya
        # tanpa koma agar Mendeley tidak menebaknya sebagai "Keluarga, Depan".
        lines.append(f"AU  - {s.penulis.replace(',', '')}")
    if s.tahun:
        lines.append(f"PY  - {s.tahun}")
    if s.venue:
        lines.append(f"{'JO' if s.tipe == 'jurnal' else 'T2'}  - {s.venue}")
    if s.doi:
        lines.append(f"DO  - {s.doi}")
    if s.doi_url:
        lines.append(f"UR  - {s.doi_url}")
    lines.append("ER  - ")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--format", choices=["bibtex", "ris"], default="bibtex")
    ap.add_argument("--include-unverified", action="store_true",
                    help="ikutkan entri yang belum diverifikasi (tidak disarankan)")
    args = ap.parse_args()

    cfg = load_config()
    path = Path(args.ledger) if args.ledger else cfg.root / DEFAULT_LEDGER
    sources, _ = load_sources(path)

    if args.include_unverified:
        selected, held = sources, []
    else:
        selected = [s for s in sources if s.is_verified]
        held = [s for s in sources if not s.is_verified]

    render = to_bibtex if args.format == "bibtex" else to_ris
    print("\n\n".join(render(s) for s in selected))

    if held:
        print(f"\n{len(held)} entri ditahan karena belum `verified`: "
              f"{', '.join(s.id for s in held)}\n"
              "Jalankan verify_citation.py --ledger ... --write lebih dulu.",
              file=sys.stderr)
    if not selected:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
