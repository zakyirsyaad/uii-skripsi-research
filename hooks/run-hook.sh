#!/usr/bin/env bash
# Pembungkus lintas platform untuk hook Python plugin ini.
#
# Dua masalah yang diselesaikan di Windows:
#
# 1. Claude Code menjalankan perintah hook lewat shell. Di Windows tanpa Git
#    Bash itu PowerShell, yang tidak bisa mengurai string perintah kita.
#    `hooks.json` karena itu mendeklarasikan "shell": "bash".
# 2. Perintah `python3` sering TIDAK ADA di Windows — yang tersedia `python`
#    atau peluncur `py`. Memanggil `python3` langsung membuat kedua hook mati
#    diam-diam di sebagian besar laptop Windows.
#
# Bila tidak ada Python sama sekali, hook gagal terbuka (exit 0) supaya sesi
# tidak rusak — tapi SessionStart tetap memberi tahu pengguna, karena tanpa
# Python seluruh perkakas plugin ini memang tidak bisa dipakai.
set -u

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_NAME="${1:-}"
[ -n "$HOOK_NAME" ] || exit 0
SCRIPT="$HOOK_DIR/$HOOK_NAME"
[ -f "$SCRIPT" ] || exit 0

is_python3() {
    "$1" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 9) else 1)' \
        >/dev/null 2>&1
}

for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && is_python3 "$candidate"; then
        exec "$candidate" "$SCRIPT"
    fi
done

# Peluncur Windows: `py -3` memilih Python 3 terbaru yang terpasang.
if command -v py >/dev/null 2>&1 && py -3 -c 'raise SystemExit(0)' >/dev/null 2>&1; then
    exec py -3 "$SCRIPT"
fi

if [ "$HOOK_NAME" = "session_start_context.py" ]; then
    printf '%s' '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Plugin uii-skripsi-research: Python 3.9+ tidak ditemukan di PATH, jadi seluruh perkakas skripsi (verifikasi sitasi, audit, pencarian literatur) tidak bisa dijalankan dan perlindungan dokumen Word tidak aktif. Pasang Python dari python.org, pastikan ia ada di PATH, lalu mulai sesi baru."}}'
fi
exit 0
