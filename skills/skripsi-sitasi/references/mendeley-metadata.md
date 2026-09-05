# Metadata Mendeley

Dibaca saat menyiapkan atau memvalidasi record di Mendeley. `verify_citation.py`
sudah mengambil bentuk kanonik; berkas ini soal memindahkannya tanpa rusak.

## Ambil dari sumber kanonik

Pakai metadata dari penerbit, rekaman registrasi DOI, badan standar resmi, atau
teks lengkap yang sah diakses. Ikuti pengalihan (redirect) dan pastikan halaman
pendaratan dan berkas yang terunduh merujuk karya yang sama. Ini sering meleset
pada agregator.

Periksa: jenis item, judul lengkap, urutan dan ejaan penulis, tahun terbit,
venue atau penerbit, volume, nomor, halaman atau nomor artikel, edisi bila
relevan, serta DOI atau URL stabil.

## Nama yang tidak boleh ditebak

Pertahankan penulis organisasi sebagai penulis korporat; jangan pecah menjadi
kolom nama depan/belakang. `export_mendeley.py` sudah membungkusnya
`{{Nama Organisasi}}` di BibTeX supaya BibTeX tidak membaliknya. Jangan melepas
kurung itu saat menyunting manual.

Jangan menebak pemenggalan nama majemuk, partikel (`van`, `de`, `bin`,
`al-`), inisial, atau nama lembaga. Bila ragu, salin persis seperti tertulis di
halaman penerbit.

## Jangan mengarang yang kosong

Nomor terbitan, halaman, kota, ISBN, atau DOI yang tidak ada **dibiarkan
kosong**. Field kosong jujur; field terisi tebakan menyesatkan dan tidak bisa
dibedakan dari data asli oleh pembaca berikutnya.

Bila sumber metadata saling bertentangan, catat konfliknya dan utamakan rekaman
penerbit atau DOI, kecuali teks lengkap jelas menunjukkan koreksi.

## Sufiks a/b/c

Untuk beberapa karya oleh penulis atau organisasi yang sama pada tahun yang
sama: jaga metadata penulis dan tahun tetap konsisten, lalu biarkan gaya sitasi
atau reference manager yang menetapkan sufiks `a`, `b`, `c` **setelah** himpunan
daftar pustaka stabil.

Jangan menetapkan sufiks dari urutan pencarian atau ingatan. Setelah stabil,
pastikan sufiks di dalam teks dan di daftar pustaka cocok.

## KBBI

Bila diminta memeriksa istilah, tanyakan jalur basis data KBBI lokal yang sudah
disetujui pengguna, lalu jalankan `kbbi_lookup.py`. Gunakan hanya untuk validasi
bahasa; simpan URL sumber asli dan tanggal pengambilan saat melaporkan hasil.

Basis data KBBI adalah dataset leksikal. Sebutkan sebagai sumber hanya bila
dataset itu sendiri yang sedang dibahas, dan **tidak pernah** sebagai pendukung
klaim tentang blockchain, crowdfunding, UI/UX, atau topik teknis lain.
