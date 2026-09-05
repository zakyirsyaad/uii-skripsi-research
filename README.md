# UII Skripsi Research

Plugin Claude Code untuk mahasiswa S1 Informatika UII. Plugin ini memverifikasi
sitasi ke basis data ilmiah sungguhan, mencari literatur, mengaudit daftar
pustaka, dan menjaga konteks skripsi tetap konsisten antar-sesi.

> Bahasa Indonesia sepenuhnya. Gratis, tanpa API key, tanpa akun.

---

## Daftar isi

- [Kenapa ini ada](#kenapa-ini-ada)
- [Yang dibutuhkan](#yang-dibutuhkan)
- [Pasang](#pasang)
- [Setelan pertama kali](#setelan-pertama-kali)
- [Mulai cepat](#mulai-cepat)
- [Alur kerja sehari-hari](#alur-kerja-sehari-hari)
- [Daftar perintah](#daftar-perintah)
- [Berkas di proyek skripsimu](#berkas-di-proyek-skripsimu)
- [Patokan panjang naskah](#patokan-panjang-naskah)
- [Kebijakan sumber dan kuota 20%](#kebijakan-sumber-dan-kuota-20)
- [Enam status sitasi](#enam-status-sitasi)
- [Perlindungan dokumen Word](#perlindungan-dokumen-word)
- [Menjalankan skripnya langsung](#menjalankan-skripnya-langsung)
- [Masalah umum](#masalah-umum)
- [Plugin tidak menambah sumber sendiri](#plugin-tidak-menambah-sumber-sendiri)
- [Yang TIDAK bisa dilakukan plugin ini](#yang-tidak-bisa-dilakukan-plugin-ini)
- [Privasi dan data](#privasi-dan-data)
- [Untuk pengembang](#untuk-pengembang)

---

## Kenapa ini ada

Model bahasa punya beberapa kesalahan khas saat dipakai menulis skripsi:

- **Mengarang sitasi.** Judul, penulis, tahun, bahkan DOI yang terdengar
  meyakinkan, padahal karyanya tidak pernah ada.
- **Menggeser istilah.** "Pengguna" di Bab 1 menjadi "pemakai" di Bab 4.
- **Melupakan keputusan.** Sesi kemarin sudah sepakat memakai satu metode, sesi
  hari ini mengusulkan metode lain.

Plugin ini membagi pekerjaan menjadi tiga lapis. Apa pun yang bisa dihitung
komputer dihitung oleh skrip, tidak diserahkan pada ingatan model.

| Bagian | Mengerjakan apa | Contoh |
|---|---|---|
| **Skrip** | Hal yang jawabannya pasti | DOI ini terdaftar? Kuota 20% sudah lewat? |
| **Skill** | Hal yang perlu dibaca dan dinilai | Sumber ini mendukung klaimnya? |
| **Hook** | Hal yang gampang terlupa | Memuat konteks, melindungi berkas Word |

Jadi saat kamu memverifikasi sitasi, plugin benar-benar menghubungi Crossref,
OpenAlex, dan DataCite untuk memastikan karyanya ada.

---

## Yang dibutuhkan

- **Claude Code** (versi yang mendukung plugin).
- **Python 3.9 atau lebih baru**, ada di PATH.
- **Git for Windows (Git Bash)**, hanya bagi pengguna Windows.

Seluruh perkakas inti memakai pustaka standar Python saja, jadi tidak perlu
`pip install`.

Satu pengecualian: `analisis_dspace.py` butuh `pypdf`, karena membaca PDF dari
pustaka standar tidak realistis. Skrip itu opsional dan tidak dipakai perkakas
lain. Bila `pypdf` belum ada, skrip berhenti sambil menyebut perintah yang perlu
dijalankan:

```bash
uv run --with pypdf analisis_dspace.py <berkas.pdf>
```

Cek Python-mu:

```bash
python3 --version
```

Kalau perintah itu tidak dikenali, coba `python --version` atau `py -3 --version`.
Kalau ketiganya gagal, pasang Python dari [python.org](https://www.python.org/downloads/)
dan centang **"Add Python to PATH"** saat memasang.

---

## Pasang

Claude Code menemukan plugin lewat *marketplace*. Menyalin folder ke
`~/.claude/plugins/` tidak akan berhasil.

```bash
claude plugin marketplace add zakyirsyaad/uii-skripsi-research
claude plugin install uii-skripsi-research@uii-skripsi
```

Lalu restart Claude Code. Perubahan plugin hanya berlaku di sesi baru.

Pastikan berhasil:

```bash
claude plugin list
claude plugin details uii-skripsi-research
```

Kamu semestinya melihat 11 skill/perintah, 2 agent, dan 2 hook.

---

## Setelan pertama kali

Saat memasang, kamu ditanya dua hal, sekali saja, bukan di tiap proyek.

### `mailto` (disarankan diisi)

Email yang dikirim ke Crossref, OpenAlex, dan DataCite sebagai perkenalan.
Ketiga API itu memberi jalur rate limit yang jauh lebih longgar untuk pemakai
yang menyertakan alamat email.

- Ini bukan autentikasi. Tidak membuat akun dan tidak memberi akses apa pun.
- Boleh dikosongkan. Verifikasi tetap jalan, hanya jauh lebih lambat.
- Baca [Privasi dan data](#privasi-dan-data) sebelum memutuskan.

### `kbbi_db_path` (wajib untuk validasi bahasa)

Jalur ke basis data SQLite KBBI. Tanpa ini kebakuan kata tidak bisa
diverifikasi, dan plugin akan menolak menebaknya.

Belum punya? Unduh dengan:

```bash
python3 <plugin>/scripts/setup_kbbi.py
```

Skrip itu mengambil KBBI Edisi IV (115.978 lema, ~26 MB), menormalkannya, dan
memverifikasi hasilnya. `/skripsi-init` juga menawarkannya bila belum ada.

> **Hak cipta.** Data kamusnya milik Badan Pengembangan dan Pembinaan Bahasa
> (Kemendikbud). Sumbernya menyatakan penggunaan komersial dilarang, tunduk pada
> UU No. 28 Tahun 2014. Skrip ini tidak mendistribusikan ulang data itu, hanya
> mengunduhkannya untuk pemakaianmu sendiri.
>
> Hanya kamus utama Edisi IV yang diambil. Tabel baku/tidak-baku, sinonim, dan
> antonim di repositori yang sama sebagian dihasilkan AI, jadi sengaja tidak
> diunduh.

Mengubah keduanya kapan saja:

```
/plugin configure uii-skripsi-research
```

---

## Mulai cepat

Buka Claude Code di folder skripsimu, lalu:

```
/skripsi-init
```

Perintah itu membuat tiga berkas dan menanyakan `project_id` serta batas
kebaruan sumber. Email dan KBBI tidak ditanyakan lagi.

Setelah itu isi beberapa sumber di `references/sources.md`, lalu:

```
/skripsi-cek
```

Plugin menghubungi Crossref, OpenAlex, dan DataCite untuk sumber yang memang
mereka indeks, menuliskan status verifikasinya kembali ke berkas, dan melaporkan
kuota sumber non-akademik. Sumber `institusi` dan `artikel` tanpa DOI tidak
dikirim ke sana sama sekali; lihat [Enam status sitasi](#enam-status-sitasi).

---

## Alur kerja sehari-hari

```
Buka sesi   →  hook memuat ringkasan konteks otomatis
            →  /skripsi-lanjut     lanjutkan dari unit terakhir

Butuh sumber →  /skripsi-cari "klaim yang perlu didukung"
            →  baca teks lengkapnya, masukkan ke references/sources.md
            →  /skripsi-cek        pastikan sumbernya nyata

Menulis      →  drafting paragraf demi paragraf, satu unit aktif
            →  "setuju" menyetujui unit; "lanjut" hanya memajukan

Ada keputusan →  /skripsi-checkpoint   simpan ke ledger konteks

Mau ganti bab →  /skripsi-audit        vonis kesiapan + daftar blocker
```

---

## Daftar perintah

| Perintah | Gunanya |
|---|---|
| `/skripsi-init` | Siapkan `.skripsi.yaml`, ledger konteks, dan source ledger |
| `/skripsi-lanjut` | Lanjutkan dari konteks tersimpan; laporkan unit aktif dan item terbuka |
| `/skripsi-cari <klaim>` | Cari literatur untuk sebuah klaim spesifik |
| `/skripsi-cek [DOI/judul]` | Verifikasi sitasi + audit kuota. Tanpa argumen: seluruh ledger |
| `/skripsi-audit [bab]` | Audit read-only kesiapan bab atau menjelang sidang |
| `/skripsi-checkpoint <apa>` | Simpan keputusan atau perubahan status ke ledger |

Selain perintah, ada lima **skill** yang aktif sendiri saat relevan
(`skripsi-uii`, `skripsi-sitasi`, `skripsi-pustaka`, `skripsi-naskah`,
`skripsi-kesiapan`) dan dua **subagent** read-only untuk pekerjaan berat
(`skripsi-pencari-pustaka`, `skripsi-auditor`).

---

## Berkas di proyek skripsimu

Plugin ini netral dan tidak menyimpan apa pun tentang skripsimu. Semua yang
spesifik proyek hidup di foldermu sendiri.

```text
proyek-skripsi/
├── .skripsi.yaml               setelan proyek
├── references/
│   ├── thesis-context.md       ledger kontinuitas antar-sesi
│   └── sources.md              source ledger (dibaca skrip)
└── naskah/                     naskah Markdown-mu (bebas namanya)
```

### `references/sources.md`

Tabel Markdown berkolom tetap. Urutan dan nama kolomnya tidak boleh diubah
karena skrip memparsenya.

```
| id | tipe | penulis | tahun | judul | venue | doi_url | klaim | status_verifikasi | tgl_verifikasi |
```

- `tipe` — `jurnal`, `prosiding`, `buku`, `standar`, `institusi`, atau `artikel`.
- `penulis` — nama keluarga penulis pertama, atau nama organisasi utuh.
- `klaim` — klaim spesifik yang didukung sumber ini. Pipa di dalam sel ditulis `\|`.
- `status_verifikasi` — jangan diisi tangan. `/skripsi-cek` yang mengisinya.
- `tgl_verifikasi` — format ISO `YYYY-MM-DD`.

### `references/thesis-context.md`

Catatan istilah: **abstrak di template UII bernama SARI.** Kata "abstrak" maupun
"abstract" tidak pernah dipakai, jadi mencarinya dengan istilah umum akan
menghasilkan temuan palsu.

Frontmatter YAML berisi `project_id`, `active_unit`, `last_checkpoint_at`, dan
`word_sync_status`, diikuti tabel keputusan, item terbuka, dan artefak.

Dua sumbu yang sengaja dipisah dan tidak boleh dicampur:

- **Status keputusan** — `proposed`, `approved`, `rejected`, `superseded`, `unconfirmed`
- **Status bukti** — `verified`, `unverified`, `unverifiable`, `mismatch`, `not_found`, `retracted`

Menyetujui sebuah paragraf berarti menyetujui kata-katanya, bukan kebenaran
klaim di dalamnya. Tiap klaim faktual tetap harus menunjuk sumber terverifikasi.

Ledger ini bukan bukti ilmiah dan tidak boleh disitasi.

---

## Patokan panjang naskah

Diukur dari skripsi Informatika UII yang sudah lolos sidang. Untuk skripsi
**pengembangan sistem**, yang membangun aplikasi atau platform:

| Bab | Kata |
|---|---|
| I Pendahuluan | ±1.900 |
| II Kajian Pustaka | ±2.100 |
| III Metodologi | 5.800–6.800 |
| IV Hasil dan Pembahasan | 1.800–2.600 |
| V Kesimpulan dan Saran | 850–1.200 |
| **Total isi** | **±13.500** |

Panjang kalimat yang lazim 19–23 kata rata-rata. Prosa yang seluruhnya di bawah
15 kata terbaca patah-patah.

Kepadatan halaman berbeda tajam antar bab. BAB I dan II sekitar 260–300 kata per
halaman, BAB IV hanya 119–163 karena didominasi tangkapan layar. Jadi "BAB IV
dua puluh halaman" sebenarnya hanya sekitar 2.500 kata tulisan.

Rincian dan profil skripsi berbasis riset ada di
`skills/skripsi-uii/references/format-uii.md`.

## Kebijakan sumber dan kuota 20%

Susun inti akademik dengan urutan prioritas:

1. Artikel jurnal peer-review, penelitian asli, prosiding bereputasi.
2. Buku akademik dan standar resmi.
3. Sumber institusional primer, hanya bila lembaga itu pemilik datanya.
4. Artikel populer untuk konteks terbatas, maksimum `floor(total × 0.20)`.

Berita, editorial, explainer, dan blog komersial tetap dihitung `artikel` meski
penerbitnya kredibel. Melabelinya ulang sebagai `institusi` tidak menolong,
karena `audit_references.py` menghitung dari kolom `tipe`. Pelanggarannya hanya
berpindah.

Batas kebaruan (`recency_years`, default 5 tahun) berlaku untuk bukti empiris.
`buku` dan `standar` dikecualikan, karena teori mendasar dan standar resmi tidak
kedaluwarsa seperti data empiris.

Gaya sitasi **APA 6th**, bukan IEEE. Template resmi Informatika UII
menetapkannya eksplisit, dan `templates/skripsi.yaml` sudah memakai itu sebagai
bawaan. Template juga mewajibkan setiap entri daftar pustaka disitasi di dalam
teks. Sumber yang tercatat tapi tak pernah dirujuk adalah temuan.

**Repositori DSpace UII bukan sumber.** Ia hanya rujukan untuk memeriksa nama
bab, urutan bagian, dan cara metode disajikan. Tidak pernah masuk sitasi,
catatan kaki, daftar pustaka, atau tinjauan pustaka.

DSpace berada di balik proteksi bot Cloudflare, jadi plugin tidak bisa
membukanya sendiri dan tidak akan mencoba menembusnya. Buka tautannya di
peramban biasa, simpan PDF-nya, lalu:

```bash
python3 <plugin>/scripts/analisis_dspace.py ~/Downloads/skripsi-uii/
```

Skrip itu melaporkan kerangka bab, jumlah kata dan halaman per bab, kepadatan
kata per halaman, struktur subbab, statistik panjang kalimat, metode yang
disebut, dan ukuran daftar pustaka. Ia sengaja tidak pernah mencetak kalimat
dari sumbernya.

---

## Enam status sitasi

| Status | Artinya | Yang harus kamu lakukan |
|---|---|---|
| `OK` | Karya ada, metadata cocok | Pakai |
| `MISMATCH` | Karyanya ada, metadatamu salah | Perbaiki metadatanya, jangan buang sumbernya |
| `NOT_FOUND` | Dicari di tempat yang mengindeksnya, tidak ada | **Dugaan kuat sitasi fiktif.** Jangan pakai |
| `RETRACTED` | Karya sudah ditarik | Buang, dan periksa klaim yang bersandar padanya |
| `UNVERIFIED` | Jaringan gagal | Belum sempat dicari. Ulangi nanti |
| `UNVERIFIABLE` | Jenis sumbernya tidak diindeks | Skrip mengecek tautannya masih hidup; penerbit dan tanggal periksa sendiri |

Tiga status terakhir sering tertukar padahal artinya jauh berbeda. `NOT_FOUND`
adalah temuan: pencarian sudah dilakukan di tempat yang tepat dan karyanya tidak
ada. `UNVERIFIED` berarti jaringannya gagal, jadi belum ada yang diketahui.
`UNVERIFIABLE` berarti jenis sumbernya memang tidak pernah masuk basis data
sitasi ilmiah, seperti publikasi BPS atau artikel berita.

Hanya `jurnal`, `prosiding`, `buku`, dan `standar` yang benar-benar diindeks.
Tipe `institusi` dan `artikel` hampir selalu berakhir `UNVERIFIABLE`, dan itu
normal. Tapi DOI palsu tetap `NOT_FOUND` untuk semua tipe, karena itu bukti,
bukan soal cakupan indeks.

Kegagalan jaringan tidak pernah diam-diam menjadi `OK`.

---

## Perlindungan dokumen Word

Sebuah hook memblokir penulisan ke `.docx`, `.doc`, `.docm`, `.dotx`, dan
`.rtf`. Dokumen Word adalah artefak yang kamu serahkan ke pembimbing.
Menimpanya bisa menghapus komentar pembimbing, field Mendeley, penomoran
halaman, dan riwayat revisi yang tidak terlihat dari Markdown.

Alur yang dianjurkan: kerjakan semuanya di Markdown, lalu pindahkan sendiri ke
Word.

Bila kamu memang ingin satu berkas boleh diubah:

```bash
echo "naskah/bab3.docx" >> .skripsi-word-authorized
```

Izinnya per berkas, bukan menyeluruh. Berkas `.docx` lain tetap terblokir.

**Batasnya.** Hook ini menjaga operasi tulis-berkas (`Write`, `Edit`,
`NotebookEdit`), bukan Bash. Membongkar `.docx` lewat `unzip`, menyunting
XML-nya, lalu memampatkan ulang tidak dicegat. Aturan untuk tidak
melakukannya ada di skill, dan model mematuhinya saat diuji, tapi hook ini
membuat kelalaian sulit dan bukan pengakalan mustahil. Jangan perlakukan
sebagai jaminan mutlak.

---

## Menjalankan skripnya langsung

Semua skrip bisa dipanggil tanpa Claude Code. Ganti `<plugin>` dengan
`~/.claude/plugins/cache/uii-skripsi/uii-skripsi-research/<versi>`.

```bash
# satu sitasi
python3 <plugin>/scripts/verify_citation.py --doi 10.1145/3313831.3376234
python3 <plugin>/scripts/verify_citation.py --title "Judul" --author "Keluarga" --year 2024

# seluruh ledger, tulis balik statusnya
python3 <plugin>/scripts/verify_citation.py --ledger references/sources.md --write

# kuota, kebaruan, kelengkapan metadata
python3 <plugin>/scripts/audit_references.py

# cari literatur
python3 <plugin>/scripts/search_literature.py "kata kunci" --since 2021 --oa --limit 15

# ekspor ke Mendeley (hanya entri terverifikasi)
python3 <plugin>/scripts/export_mendeley.py --format bibtex > pustaka.bib
python3 <plugin>/scripts/export_mendeley.py --format ris > pustaka.ris

# audit naskah Word terhadap template resmi UII
python3 <plugin>/scripts/audit_naskah.py naskah.docx

# analisis bentuk skripsi UII lain sebagai rujukan kerangka
python3 <plugin>/scripts/analisis_dspace.py ~/Downloads/skripsi-uii/

# siapkan basis data KBBI (sekali saja)
python3 <plugin>/scripts/setup_kbbi.py

# periksa kata baku
python3 <plugin>/scripts/kbbi_lookup.py --check "analisa,sistim,praktek"
```

Keluaran pemeriksaan kebakuan menyebut bentuk yang benar, tidak sekadar
menandai:

```
Diperiksa 3 kata; 3 bermasalah.
  TIDAK BAKU  analisa -> pakai: analisis
  TIDAK BAKU  sistim -> pakai: sistem
  TIDAK BAKU  praktek -> pakai: praktik
```

**"Ada di KBBI" tidak berarti baku.** KBBI mencatat bentuk tidak baku sebagai
lema tersendiri yang merujuk ke bentuk bakunya, jadi `analisa`, `praktek`, dan
`obyek` semuanya ada di kamus. Plugin mendeteksi rujukan silang itu. Pemeriksa
yang hanya mengecek keberadaan kata akan meloloskan ketiganya.

Tambahkan `--json` pada hampir semua skrip untuk keluaran yang bisa diolah.

Exit code `verify_citation.py`: `0`=OK, `1`=MISMATCH, `2`=NOT_FOUND,
`3`=UNVERIFIED, `4`=RETRACTED, `5`=UNVERIFIABLE.
`audit_references.py` keluar `1` bila ada blocker.

---

## Masalah umum

**Plugin tidak muncul setelah dipasang.**
Restart Claude Code. Perubahan plugin hanya berlaku di sesi baru. Lalu cek
`claude plugin list`.

**Verifikasi sitasi sangat lambat.**
`mailto` belum diisi, jadi kamu masuk jalur rate limit paling ketat. Jalankan
`/plugin configure uii-skripsi-research`.

**Sumber BPS atau artikel berita ditandai `UNVERIFIABLE`.**
Itu normal. Basis data sitasi ilmiah tidak mengindeks jenis sumber itu. Skrip
sudah mengecek tautannya masih hidup dan melaporkannya; yang perlu kamu periksa
sendiri adalah penerbit bernama dan tanggal terbit.

**Hook tidak jalan di Windows.**
Pastikan Git for Windows (Git Bash) terpasang dan Python ada di PATH. Bila
Python tidak ditemukan, plugin akan mengatakannya di awal sesi.

**`audit_references.py` mengeluh format ledger.**
Pesannya menyebut nomor baris dan kolom yang salah. Penyebab tersering: kolom
diubah urutannya, atau ada pipa `|` di dalam sel yang belum ditulis `\|`.

**Sudah menyunting plugin tapi tidak ada perubahan.**
Naikkan `version` di kedua manifest, jalankan `claude plugin update`, lalu
restart. `update` menolak menyegarkan bila nomor versinya sama.

---

## Plugin tidak menambah sumber sendiri

Plugin tidak akan menambahkan baris ke `references/sources.md` tanpa kamu minta,
bahkan ketika sumbernya jelas dibutuhkan, dan bahkan setelah DOI-nya
terverifikasi.

Alasannya: verifikasi membuktikan karyanya ada, bukan bahwa isinya mendukung
klaimmu. Kolom `klaim` hanya bisa diisi jujur oleh yang sudah membaca teks
lengkapnya.

Yang kamu dapat sebagai gantinya adalah baris siap tempel dengan metadata
kanonik dan kolom `klaim` dikosongkan. Kamu yang memutuskan masuk atau tidak.

Kolom `status_verifikasi` dan `tgl_verifikasi` boleh ditulis perkakas, karena
isinya temuan, bukan komitmen. Itulah yang `--write` lakukan.

## Yang TIDAK bisa dilakukan plugin ini

- **Skrip membuktikan sebuah karya nyata dan metadatanya benar.** Apakah isinya
  mendukung klaimmu tetap harus kamu pastikan sendiri dari teks lengkapnya.
- **Audit Markdown tidak bisa mengesahkan apa pun yang hanya ada di Word:**
  penomoran halaman, field Mendeley, komentar, caption, daftar isi, referensi
  silang.
- **Tidak memeriksa plagiarisme atau kemiripan.** Pakai perkakas kampus untuk itu.
- **Pemeriksaan bahasa terbatas pada kebakuan lema.** Tata kalimat, koherensi
  paragraf, dan ketepatan istilah dalam konteks tidak dinilai. Untuk kasus yang
  menentukan, KBBI Daring resmi tetap rujukannya.
- **Tidak menggantikan kepengarangan.** Plugin menyusun draf paragraf demi
  paragraf, tapi tiap unit baru berlaku setelah kamu menyetujuinya. Gagasan
  penelitiannya (rumusan masalah, celah, pilihan metode, tafsir hasil) tetap
  milikmu, dan kamu yang menjawab di sidang. Yang dijaga plugin adalah
  disiplin bukti dan konsistensi.
- **Tidak menjamin kelulusan.** Vonis `ready` berarti pemeriksaan otomatis
  bersih, tidak lebih.

---

## Privasi dan data

- **`mailto` benar-benar dikirim keluar**, ke `api.crossref.org`,
  `api.openalex.org`, dan `api.datacite.org`. Crossref dan OpenAlex menerimanya
  sebagai parameter URL sekaligus header `User-Agent`; DataCite hanya lewat
  header. Ketiganya lembaga akademik nirlaba, tapi alamatmu tetap meninggalkan
  mesinmu. Kosongkan bila kamu keberatan.
- **Judul dan penulis sumber yang kamu verifikasi juga dikirim** ke API itu.
  Memang begitu cara kerjanya.
- **Untuk sumber `institusi` dan `artikel`, plugin menghubungi situs sumbernya
  langsung**, misalnya bps.go.id atau portal berita, dengan permintaan `HEAD`
  untuk mengecek tautannya masih hidup. Situs itu melihat kunjungan dari
  mesinmu. `mailto` tidak ikut dikirim ke sana.
- **Naskah skripsimu tidak pernah dikirim ke mana pun** oleh skrip plugin ini.
- **Respons API disimpan di cache lokal** `.skripsi-cache/` supaya API tidak
  dihubungi berulang. Tambahkan ke `.gitignore`.
- **Jangan simpan data sensitif di ledger**, seperti rekaman wawancara, kontak
  responden, atau kredensial. Ledger itu untuk keputusan proyek.

---

## Untuk pengembang

```bash
git clone https://github.com/zakyirsyaad/uii-skripsi-research
cd uii-skripsi-research
python3 -m unittest discover -s tests -v     # tes unit, nol menyentuh jaringan
claude plugin eval .                         # eval perilaku skill (early access)
claude plugin validate .
claude plugin validate .claude-plugin/marketplace.json
```

Tes unit menguji skripnya. Eval menguji perilaku modelnya: apakah ia menolak
menebak, apakah ia membedakan status sitasi dengan benar. Delapan kasusnya
dijelaskan di [`evals/README.md`](evals/README.md).

Memasang salinan lokal untuk dikembangkan. Pakai jalur absolut, `.` tidak
diterima:

```bash
claude plugin marketplace add /jalur/absolut/ke/uii-skripsi-research
claude plugin install uii-skripsi-research@uii-skripsi
```

Suntingan tidak langsung berlaku. Naikkan `version` di kedua manifest
(`plugin.json` dan `marketplace.json` harus cocok), lalu:

```bash
claude plugin update uii-skripsi-research@uii-skripsi
```

dan restart sesi.

Aturan arsitektur yang perlu dijaga ada di [`CLAUDE.md`](CLAUDE.md), terutama
dua hal: jangan memindahkan pemeriksaan yang bisa dihitung kembali menjadi
prosa, dan jangan memperkenalkan kembali ketergantungan pihak ketiga.

---

## Lisensi

MIT.
