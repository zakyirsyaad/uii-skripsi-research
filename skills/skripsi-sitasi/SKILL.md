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
python3 <plugin>/scripts/verify_citation.py --doi 10.1145/3313831.3376234
python3 <plugin>/scripts/verify_citation.py --title "Judul" --author "Keluarga" --year 2024
python3 <plugin>/scripts/verify_citation.py --ledger references/sources.md --write
python3 <plugin>/scripts/audit_references.py                       # kuota, kebaruan
python3 <plugin>/scripts/export_mendeley.py --format bibtex        # entri verified saja
```

Enam status, dan **beda di antaranya menentukan tindakan**:

| Status | Artinya | Tindakan |
|---|---|---|
| `OK` | Karya ada, metadata cocok | Pakai |
| `MISMATCH` | Karyanya ada, metadatamu salah | Perbaiki metadata ke bentuk kanonik, jangan buang sumbernya |
| `NOT_FOUND` | Sudah dicari di Crossref, OpenAlex, DataCite — tidak ada | **Dugaan kuat sitasi fiktif.** Jangan pakai sampai kamu menunjukkan bukti keberadaannya |
| `RETRACTED` | Karya sudah ditarik | Buang, dan periksa klaim yang bersandar padanya |
| `UNVERIFIED` | Jaringan gagal | **Bukan bukti apa-apa.** Jangan laporkan sebagai aman maupun fiktif; ulangi nanti |
| `UNVERIFIABLE` | Jenis sumber ini tidak diindeks Crossref/OpenAlex | Periksa manual: tautan hidup, penerbit bernama, tanggal ada |

Ketiga status "tidak OK" itu artinya berbeda-beda dan **tidak boleh dicampur**.
Penjelasan tiap perbedaannya, dan kenapa tipe `institusi` serta `artikel` hampir
selalu berakhir `UNVERIFIABLE`, ada di `references/status-sitasi.md`.

## Sumber mana yang boleh

Inti akademik disusun berurutan: jurnal peer-review dan prosiding bereputasi,
lalu buku dan standar resmi, lalu sumber institusional primer. Artikel populer
hanya untuk konteks terbatas, maksimum `floor(total × 0.20)`.

Berita, editorial, dan blog komersial tetap `artikel` meski penerbitnya
kredibel. **Jangan melabelinya ulang jadi `institusi` untuk menghindari kuota** —
`audit_references.py` menghitung dari kolom `tipe`, jadi pelanggarannya hanya
berpindah.

Kriteria kelayakan lengkap, dan apa yang membuat sebuah artikel ditolak, ada di
`references/kelayakan-sumber.md`.

## Gaya sitasi: APA 6th

Template resmi UII menetapkan **APA 6th**, bukan IEEE — berlaku di template 2020
maupun 2025. Gaya lain hanya bila pembimbing menyatakannya, dan itu dicatat
sebagai keputusan berprovenance di ledger.

**Setiap entri daftar pustaka wajib disitasi di dalam teks.** Sumber yang
tercatat tapi tak pernah dirujuk adalah temuan, bukan cadangan. Skrip tidak bisa
memeriksanya — ia tidak membaca naskah — jadi periksa saat audit bab.

## DSpace UII bukan sumber

Repositori DSpace UII (`Undergraduate Thesis → Faculty of Industrial Technology
→ Informatics Engineering`) hanya untuk memeriksa nama bab, urutan bagian,
frasa akademik Indonesia, dan cara penyajian metode.

**Tidak pernah** masukkan item DSpace ke sitasi, catatan kaki, daftar pustaka,
tinjauan pustaka, matriks perbandingan, atau bukti penelitian — termasuk ketika
metode atau kerangkanya sedang dipertimbangkan. DSpace juga bukan bukti bahwa
sebuah metode cocok untuk penelitianmu; ia hanya menunjukkan bagaimana metode
itu pernah *dituliskan*.

## Sumber ada ≠ sumber mendukung, dan kapan boleh menulis ke ledger

Skrip membuktikan karyanya nyata dan metadatanya benar. Ia **tidak** bisa menilai
apakah isinya mendukung klaimmu. Itu butuh membaca teks lengkap yang benar-benar
bisa diakses — bukan abstrak, bukan cuplikan pencarian.

Konsekuensinya: menambah baris ke `references/sources.md` berarti menyatakan
sumber itu akan disitasi, dan itu komitmen yang hanya bisa dibuat orang yang
sudah membacanya — bukan olehmu.

| Tindakan | Boleh sendiri? |
|---|---|
| Isi `status_verifikasi` dan `tgl_verifikasi` | **Ya** — itu temuan perkakas, bukan komitmen. Inilah yang `--write` lakukan |
| Buat berkas kosong lewat `/skripsi-init` | Ya |
| **Tambah baris baru** | **Tidak.** Butuh permintaan eksplisit |
| Ubah kolom yang ditulis mahasiswa | **Tidak** |
| Hapus baris | **Tidak** |

Berlaku juga saat sumbernya jelas tak terhindarkan — Peffers untuk DSRM, Hevner
untuk design science. **"Jelas dibutuhkan" bukan izin**; ia hanya membuat
persetujuannya cepat didapat.

Sebagai gantinya, **sajikan baris siap tempel**: metadata kanonik hasil
verifikasi, `klaim` dikosongkan, disertai keterangan bahwa kamu belum membaca
teks lengkapnya. Ledger berisi sumber yang belum dibaca pemiliknya akan runtuh
di sidang.

Saat menyusun klaim: pastikan kolom `klaim` memang ditopang bagian yang kamu
tunjuk, dan bila satu paragraf memakai beberapa sumber, pastikan tiap klaim
punya pendukungnya sendiri — kalau tidak, pecah paragrafnya. Nyatakan terus
terang bila bukti yang memadai tidak ditemukan; jangan menambal kuota dengan
sumber lemah.

## Rujukan lanjutan

Baca hanya saat relevan:

- `references/mendeley-metadata.md` — memvalidasi record Mendeley, nama korporat,
  konflik metadata, sufiks a/b/c untuk karya sepenulis-setahun.
- `references/kelayakan-sumber.md` — kriteria penerimaan sumber dan kuota 20%.
- `references/jejak-sitasi.md` — format komentar jejak sitasi untuk Word, dan
  cara memisahkan dukungan langsung dari sintesis dan inferensi.
