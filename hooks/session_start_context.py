#!/usr/bin/env python3
"""Suntikkan ringkasan ledger konteks skripsi di awal sesi.

Menutup satu mode kegagalan secara deterministik: model lupa membaca
`references/thesis-context.md` sebelum melanjutkan pekerjaan. Hook dijalankan
harness, jadi tidak bisa "lupa".

Sengaja hanya RINGKASAN. Menuangkan seluruh ledger ke tiap sesi akan membuatnya
diabaikan, dan ledger yang diabaikan sama saja dengan tidak ada.

Hook tidak boleh pernah menggagalkan sesi: kegagalan apa pun berakhir senyap.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LEDGER = "references/thesis-context.md"
MAX_ITEMS = 5
MAX_DECISIONS = 5


def emit(text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": text,
    }}))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    root = Path(payload.get("cwd") or Path.cwd())
    ledger = root / LEDGER
    if not ledger.is_file():
        return 0  # bukan proyek skripsi: jangan bising

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    try:
        from skripsi.ledger import errors, load_context
    except ImportError:
        return 0

    ctx, issues = load_context(ledger)

    lines = [
        "Konteks skripsi ditemukan di `references/thesis-context.md` "
        "(ledger kontinuitas — bukan bukti ilmiah, tidak boleh disitasi).",
        "",
        f"- Proyek: {ctx.project_id or '(belum diisi)'}"
        + (f" — {ctx.active_workstream}" if ctx.active_workstream else ""),
        f"- Unit aktif: {ctx.active_unit or '(tidak ada)'}"
        + (f" [{ctx.active_unit_status}]" if ctx.active_unit_status else ""),
        f"- Checkpoint terakhir: {ctx.last_checkpoint_at or '(belum pernah)'}",
        f"- Sinkronisasi Word: {ctx.word_sync_status}",
    ]

    approved = ctx.approved_decisions
    if approved:
        lines.append(f"- Keputusan disetujui: {len(approved)}")
        for d in approved[:MAX_DECISIONS]:
            lines.append(f"    · [{d.id}] {d.pernyataan}")
        if len(approved) > MAX_DECISIONS:
            lines.append(f"    · … {len(approved) - MAX_DECISIONS} lagi")

    if ctx.open_items:
        lines.append(f"- Item terbuka: {len(ctx.open_items)}")
        for item in ctx.open_items[:MAX_ITEMS]:
            lines.append(f"    · {item}")
        if len(ctx.open_items) > MAX_ITEMS:
            lines.append(f"    · … {len(ctx.open_items) - MAX_ITEMS} lagi")

    parse_errors = errors(issues)
    if parse_errors:
        lines.append(f"- PERINGATAN: {len(parse_errors)} kesalahan format di ledger; "
                     "sebagian konteks mungkin tidak terbaca:")
        for i in parse_errors[:3]:
            lines.append(f"    · {i}")

    lines += [
        "",
        "Ini ringkasan, bukan isi lengkap. Baca berkasnya sebelum drafting "
        "substantif, saran metodologi, perubahan cakupan, atau audit.",
    ]

    emit("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # hook tidak boleh menggagalkan sesi
