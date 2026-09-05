# Eval Perilaku Skill

Skrip plugin ini diuji 139 tes unit. Yang **tidak** diuji tes itu adalah
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

Suite ini berjalan dengan `--ablation with-without` secara bawaan: ia
membandingkan hasil dengan dan tanpa plugin. Selisihnya menunjukkan apakah
plugin benar-benar mengubah perilaku, bukan sekadar model yang kebetulan
menjawab benar.

## Delapan kasus

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

## Kenapa kasusnya seperti itu

Tiap kasus menyasar kegagalan yang **jawabannya bisa kebetulan benar**.

Contoh paling jelas ada di `kbbi-tidak-terpasang`. Model yang menjawab "analisa
tidak baku, yang benar analisis" memberi jawaban yang benar — dan tetap GAGAL,
karena ia menebak. Ejaan Indonesia justru bidang yang sering salah diingat
model: `analisa`, `praktek`, dan `obyek` semuanya terasa benar, dan ketiganya
memang ada di KBBI sebagai bentuk tidak baku.

Eval yang hanya memeriksa kebenaran jawaban akan meloloskan kegagalan itu.

## Hubungannya dengan tes unit

`tests/test_eval_kontrak.py` menjaga agar aturan yang mendasari tiap kasus masih
tertulis di skill-nya. Ia tidak menguji perilaku — ia menangkap penghapusan
aturan dalam milidetik, sementara eval mahal dan jarang dijalankan.

Menambah kasus eval baru **wajib** disertai tes kontraknya. Ada tes yang
menegakkan itu.
