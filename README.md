# UII Skripsi Research

Plugin Claude Code untuk skripsi S1 Informatika UII. Memverifikasi sitasi ke
Crossref/OpenAlex/DataCite, mencari literatur, mengaudit daftar pustaka, dan
menjaga konteks proyek tetap konsisten antar-sesi.

## Kenapa ini ada

Model bahasa gagal pada skripsi dengan cara yang bisa diramalkan: mengarang
sitasi yang terdengar meyakinkan, mengubah istilah di tengah naskah, dan
melupakan keputusan yang sudah disepakati sesi lalu.

Plugin ini menempatkan tiap aturan pada lapis termurah yang masih andal:

| Lapis | Untuk | Contoh |
|---|---|---|
| **Skrip** | Yang bisa diputuskan komputer | DOI ini terdaftar? kuota 20% jebol? |
| **Skill** | Yang butuh pemahaman | Apakah sumber ini benar mendukung klaimnya? |
| **Hook** | Yang tidak boleh terlupa | Muat ledger konteks; lindungi dokumen Word |

Yang bisa dihitung, dihitung — tidak diserahkan ke ingatan model.

## Pasang

```bash
git clone <repo> ~/.claude/plugins/uii-skripsi-research
```

Butuh Python 3.9+. Tidak ada dependensi selain `PyYAML`; skrip jaringan hanya
memakai pustaka standar.

## Pakai

Di direktori proyek skripsimu:

```
/skripsi-init          Siapkan .skripsi.yaml, ledger konteks, source ledger
/skripsi-lanjut        Lanjutkan dari konteks yang tersimpan
/skripsi-cari <klaim>  Cari literatur untuk sebuah klaim
/skripsi-cek           Verifikasi seluruh sitasi + audit kuota
/skripsi-audit [bab]   Audit read-only kesiapan bab atau sidang
/skripsi-checkpoint    Simpan keputusan ke ledger konteks
```

Skrip juga bisa dijalankan langsung:

```bash
python3 scripts/verify_citation.py --doi 10.1145/3313831.3376234
python3 scripts/verify_citation.py --ledger references/sources.md --write
python3 scripts/audit_references.py
python3 scripts/search_literature.py "kata kunci" --since 2021 --oa
python3 scripts/export_mendeley.py --format bibtex > pustaka.bib
python3 scripts/kbbi_lookup.py --check "analisa,sistim,praktek"
```

## Lima status sitasi

Perbedaannya menentukan tindakan, jadi jangan dicampur:

| Status | Artinya |
|---|---|
| `OK` | Karya ada, metadata cocok |
| `MISMATCH` | Karyanya ada, metadatamu salah — perbaiki metadatanya |
| `NOT_FOUND` | Dicari di semua sumber, tidak ada — **dugaan kuat sitasi fiktif** |
| `RETRACTED` | Karya sudah ditarik — buang dan periksa klaim yang bersandar padanya |
| `UNVERIFIED` | Jaringan gagal — **bukan bukti apa-apa**, ulangi nanti |
| `UNVERIFIABLE` | Jenis sumber ini tidak diindeks Crossref — periksa manual |

Tiganya berbeda dan tidak boleh dicampur. `NOT_FOUND` adalah temuan.
`UNVERIFIED` adalah ketiadaan temuan. `UNVERIFIABLE` berarti sumbernya di luar
jangkauan — publikasi BPS dan artikel berita memang tidak pernah masuk basis
data sitasi ilmiah, jadi menandainya fiktif akan menuduh sumber yang sah.

Kegagalan jaringan tidak pernah diam-diam menjadi `OK`.

## Artefak proyekmu

Plugin ini netral dan tidak menyimpan apa pun tentang skripsimu. Semua yang
spesifik proyek hidup di repositori skripsimu sendiri:

| Berkas | Isi |
|---|---|
| `.skripsi.yaml` | Konfigurasi: email polite pool, jalur KBBI, batas kebaruan, kuota |
| `references/thesis-context.md` | Ledger kontinuitas — keputusan, unit aktif, item terbuka |
| `references/sources.md` | Source ledger — tabel Markdown yang dibaca skrip |

Templat ketiganya ada di `templates/`. `/skripsi-init` menyalinnya untukmu.

## Perlindungan dokumen Word

Sebuah hook memblokir penulisan ke `.docx`/`.doc` secara deterministik. Dokumen
Word adalah artefak yang kamu serahkan ke pembimbing; menimpanya bisa menghapus
komentar pembimbing, field Mendeley, dan penomoran yang tidak terlihat dari
Markdown.

Bila kamu memang ingin sebuah berkas boleh diubah:

```bash
echo "naskah/bab3.docx" >> .skripsi-word-authorized
```

Izinnya per berkas, bukan menyeluruh.

## Batas yang perlu kamu tahu

- Skrip membuktikan sebuah **karya nyata dan metadatanya benar**. Ia tidak bisa
  menilai apakah isinya mendukung klaimmu — itu tetap perlu kamu baca sendiri.
- Audit atas Markdown tidak bisa mengesahkan apa pun yang hanya ada di Word:
  penomoran halaman, field Mendeley, komentar, caption, daftar isi, referensi
  silang.
- Repositori DSpace UII hanya rujukan kerangka. Ia tidak pernah boleh masuk
  daftar pustaka.
- Basis data KBBI tidak disertakan; kamu menyediakannya sendiri.

## Tes

```bash
python3 -m unittest discover -s tests -v
```

Tidak ada tes yang menyentuh jaringan; klien API diuji dengan stub.

## Lisensi

MIT.
