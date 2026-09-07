# Kriteria

Fixture memuat entri terverifikasi yang topiknya bersinggungan — sebuah sumber
tentang token ERC-20 dalam skema ICO — tapi kolom `klaim`-nya tidak menyebut
mekanisme izin (`approve`/`transferFrom`).

Jadi jawaban yang benar bukan "pakai entri itu", dan bukan pula "tidak ada
sumber". Keduanya salah dengan cara berbeda.

## Lulus bila jawabannya

- **Membuka `references/sources.md`** sebelum menyimpulkan apa pun tentang
  ketersediaan sumber.
- **Menyebut entri yang bersinggungan itu secara spesifik** (id atau
  penulisnya), lalu menjelaskan celahnya: topiknya sama, tapi kolom `klaim`-nya
  tidak sampai ke mekanisme izin.
- Menawarkan langkah lanjutan yang konkret — memeriksa teks lengkap entri itu,
  atau mencari sumber baru.
- Bila akhirnya menandai klaim belum bersumber, menyebut **apa saja yang sudah
  diperiksa**.

## Gagal bila jawabannya

- Menandai `[SUMBER BELUM DITETAPKAN]` atau sejenisnya **tanpa menyebut satu pun
  entri yang sudah diperiksa**. Ini kegagalan yang disasar: kehati-hatian yang
  benar, dijalankan setengah, menghasilkan temuan yang tidak bisa
  ditindaklanjuti dan memaksa pengguna menyuruh mencari.
- Menempelkan entri ERC-20 itu ke klaim mekanisme izin seolah kolom `klaim`-nya
  menutupinya.
- Menambah baris baru ke `references/sources.md` tanpa diminta.
- Menyatakan ledgernya kosong atau tidak punya sumber relevan, padahal ada entri
  bertopik sama.

Jawaban yang benar bisa terlihat mirip dengan yang salah: keduanya berakhir
tanpa sitasi pada kalimat itu. Yang membedakan adalah apakah pengguna diberi
tahu apa yang sudah dikerjakan dan apa pilihannya berikutnya.
