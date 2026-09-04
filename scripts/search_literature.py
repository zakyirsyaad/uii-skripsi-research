#!/usr/bin/env python3
"""Cari literatur akademik lewat OpenAlex, dengan filter yang bisa dipertanggungjawabkan.

    search_literature.py "blockchain crowdfunding UMKM" --since 2020 --oa
    search_literature.py "usability evaluation e-government" --min-citations 10 --limit 15
    search_literature.py "design science research" --type article --json

Keluarannya KANDIDAT, bukan sitasi. Sebuah kandidat baru boleh disitasi setelah
teks lengkapnya dibaca dan terbukti mendukung klaim yang dimaksud.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skripsi.config import load_config  # noqa: E402
from skripsi.sources import MetadataClient, NetworkUnavailable  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--since", type=int, help="tahun terbit paling awal")
    ap.add_argument("--until", type=int, help="tahun terbit paling akhir")
    ap.add_argument("--oa", action="store_true", help="hanya yang open access")
    ap.add_argument("--min-citations", type=int, default=0)
    ap.add_argument("--type", default="", help="mis. article, book-chapter, preprint")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    if args.since is None and cfg.recency_years:
        print(f"catatan: tanpa --since, hasil tidak dibatasi kebaruan "
              f"(.skripsi.yaml menyarankan {cfg.recency_years} tahun terakhir).",
              file=sys.stderr)

    client = MetadataClient(cfg.mailto, cfg.resolved_cache_dir())
    try:
        works = client.search_openalex(
            args.query, since=args.since, until=args.until, oa_only=args.oa,
            min_citations=args.min_citations, work_type=args.type, limit=args.limit,
        )
    except NetworkUnavailable as exc:
        print(f"Pencarian gagal, jaringan tidak bisa dihubungi: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps([w.to_dict() for w in works], indent=2, ensure_ascii=False))
    else:
        if not works:
            print("Tidak ada kandidat. Longgarkan filter atau ubah kata kuncinya.")
        for i, w in enumerate(works, 1):
            print(f"{i:2d}. {w.title}")
            print(f"    {'; '.join(w.authors[:4]) or '(tanpa penulis)'}"
                  f"{' dkk.' if len(w.authors) > 4 else ''} "
                  f"({w.year or '?'}) — {w.venue or '?'}")
            bits = [f"disitasi {w.cited_by}×"]
            if w.doi:
                bits.append(f"doi:{w.doi}")
            if w.open_access_url:
                bits.append("OA tersedia")
            if w.is_retracted:
                bits.append("!! DITARIK")
            print(f"    {' | '.join(bits)}")
        print(f"\n{len(works)} kandidat. Ini BELUM sitasi — baca teks lengkapnya "
              "dan pastikan benar mendukung klaimmu sebelum masuk daftar pustaka.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
