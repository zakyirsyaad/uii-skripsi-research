---
description: Cari literatur akademik untuk sebuah klaim atau topik
argument-hint: "[klaim atau topik yang perlu didukung]"
---

Cari literatur untuk: $ARGUMENTS

1. Bila argumennya berupa topik luas, persempit dulu menjadi klaim spesifik
   yang perlu didukung — tanyakan bila perlu. Pencarian dari topik besar
   menghasilkan ribuan hasil yang tak satu pun menopang kalimat yang ditulis.
2. Susun 2–4 kueri dari sudut berbeda. Satu kueri hampir selalu melewatkan
   literatur relevan.
3. Jalankan untuk tiap kueri:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search_literature.py "<kueri>" --since <tahun> --limit 15`
   Ambil `--since` dari `recency_years` di `.skripsi.yaml`.
4. Bila hasilnya banyak dan mentah, delegasikan ke subagent
   `skripsi-pencari-pustaka` agar konteks utama tidak terisi hasil mentah.
5. Sajikan kandidat tersaring: penulis, tahun, judul, venue, DOI, ketersediaan
   teks lengkap, dan satu kalimat tentang bagian klaim mana yang ia dukung.
6. Sebutkan juga kueri apa saja yang dijalankan dan apa yang **tidak** ditemukan.

Hasil ini kandidat, bukan sitasi. Jangan tambahkan ke `references/sources.md`
sebelum pengguna memilih, dan jangan nyatakan sebuah kandidat mendukung klaim
bila yang dibaca baru abstraknya.
