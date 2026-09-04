#!/usr/bin/env python3
"""Blokir penulisan ke dokumen Word kecuali ada otorisasi eksplisit.

Dokumen Word adalah artefak yang diserahkan mahasiswa ke pembimbing dan penguji.
Menimpanya bisa menghapus komentar pembimbing, field Mendeley, penomoran, dan
riwayat revisi yang tidak terlihat dari Markdown — dan sering tidak bisa
dipulihkan.

Aturan izinnya dulu hanya prosa yang bisa dilupakan model. Hook ini
menjadikannya jaminan.

Cara pengguna memberi izin: buat `.skripsi-word-authorized` di root proyek,
berisi satu jalur berkas per baris. Baris yang diawali `#` diabaikan.

    echo "naskah/bab3.docx" > .skripsi-word-authorized

Hook tidak boleh pernah menggagalkan sesi karena kesalahannya sendiri: bila
terjadi galat tak terduga, ia mengizinkan dan diam.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORD_SUFFIXES = {".docx", ".doc", ".docm", ".dotx", ".rtf"}
MARKER = ".skripsi-word-authorized"


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def authorized_paths(root: Path) -> set[str]:
    marker = root / MARKER
    if not marker.is_file():
        return set()
    out = set()
    for line in marker.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line)
    return out


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = payload.get("tool_input") or {}
    raw = (tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if not raw:
        return 0

    target = Path(raw)
    if target.suffix.lower() not in WORD_SUFFIXES:
        return 0

    root = Path(payload.get("cwd") or Path.cwd())
    allowed = authorized_paths(root)

    # Cocokkan sebagai jalur absolut maupun relatif terhadap root proyek.
    candidates = {raw, target.name}
    try:
        candidates.add(str(target.resolve().relative_to(root.resolve())))
    except (ValueError, OSError):
        pass

    if candidates & allowed:
        return 0

    deny(
        f"Penulisan ke dokumen Word diblokir: {raw}\n\n"
        "Dokumen Word adalah artefak yang kamu kelola sendiri dan diserahkan ke "
        "pembimbing. Menimpanya bisa menghapus komentar pembimbing, field "
        "Mendeley, penomoran, dan riwayat revisi yang tidak terlihat dari "
        "Markdown.\n\n"
        "Kerjakan perubahannya di Markdown, lalu pindahkan sendiri ke Word.\n\n"
        f"Bila kamu memang ingin berkas ini boleh diubah, daftarkan di "
        f"`{MARKER}` pada root proyek:\n"
        f"    echo \"{raw}\" >> {MARKER}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # gagal terbuka: jangan sampai hook merusak sesi
