#!/usr/bin/env python3
"""Verifikasi sitasi terhadap Crossref/OpenAlex/DataCite.

    # satu sitasi lewat DOI
    verify_citation.py --doi 10.1145/3313831.3376234

    # satu sitasi lewat judul
    verify_citation.py --title "Judul" --author "Nakamoto" --year 2008

    # seluruh source ledger, lalu tulis balik statusnya
    verify_citation.py --ledger references/sources.md --write

Exit code: 0=OK 1=MISMATCH 2=NOT_FOUND 3=UNVERIFIED 4=RETRACTED 5=UNVERIFIABLE.
Untuk mode --ledger, exit code diambil dari kasus terparah.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skripsi.config import load_config  # noqa: E402
from skripsi.ledger import errors, load_sources, today, update_source_rows  # noqa: E402
from skripsi.sources import MetadataClient  # noqa: E402
from skripsi.verify import (  # noqa: E402
    EXIT_CODES, STATUS_MISMATCH, STATUS_NOT_FOUND, STATUS_OK, STATUS_RETRACTED,
    STATUS_UNVERIFIABLE, STATUS_UNVERIFIED, Claim, Result, verify,
)

SEVERITY_ORDER = [STATUS_OK, STATUS_UNVERIFIABLE, STATUS_UNVERIFIED,
                  STATUS_MISMATCH, STATUS_RETRACTED, STATUS_NOT_FOUND]

ICON = {STATUS_OK: "OK      ", STATUS_MISMATCH: "MISMATCH", STATUS_NOT_FOUND: "HILANG  ",
        STATUS_RETRACTED: "DITARIK ", STATUS_UNVERIFIED: "?       ",
        STATUS_UNVERIFIABLE: "MANUAL  "}


def render(result: Result, verbose: bool = True) -> str:
    lines = [f"[{ICON[result.status]}] {result.claim.id or result.claim.doi or result.claim.title}"]
    if result.work:
        w = result.work
        lines.append(f"           kanonik: {w.title}")
        lines.append(f"                    {'; '.join(w.authors) or '(tanpa penulis)'} "
                     f"({w.year or '?'}) — {w.venue or w.publisher or '?'}")
        if w.doi:
            lines.append(f"                    https://doi.org/{w.doi}")
    for d in result.diffs:
        if not d.ok:
            mark = "!" if d.severity == "error" else "~"
            lines.append(f"           {mark} {d.field}: ditulis {d.ditulis!r} "
                         f"vs kanonik {d.kanonik!r}" + (f" ({d.note})" if d.note else ""))
    if verbose:
        for n in result.notes:
            lines.append(f"           · {n}")
    return "\n".join(lines)


def worst(statuses: list[str]) -> str:
    if not statuses:
        return STATUS_OK
    return max(statuses, key=SEVERITY_ORDER.index)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doi")
    ap.add_argument("--title")
    ap.add_argument("--author", default="")
    ap.add_argument("--year", type=int)
    ap.add_argument("--tipe", default="",
                    help="jenis sumber; halaman institusi/artikel tidak diindeks "
                         "Crossref sehingga ketidakhadirannya tidak bermakna")
    ap.add_argument("--ledger", help="verifikasi seluruh entri source ledger")
    ap.add_argument("--write", action="store_true",
                    help="tulis balik status ke ledger (butuh --ledger)")
    ap.add_argument("--only-unverified", action="store_true",
                    help="lewati entri yang sudah verified")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.write and not args.ledger:
        ap.error("--write hanya berlaku bersama --ledger")
    if not args.ledger and not (args.doi or args.title):
        ap.error("butuh --doi, --title, atau --ledger")

    cfg = load_config()
    if not cfg.has_mailto:
        print("catatan: `mailto` belum diisi di .skripsi.yaml — API akan memakai "
              "rate limit paling ketat dan bisa lambat.", file=sys.stderr)
    client = MetadataClient(cfg.mailto, cfg.resolved_cache_dir())

    # -- satu sitasi ------------------------------------------------------
    if not args.ledger:
        result = verify(Claim(doi=args.doi or "", title=args.title or "",
                              author=args.author, year=args.year,
                              tipe=args.tipe), client)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
              if args.json else render(result))
        return result.exit_code

    # -- seluruh ledger ---------------------------------------------------
    path = Path(args.ledger)
    sources, issues = load_sources(path)
    for issue in errors(issues):
        print(f"ledger: {issue}", file=sys.stderr)
    if not sources:
        print("Tidak ada entri yang bisa diverifikasi.", file=sys.stderr)
        return EXIT_CODES[STATUS_UNVERIFIED]

    results: list[Result] = []
    updates: dict[str, tuple[str, str]] = {}
    stamp = today()

    for src in sources:
        if args.only_unverified and src.is_verified:
            continue
        claim = Claim(id=src.id, doi=src.doi, title=src.judul,
                      author=src.penulis, year=src.tahun,
                      tipe=src.tipe, url=src.doi_url)
        result = verify(claim, client)
        results.append(result)
        if not args.json:
            print(render(result, verbose=False))
        # Status UNVERIFIED tidak ditulis balik: kegagalan jaringan bukan temuan.
        if result.status != STATUS_UNVERIFIED:
            updates[src.id] = (result.ledger_status, stamp)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))

    if args.write and updates:
        path.write_text(update_source_rows(path.read_text(encoding="utf-8"), updates),
                        encoding="utf-8")
        print(f"\n{len(updates)} entri diperbarui di {path}", file=sys.stderr)

    tally: dict[str, int] = {}
    for r in results:
        tally[r.status] = tally.get(r.status, 0) + 1
    print("\nRingkasan: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())),
          file=sys.stderr)
    if tally.get(STATUS_UNVERIFIABLE):
        print(f"{tally[STATUS_UNVERIFIABLE]} sumber di luar jangkauan basis data "
              "sitasi ilmiah — periksa manual, jangan anggap fiktif.", file=sys.stderr)
    if tally.get(STATUS_NOT_FOUND):
        print(f"PERINGATAN: {tally[STATUS_NOT_FOUND]} sitasi tidak ditemukan di "
              "sumber mana pun — perlakukan sebagai dugaan sitasi fiktif.", file=sys.stderr)

    return EXIT_CODES[worst([r.status for r in results])]


if __name__ == "__main__":
    sys.exit(main())
