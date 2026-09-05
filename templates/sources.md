# Source Ledger

Tabel ini dibaca mesin. Jaga agar kolomnya tetap persis seperti di bawah — nama
dan urutan header tidak boleh diubah, karena `audit_references.py` dan
`export_mendeley.py` memparsenya.

Aturan pengisian:

- `tipe` — salah satu: `jurnal`, `prosiding`, `buku`, `standar`, `institusi`, `artikel`.
  Lima yang pertama adalah inti akademik. `artikel` adalah sumber non-akademik
  (berita, blog, explainer, siaran pers komersial) dan terkena kuota
  `floor(total × 0.20)`. Jangan melabeli ulang artikel jadi `institusi` untuk
  menghindari kuota — halaman resmi pemerintah/kampus hanya `institusi` bila ia
  benar-benar pemilik data yang dirujuk.
- `penulis` — nama keluarga penulis pertama, atau nama organisasi utuh untuk
  penulis korporat. Jangan pecah nama organisasi menjadi nama orang.
- `doi_url` — DOI (`10.xxxx/...`) bila ada; kalau tidak, URL stabil. Kosongkan
  hanya kalau sumbernya benar-benar tidak punya keduanya.
- `klaim` — klaim spesifik yang didukung sumber ini. Satu baris, ringkas. Kalau
  satu sumber mendukung beberapa klaim yang berjauhan, buat baris terpisah.
  Pipa di dalam sel harus di-escape sebagai `\|`.
- `status_verifikasi` — **jangan diisi tangan.** Diisi `verify_citation.py`:
  `verified`, `unverified`, `unverifiable`, `mismatch`, `not_found`, atau
  `retracted`. `not_found` berarti karyanya dicari di tempat yang memang
  mengindeksnya dan tidak ada — dugaan kuat sitasi halusinasi. `unverifiable`
  berarti jenis sumbernya (biasanya `institusi` atau `artikel`) tidak diindeks
  basis data sitasi ilmiah; itu normal. Keterjangkauan tautannya sudah dicek
  skrip; yang tersisa untukmu adalah memastikan penerbitnya bernama, tanggalnya
  ada, dan lembaganya benar pemilik data.
- `tgl_verifikasi` — ISO `YYYY-MM-DD`, diisi otomatis saat verifikasi.

Baris di bawah adalah **placeholder struktur**, bukan sitasi sungguhan. Ganti
seluruhnya; jangan pernah menyalin baris contoh ke daftar pustaka.

Sengaja tidak ada baris bertipe `artikel`: dengan tiga sumber, kuotanya
`floor(3 × 0.20) = 0`, jadi satu baris contoh saja sudah membuat proyek baru
gagal audit sebelum mahasiswanya menulis apa pun.

| id | tipe | penulis | tahun | judul | venue | doi_url | klaim | status_verifikasi | tgl_verifikasi |
|---|---|---|---|---|---|---|---|---|---|
| s001 | jurnal | NamaKeluarga | 2024 | Judul artikel jurnal | Nama Jurnal | 10.xxxx/contoh | Klaim spesifik yang didukung sumber ini | unverified |  |
| s002 | institusi | Badan Pusat Statistik | 2025 | Judul publikasi resmi | BPS | https://contoh.go.id/publikasi | Data statistik yang dirujuk di Bab 1 | unverified |  |
| s003 | prosiding | NamaKeluarga | 2023 | Judul makalah konferensi | Nama Konferensi | 10.xxxx/contoh2 | Klaim lain yang didukung sumber ini | unverified |  |
