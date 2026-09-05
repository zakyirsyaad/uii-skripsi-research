# Membedakan Enam Status Sitasi

Dibaca saat melaporkan hasil verifikasi. Menyamakan ketiga status "tidak OK"
adalah kesalahan yang paling merugikan pengguna.

Tiga status "tidak OK" itu punya arti yang sama sekali berbeda dan tidak boleh
dicampur:

- `NOT_FOUND` adalah **temuan** — sudah dicari di tempat yang memang
  mengindeksnya, dan tidak ada.
- `UNVERIFIED` adalah **ketiadaan temuan** — jaringan gagal, tidak ada yang
  dipelajari.
- `UNVERIFIABLE` adalah **di luar jangkauan** — halaman BPS atau artikel Kontan
  memang tidak pernah masuk basis data sitasi ilmiah. Menandainya fiktif berarti
  menuduh sumber sah. Jenis `institusi` dan `artikel` hampir selalu berakhir di
  sini, dan itu normal.

Sebaliknya, **DOI yang tidak terdaftar tetap `NOT_FOUND` apa pun jenis
sumbernya.** DOI palsu adalah bukti kuat, bukan soal cakupan indeks.

## Kesalahan yang paling mahal

Menyebut sumber sah sebagai fiktif lebih merusak daripada melewatkan satu sitasi
palsu. Mahasiswa yang dituduh mengarang publikasi BPS akan membuang sumber yang
sebenarnya benar, dan kepercayaannya pada seluruh perkakas ini ikut hilang.

Karena itu ambang buktinya berbeda: `NOT_FOUND` hanya boleh dinyatakan untuk
jenis sumber yang memang diindeks, atau untuk DOI yang tidak terdaftar.
