# Kelayakan Sumber

Dibaca saat memutuskan boleh-tidaknya sebuah sumber masuk daftar pustaka.

Susun inti akademik dengan urutan prioritas ini:

1. Artikel jurnal peer-review, penelitian asli, prosiding bereputasi dengan
   venue/penerbit yang teridentifikasi.
2. Buku akademik dan standar resmi. Teori mendasar boleh tua; bukti empiris
   dan kontekstual harus mengikuti batas kebaruan di `.skripsi.yaml`.
3. Sumber institusional primer untuk aturan, statistik, atau data resmi —
   hanya bila lembaga itu **pemilik** datanya. Utamakan penerbit aslinya.
4. Artikel populer hanya untuk konteks terbatas, maksimum
   `floor(total_referensi × 0.20)`.

Halaman berita, editorial, explainer, atau blog komersial tetap dihitung
`artikel` meski penerbitnya kredibel. **Jangan melabelinya ulang sebagai
`institusi` untuk menghindari kuota** — `audit_references.py` menghitung dari
kolom `tipe`, jadi pelanggaran hanya berpindah, tidak hilang.

Tolak tulisan anonim, konten SEO, agregator sitasi, salinan hasil scraping, dan
halaman tanpa penanggung jawab redaksi. Terima artikel hanya bila punya
penerbit bernama, penulis atau redaksi yang bertanggung jawab, tanggal terbit,
URL stabil, dan hubungan langsung dengan klaim.

## Kenapa kuotanya mengikat

Kuota 20% bukan soal gengsi akademik. Artikel populer menyaring dan
menyederhanakan temuan orang lain; menyandarkan argumen padanya berarti
menyitasi tafsiran, bukan penelitiannya.

Batasnya `floor(total × 0.20)` — dihitung `audit_references.py`, bukan
diperkirakan. Dengan 12 sumber, jatahnya 2. Dengan 19 sumber, tetap 3.
