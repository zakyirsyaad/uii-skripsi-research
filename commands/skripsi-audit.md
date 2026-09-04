---
description: Audit read-only kesiapan bab atau naskah menjelang sidang
argument-hint: "[bab atau berkas yang diaudit, kosong untuk seluruhnya]"
---

Audit read-only: $ARGUMENTS

**Jangan ubah naskah apa pun selama audit.** Temuan dilaporkan; perbaikan
dikerjakan hanya bila pengguna memintanya setelah melihat laporan.

1. Jalankan yang bisa dihitung mesin lebih dulu, dan laporkan keluarannya apa
   adanya — jangan menilai ulang kuota atau kebaruan dengan mata:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_references.py
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_citation.py --ledger references/sources.md
   ```
2. Baca `references/thesis-context.md` untuk keputusan `approved` terakhir.
3. Untuk audit lintas bab, delegasikan pembacaan menyeluruh ke subagent
   `skripsi-auditor`.
4. Periksa yang tidak bisa dihitung mesin: klaim tanpa bukti, sitasi yang tidak
   menopang klaimnya, terminologi yang bergeser, dan keselarasan rumusan
   masalah → pertanyaan → tujuan → metode → hasil → kesimpulan.

Tutup dengan vonis `ready`, `ready_with_notes`, atau `not_ready`, diikuti daftar
blocker dan perbaikan yang disarankan.

Nyatakan secara eksplisit apa yang **tidak** bisa diaudit dari Markdown —
penomoran halaman, field Mendeley, komentar, caption, daftar isi, dan referensi
silang hanya ada di Word.
