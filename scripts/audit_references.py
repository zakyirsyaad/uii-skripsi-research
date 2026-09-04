#!/usr/bin/env python3
"""Audit daftar pustaka terhadap kuota, kebaruan, dan kelengkapan metadata.

    audit_references.py                                  # pakai references/sources.md
    audit_references.py --ledger jalur/lain.md --json

Exit code: 0 bila tidak ada blocker, 1 bila ada.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skripsi.audit import audit_sources  # noqa: E402
from skripsi.config import load_config  # noqa: E402
from skripsi.ledger import errors, load_sources, warnings as ledger_warnings  # noqa: E402

DEFAULT_LEDGER = "references/sources.md"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    path = Path(args.ledger) if args.ledger else cfg.root / DEFAULT_LEDGER

    sources, issues = load_sources(path)
    parse_errors = errors(issues)

    rep = audit_sources(sources, cfg)

    if args.json:
        print(json.dumps({
            "verdict": rep.verdict,
            "total": rep.total, "akademik": rep.academic, "artikel": rep.articles,
            "kuota_artikel": rep.article_cap, "terverifikasi": rep.verified,
            "error_format": [str(i) for i in parse_errors],
            "temuan": [{"level": f.level, "code": f.code,
                        "pesan": f.message, "baris": f.lines} for f in rep.findings],
        }, indent=2, ensure_ascii=False))
        return 1 if (rep.blockers or parse_errors) else 0

    print(f"Source ledger: {path}")
    print(f"  total {rep.total} — akademik {rep.academic}, non-akademik {rep.articles} "
          f"(kuota {rep.article_cap}), terverifikasi {rep.verified}/{rep.total}\n")

    if parse_errors:
        print("Format ledger bermasalah:")
        for i in parse_errors:
            print(f"  {i}")
        print()

    for f in rep.blockers:
        print(f"  {f}")
    for f in rep.warnings:
        print(f"  {f}")
    if not rep.findings and not parse_errors:
        print("  Tidak ada temuan.")

    verdict = "not_ready" if parse_errors else rep.verdict
    print(f"\nVonis: {verdict}")
    if verdict == "not_ready":
        print("Perbaiki seluruh blocker sebelum daftar pustaka ini dipakai.")
    return 1 if (rep.blockers or parse_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
