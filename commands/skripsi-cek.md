---
description: Verifikasi sitasi terhadap Crossref/OpenAlex/DataCite dan audit kuota
argument-hint: "[kosong untuk seluruh ledger, atau DOI/judul tertentu]"
---

Verifikasi sitasi: $ARGUMENTS

Bila argumen kosong, verifikasi seluruh source ledger:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_citation.py --ledger references/sources.md --write
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_references.py
```

Bila argumen berisi DOI atau judul, verifikasi satu itu saja dengan `--doi` atau
`--title/--author/--year`.

Laporkan hasilnya dengan membedakan enam status secara tegas:

- `NOT_FOUND` — sudah dicari di semua sumber dan tidak ada. Sebut ini sebagai
  dugaan kuat sitasi fiktif, dan jangan perhalus.
- `UNVERIFIED` — jaringan gagal. Ini **bukan** temuan; jangan laporkan sebagai
  aman maupun sebagai fiktif. Sarankan mengulang nanti.
- `UNVERIFIABLE` — jenis sumbernya (institusi, artikel) memang tidak diindeks
  Crossref/OpenAlex. Ini normal dan bukan tuduhan. Minta pengguna memeriksa
  manual: tautannya hidup, penerbitnya bernama, tanggalnya ada.
- `MISMATCH` — karyanya ada, metadatanya salah. Tunjukkan bentuk kanoniknya dan
  tawarkan memperbaiki, jangan buang sumbernya.
- `RETRACTED` — buang, lalu periksa klaim yang bersandar padanya.
- `OK` — metadata cocok. Ingatkan bahwa ini belum membuktikan sumbernya
  mendukung klaim; itu masih perlu pembacaan teks lengkap.

Tutup dengan status kuota 20% dan jumlah entri yang masih belum terverifikasi.
