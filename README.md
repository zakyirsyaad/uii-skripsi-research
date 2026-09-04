# UII Skripsi Research

Plugin Codex untuk riset dan penulisan skripsi S1 Informatika UII dengan workflow Markdown-first, sumber akademik terverifikasi, citation trace, serta konteks proyek yang persisten antartask.

## Kemampuan utama

- Membaca `references/thesis-context.md` sebelum melanjutkan pekerjaan skripsi.
- Merekonsiliasi keputusan terbaru, artefak proyek, dan konteks sebelumnya.
- Menyimpan checkpoint hanya untuk keputusan eksplisit dan perubahan status yang material.
- Menjaga Word sebagai artefak yang dikelola pengguna, bukan fallback otomatis.
- Memisahkan bukti akademik, keputusan pengguna, proposal, dan inferensi.
- Menggunakan DSpace UII hanya sebagai referensi format non-sitasi dan KBBI hanya untuk validasi bahasa.

## Struktur

```text
.codex-plugin/plugin.json
skills/uii-skripsi-research/SKILL.md
```

Sumber konteks proyek tidak disertakan dalam plugin. Setiap proyek menyimpan ledger privatnya sendiri di `references/thesis-context.md`.
