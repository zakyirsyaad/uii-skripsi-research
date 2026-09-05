---
name: skripsi-pustaka
description: Use when searching for academic literature for a UII Informatics thesis — finding sources that support a specific claim, building a literature review, identifying a research gap, or screening search results down to citable sources. Covers OpenAlex/Crossref search and the screening discipline that turns candidates into citations.
---

# Pencarian Pustaka

## Kandidat bukan sitasi

Hasil pencarian adalah **kandidat**, dan baru menjadi sitasi setelah teks
lengkapnya dibaca dan terbukti mendukung klaim yang dimaksud. Kesalahan paling
umum adalah menyalin judul dan abstrak dari hasil pencarian langsung ke daftar
pustaka. Hasilnya sitasi yang nyata tapi tidak relevan.

```bash
python3 <plugin>/scripts/search_literature.py "kata kunci" --since 2021 --oa --limit 15
python3 <plugin>/scripts/search_literature.py "kata kunci" --min-citations 10 --type article
```

## Cari dari klaim, bukan dari judul skripsi

Mulai dari klaim spesifik yang perlu didukung, bukan dari topik besar.
"Blockchain untuk crowdfunding" menghasilkan ribuan hasil yang tak satu pun
menopang kalimat yang sedang kamu tulis. "Biaya transaksi crowdfunding
terdesentralisasi dibanding terpusat" menghasilkan sedikit hasil yang benar
menopangnya.

Untuk tiap klaim, catat kata kunci yang dipakai dan filter yang dipasang.
Pencarian yang tidak bisa diulang tidak bisa dipertahankan saat sidang.

## Menyaring kandidat

Buang lebih dulu, baru baca dalam:

1. **Venue dan penerbit teridentifikasi?** Tanpa ini, lewati.
2. **Bisa diakses teks lengkapnya secara sah?** Kalau hanya abstrak, ia tidak
   bisa dipakai untuk klaim tingkat halaman. Catat sebagai keterbatasan.
3. **Benar-benar tentang klaimmu?** Judul yang mirip sering membahas hal lain.
4. **Masih dalam batas kebaruan** (`recency_years` di `.skripsi.yaml`), kecuali
   ini teori, metode, atau standar mendasar, yang harus dijustifikasi terpisah.

Jumlah sitasi menunjukkan perhatian, bukan kebenaran. Paper baru yang relevan
lebih berharga daripada paper lama yang banyak disitasi tapi menyerempet.

Waspadai `!! DITARIK` pada keluaran. Karya yang ditarik kadang tetap banyak
disitasi karena orang menyalin daftar pustaka tanpa memeriksa.

## Menemukan celah penelitian

Celah penelitian bukan "belum ada yang meneliti ini". Itu biasanya berarti
pencarianmu kurang dalam. Celah yang bisa dipertahankan berbentuk:

- Metode sudah mapan, tapi belum diuji pada konteks/populasi ini.
- Hasil antar-studi bertentangan dan belum direkonsiliasi.
- Studi terdahulu punya keterbatasan yang mereka nyatakan sendiri.
- Ada asumsi yang tidak pernah diuji.

Bila kamu menyimpulkan celah, tunjukkan pencarian yang mendasarinya. Klaim
"belum ada penelitian" tanpa jejak pencarian adalah inferensi, bukan temuan.
Tandai sebagai `inference` di ledger konteks, bukan `factual_claim`.

## Setelah menemukan sumber

1. Masukkan ke `references/sources.md` dengan kolom `klaim` yang spesifik.
2. Jalankan `verify_citation.py --ledger references/sources.md --write`.
3. Jalankan `audit_references.py` untuk memastikan kuota dan kebaruan aman.

Detail kelayakan sumber, kuota 20%, dan larangan DSpace ada di skill
`skripsi-sitasi`. Baca itu saat memutuskan boleh-tidaknya sebuah sumber, bukan
saat mencari.

## Beban pencarian besar

Bila pencarian akan menghasilkan banyak keluaran mentah (belasan kueri,
puluhan kandidat), delegasikan ke subagent `skripsi-pencari-pustaka` supaya
konteks utama tidak terisi hasil mentah. Yang kembali hanya kandidat tersaring
beserta alasan penyaringannya.
