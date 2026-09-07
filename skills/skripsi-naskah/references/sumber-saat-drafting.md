# Menemukan Sumber untuk Klaim yang Sedang Ditulis

Dibaca saat sebuah kalimat butuh sumber dan kamu belum tahu mana yang dipakai.

## Kenapa berkas ini ada

Sebuah sesi drafting menulis paragraf tentang mekanisme `approve`/`transferFrom`
pada ERC-20, lalu menandainya `[SUMBER BELUM DITETAPKAN]` dengan alasan yang
benar: sumber tidak boleh ditempelkan hanya karena ia ada di daftar.

Tapi ia tidak pernah membuka `references/sources.md`. Di sana ada entri
terverifikasi yang kolom `klaim`-nya berbunyi *"…menggunakan Solidity,
OpenZeppelin, dan token ERC-20 dalam skema ICO."* Bertopik sama, dan mungkin
memang tidak sampai ke mekanisme allowance — tapi itu baru bisa dikatakan
setelah dilihat.

Pengguna harus menyuruhnya mencari. Kehati-hatian yang benar, dijalankan
setengah, terbaca sebagai tidak membantu.

## Urutannya

1. **Buka `references/sources.md`.** Cari entri yang topiknya bersinggungan
   dengan klaim yang sedang ditulis.

2. **Kolom `klaim` menutupi klaim ini?** Pakai entri itu. Kolom `klaim` adalah
   pernyataan pemilik ledger tentang apa yang sumber itu dukung; menghormatinya
   bukan menebak.

3. **Bertopik sama tapi `klaim`-nya tidak sejauh itu?** Ini kasus yang paling
   sering, dan paling mudah salah ditangani. Jangan menempelkannya diam-diam,
   dan jangan pula menyatakan tidak ada sumber. Sebut entrinya, jelaskan
   celahnya, lalu tawarkan dua jalan:

   - memeriksa teks lengkap entri itu apakah benar memuat klaimnya, atau
   - mencari sumber baru lewat `skripsi-pustaka`.

4. **Tidak ada yang bersinggungan sama sekali?** Baru tandai belum bersumber —
   dan sebutkan apa saja yang sudah kamu periksa.

## Bentuk laporan yang bisa ditindaklanjuti

Buruk, karena tidak bisa ditindaklanjuti:

    [SUMBER BELUM DITETAPKAN]

Baik, karena pengguna bisa langsung memutuskan:

    [SUMBER BELUM DITETAPKAN] — sudah diperiksa: s4 (Naik 2023) menyebut token
    ERC-20 dalam skema ICO, tapi kolom klaimnya tidak menyentuh mekanisme
    allowance. Mau saya periksa teks lengkap s4, atau carikan sumber khusus
    untuk approve/transferFrom?

Bedanya bukan kehati-hatian — keduanya sama hati-hati. Bedanya apakah pengguna
tahu apa yang sudah dikerjakan dan apa pilihannya.

## Yang tidak berubah

Aturan di `skripsi-sitasi` tetap berlaku penuh:

- Sumber ada ≠ sumber mendukung. Verifikasi membuktikan karyanya nyata, bukan
  bahwa isinya menopang klaimmu.
- Jangan menambah baris ke `references/sources.md` tanpa diminta.
- Klaim tingkat halaman butuh teks lengkap, bukan abstrak.

Berkas ini tidak melonggarkan satu pun. Ia hanya mewajibkan **melihat lebih
dulu**, lalu melaporkan hasilnya.
