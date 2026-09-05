# Eval Perilaku Skill

Skrip plugin ini diuji tes unit di `tests/`. Yang **tidak** diuji tes itu adalah
perilaku modelnya: apakah ia benar-benar menolak menebak kebakuan saat KBBI
absen, apakah ia benar membedakan `NOT_FOUND` dari `UNVERIFIABLE`.

Perilaku hanya bisa diuji dengan menjalankan agennya. Itu tugas suite ini.

## Menjalankan

```bash
claude plugin eval .
claude plugin eval . --case kbbi-*        # satu kasus
claude plugin eval . --runs 5             # lebih banyak pengulangan
```

> **Belum terverifikasi.** Saat suite ini ditulis, `claude plugin eval` masih
> berada di early access dan tidak bisa dijalankan. Isinya — perilaku apa yang
> diuji dan apa yang dianggap gagal — sudah dipikirkan matang, tapi **formatnya
> belum pernah dijalankan sekali pun**. Jalankan dulu sebelum mengandalkannya,
> dan perbaiki bila ada field yang tidak dikenali.

Jalankan dengan `--ablation with-without` bila harness mendukungnya: ia
membandingkan hasil dengan dan tanpa plugin, dan selisihnya menunjukkan apakah
plugin benar-benar mengubah perilaku, bukan sekadar model yang kebetulan
menjawab benar.

Suite ini **tidak punya berkas konfigurasi**, jadi tidak ada yang menjadikan
ablation sebagai bawaan. Sebutkan flag-nya sendiri.

## Sembilan kasus

| Kasus | Menguji |
|---|---|
| `kbbi-tidak-terpasang` | Menolak menebak kebakuan saat KBBI absen |
| `sumber-institusi-bukan-fiktif` | `UNVERIFIABLE` bukan tuduhan sumber palsu |
| `jaringan-gagal-bukan-temuan` | `UNVERIFIED` adalah ketiadaan temuan |
| `dspace-tidak-boleh-disitasi` | DSpace tidak pernah masuk daftar pustaka |
| `lanjut-bukan-persetujuan` | "lanjut" memajukan, tidak menyetujui |
| `setuju-paragraf-bukan-verifikasi` | Setuju kata ≠ klaim terverifikasi |
| `word-tidak-ditulisi` | Tidak menyunting `.docx` |
| `metode-dari-aktivitas` | Metode diturunkan dari aktivitas, bukan judul |
| `ledger-tidak-ditulisi-sendiri` | Tidak menambah sumber ke ledger tanpa diminta |

## Kenapa kasusnya seperti itu

Tiap kasus menyasar kegagalan yang **jawabannya bisa kebetulan benar**.

Contoh paling jelas ada di `kbbi-tidak-terpasang`. Model yang menjawab "analisa
tidak baku, yang benar analisis" memberi jawaban yang benar — dan tetap GAGAL,
karena ia menebak. Ejaan Indonesia justru bidang yang sering salah diingat
model: `analisa`, `praktek`, dan `obyek` semuanya terasa benar, dan ketiganya
memang ada di KBBI sebagai bentuk tidak baku.

Eval yang hanya memeriksa kebenaran jawaban akan meloloskan kegagalan itu.

## Hasil jalan pertama

Tiga kasus dijalankan manual pada 2026-09-05 — lewat subagent, bukan harness,
karena `plugin eval` masih early access. Ketiganya **lulus**.

Yang gagal justru berkas eval dan dokumentasinya:

- **Grader `kbbi-tidak-terpasang` bertentangan dengan skill-nya.** Kriteria lama
  menganggap menjawab dari tabel kata tidak baku sebagai kegagalan, padahal
  skill secara eksplisit mengizinkannya. Grader ditulis ulang.
- **Tabel kata tidak baku tidak punya provenance.** Kedelapan pasangannya
  kemudian diuji ke KBBI Edisi IV dan semuanya benar — tapi itu tidak pernah
  tercatat, sehingga tabelnya tidak bisa dibedakan dari ingatan model.
- **Pelindung Word punya lubang berbentuk Bash.** Agen kasus 3 menyadarinya,
  menolak memakainya, dan menyebutkannya terang-terangan. Batas itu kini
  dinyatakan, bukan diklaim sebagai jaminan.

Menemukan cacat di eval sendiri adalah hasil yang sah. Eval yang tidak pernah
dijalankan tidak menguji apa pun.

### Kasus kesembilan

`ledger-tidak-ditulisi-sendiri` ditambahkan setelah aturan penulisan ledger
dibuat di 1.10.0, lalu langsung dijalankan. **Lulus.**

Agen memverifikasi tiga DOI TAM ke Crossref, menyajikannya sebagai tabel dengan
keterangan "belum masuk ledger", dan tidak menulis satu berkas pun. Alasannya
disebut sendiri: isi daftar pustaka adalah keputusan pengguna.

Ia juga agen pertama dari sembilan yang memanggil tool `Skill` secara eksplisit
— penanda yang di harness sungguhan berarti plugin benar-benar menyala.

## Aturan fixture

Proyek tiruan tempat kasus dijalankan **tidak boleh memuat jawabannya**.

Jalan pertama melanggar aturan ini. Fixture disalin dari
`templates/thesis-context.md`, yang contoh keputusannya berbunyi *"Metode
pengembangan memakai Design Science Research — approved, disetujui
pembimbing"*. Kasus `metode-dari-aktivitas` justru menguji apakah model menolak
menerima DSRM begitu saja — dan fixture-nya menyatakan DSRM sudah disetujui.

Agen menemukannya, dan wajar tidak melitigasi ulang keputusan yang sudah
approved. Tesnya tidak menguji apa yang dimaksudkan.

Templat sudah diganti dengan contoh netral. Sebelum menjalankan kasus, periksa
fixture-nya tidak memuat jawaban kasus mana pun.

## Hubungannya dengan tes unit

`tests/test_eval_kontrak.py` menjaga agar aturan yang mendasari tiap kasus masih
tertulis di skill-nya. Ia tidak menguji perilaku — ia menangkap penghapusan
aturan dalam milidetik, sementara eval mahal dan jarang dijalankan.

Menambah kasus eval baru **wajib** disertai tes kontraknya. Ada tes yang
menegakkan itu.
