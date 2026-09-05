---
name: skripsi-sitasi
description: Use when adding, checking, or exporting citations for a UII Informatics thesis — verifying that a source actually exists and its metadata is canonical, deciding whether a source is admissible, keeping the 20% non-academic quota, preparing Mendeley records, or writing Word citation-trace comments in Indonesian.
---

# Sitasi Skripsi

Sitasi adalah tempat model paling sering gagal: karya yang tidak pernah ada
ditulis dengan penuh percaya diri. Karena itu **verifikasi di sini dijalankan,
bukan dinilai.** Jangan pernah menyatakan sebuah sitasi sahih tanpa menjalankan
skripnya.

## Jalankan, jangan menebak

```bash
# satu sitasi
python3 <plugin>/scripts/verify_citation.py --doi 10.1145/3313831.3376234
python3 <plugin>/scripts/verify_citation.py --title "Judul" --author "Keluarga" --year 2024

# seluruh ledger, tulis balik statusnya
python3 <plugin>/scripts/verify_citation.py --ledger references/sources.md --write

# kuota, kebaruan, kelengkapan
python3 <plugin>/scripts/audit_references.py

# ekspor ke Mendeley (hanya entri terverifikasi)
python3 <plugin>/scripts/export_mendeley.py --format bibtex > pustaka.bib
```

Lima status, dan **beda di antaranya menentukan tindakan**:

| Status | Artinya | Tindakan |
|---|---|---|
| `OK` | Karya ada, metadata cocok | Pakai |
| `MISMATCH` | Karyanya ada, metadatamu salah | Perbaiki metadata ke bentuk kanonik, jangan buang sumbernya |
| `NOT_FOUND` | Sudah dicari di Crossref, OpenAlex, DataCite — tidak ada | **Dugaan kuat sitasi fiktif.** Jangan pakai sampai kamu menunjukkan bukti keberadaannya |
| `RETRACTED` | Karya sudah ditarik | Buang, dan periksa klaim yang bersandar padanya |
| `UNVERIFIED` | Jaringan gagal | **Bukan bukti apa-apa.** Jangan laporkan sebagai aman maupun fiktif; ulangi nanti |
| `UNVERIFIABLE` | Jenis sumber ini tidak diindeks Crossref/OpenAlex | Periksa manual: tautan hidup, penerbit bernama, tanggal ada |

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
sumbernya** — DOI palsu adalah bukti kuat, bukan soal cakupan indeks.

## Sumber mana yang boleh

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

## Gaya sitasi: APA 6th

Template resmi Informatika UII menetapkan **APA 6th**, bukan IEEE. Ini berlaku
pada template 2020 maupun 2025. Jangan menawarkan gaya lain kecuali pembimbing
menyatakannya secara eksplisit — dan bila itu terjadi, catat sebagai keputusan
di ledger beserta provenance-nya.

**Setiap entri daftar pustaka wajib disitasi di dalam teks.** Sumber yang
tercatat di `references/sources.md` tapi tidak pernah dirujuk di naskah adalah
temuan yang harus dilaporkan, bukan cadangan yang tidak apa-apa dibiarkan.
`audit_references.py` tidak bisa memeriksa ini sendiri — ia tidak membaca
naskahmu — jadi periksalah saat audit bab.

## DSpace UII bukan sumber

Repositori DSpace UII (`Undergraduate Thesis → Faculty of Industrial Technology
→ Informatics Engineering`) hanya untuk memeriksa nama bab, urutan bagian,
frasa akademik Indonesia, dan cara penyajian metode.

**Tidak pernah** masukkan item DSpace ke sitasi, catatan kaki, daftar pustaka,
tinjauan pustaka, matriks perbandingan, atau bukti penelitian — termasuk ketika
metode atau kerangkanya sedang dipertimbangkan. DSpace juga bukan bukti bahwa
sebuah metode cocok untuk penelitianmu; ia hanya menunjukkan bagaimana metode
itu pernah *dituliskan*.

## Sumber ada ≠ sumber mendukung

Skrip hanya membuktikan karyanya nyata dan metadatanya benar. Ia tidak bisa
menilai apakah isinya mendukung klaimmu — itu bagianmu, dan tetap wajib:

- Baca teks lengkap yang benar-benar bisa diakses, bukan abstrak atau cuplikan.
- Pastikan klaim di kolom `klaim` memang ditopang bagian yang kamu tunjuk.
- Bila satu paragraf memakai beberapa sumber, pastikan tiap klaim punya
  pendukungnya sendiri; kalau tidak, pecah paragrafnya.

Nyatakan terus terang bila bukti akademik yang memadai tidak ditemukan. Jangan
pernah mengarang sitasi atau menambal kuota dengan sumber lemah.

## Rujukan lanjutan

Baca hanya saat relevan:

- `references/mendeley-metadata.md` — memvalidasi record Mendeley, nama korporat,
  konflik metadata, sufiks a/b/c untuk karya sepenulis-setahun.
- `references/jejak-sitasi.md` — format komentar jejak sitasi untuk Word, dan
  cara memisahkan dukungan langsung dari sintesis dan inferensi.
