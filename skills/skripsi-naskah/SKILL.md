---
name: skripsi-naskah
description: Use when drafting or revising thesis prose for a UII Informatics thesis — writing paragraph by paragraph, tracking which unit is approved, handling revisions, running an impact sweep after a decision changes, checking Indonesian academic register against KBBI, or deciding how to treat the Word document.
---

# Naskah Skripsi

## Satu unit aktif

Drafting berjalan satu unit pada satu waktu. Unit bisa berupa paragraf, tabel,
subbab, atau item lain yang bernama jelas. Tiap unit punya satu status:

`draft` → `awaiting_review` → `approved`
                            ↘ `revision_requested` → (versi baru) → `approved`
                              versi lama menjadi `superseded`

Tandai `approved` **hanya** dari jawaban yang tidak ambigu dan merujuk unit itu
— "setuju", "oke", "sudah". 

**"lanjut" bukan persetujuan.** Itu instruksi untuk maju ke unit berikutnya. Ia
tidak menyelesaikan keberatan yang sudah dinyatakan dan tidak mengesahkan draf
yang masih ambigu. Bila ada keberatan yang belum dijawab lalu pengguna menulis
"lanjut", majulah — tapi biarkan unit sebelumnya tetap `revision_requested`, dan
katakan itu.

Saat pengguna meminta revisi, jaga versi sebelumnya tetap bisa ditelusuri.
Tandai `superseded` hanya setelah penggantinya diterima.

Jangan diam-diam menulis ulang unit yang sudah `approved` karena draf berikutnya
memakai istilah atau cakupan berbeda. Sebutkan ketergantungannya, lalu jalankan
impact sweep.

Untuk alur pendek, penanda status di dalam respons sudah cukup. Jangan membuat
berkas pelacak hanya untuk menyimpan status drafting kecuali diminta.

## Persetujuan kata ≠ verifikasi klaim

Ini pemisahan yang paling sering runtuh. Persetujuan pengguna atas sebuah
paragraf mengesahkan **kata-katanya**, bukan kebenaran klaim di dalamnya.

Sebuah paragraf yang sudah `approved` boleh menjadi provenance untuk keputusan
proyek atau pilihan diksi. Ia **tidak pernah** menjadi bukti untuk klaim
faktual: tiap klaim di dalamnya tetap harus menunjuk ke `references/sources.md`
atau berkas proyek yang terverifikasi.

Jangan menandai status bukti sebuah inferensi atau klaim faktual sebagai
`verified` hanya karena pengguna menerima paragrafnya.

## Impact sweep setelah keputusan berubah

Ketika pengguna menolak, mempersempit, mengganti, atau mengoreksi sebuah
keputusan proyek, telusuri dulu semua elemen yang bergantung padanya sebelum
melanjutkan. Periksa yang relevan dari: judul, rumusan masalah, pertanyaan
penelitian, tujuan, batasan, terminologi, metodologi, rancangan sistem, rencana
evaluasi, kerangka bab, prosa yang sudah disetujui, tabel dan gambar, source
ledger, sitasi, dan jejak sitasi.

Laporkan tiap elemen sebagai `unaffected`, `needs_revision`, `superseded`, atau
`needs_confirmation`. Berhenti memakai bahasa dan bukti yang sudah `superseded`.

Untuk koreksi kecil dan lokal, jaga sweep tetap proporsional — laporkan hanya
ketergantungan yang benar-benar ada. Sweep yang membengkak untuk perbaikan
sepele sama tidak bergunanya dengan sweep yang dilewatkan.

## Bahasa

Validasi istilah dengan basis data KBBI lokal, bukan dari ingatan:

```bash
python3 <plugin>/scripts/kbbi_lookup.py --word kualitatif
python3 <plugin>/scripts/kbbi_lookup.py --check "analisa,sistim,praktek"
```

### Bila KBBI tidak terpasang

Skrip keluar dengan kode 2 dan pesan "belum dikonfigurasi". Saat itu terjadi,
**jangan menyimpulkan baku atau tidak-baku dari ingatan.** Itu persis kegagalan
yang plugin ini ada untuk mencegahnya, dan ejaan bahasa Indonesia justru bidang
yang sering salah diingat model.

Yang harus dilakukan:

1. Katakan bahwa kebakuan kata itu **belum terverifikasi**, jangan diam-diam
   dilewati.
2. Arahkan pengguna memeriksa manual di <https://kbbi.kemdikbud.go.id>, atau
   memasang basis datanya lewat `/plugin configure uii-skripsi-research`.
3. Lanjutkan menulis. Kebakuan satu kata bukan alasan menghentikan drafting —
   tapi juga bukan sesuatu yang boleh diklaim sudah benar.

Daftar di `references/bahasa-akademik.md` adalah **contoh yang sering muncul**,
bukan pengganti pemeriksaan. Menemukan sebuah kata di sana boleh dipakai; tidak
menemukannya di sana tidak membuktikan kata itu baku.

### Ada di KBBI bukan berarti baku

KBBI mencatat bentuk **tidak baku** sebagai lema tersendiri yang hanya merujuk ke
bentuk bakunya — `analisa ? analisis`, `praktek Lihat praktik`. Karena itu
"ketemu di kamus" tidak membuktikan apa pun.

`kbbi_lookup.py --check` sudah mendeteksi rujukan silang ini dan melaporkan tiga
keadaan: `baku`, `TIDAK BAKU -> pakai: X`, atau `TIDAK ADA`. Percayai keluarannya,
jangan menilai ulang dari ingatan.

### Batas basis data KBBI

Yang sahih hanya pemeriksaan **ada/tidaknya lema di kamus utama** — itu turunan
KBBI Edisi IV. Basis data yang beredar juga memuat tabel pasangan baku/tidak-baku,
sinonim, dan antonim yang **sebagian dihasilkan AI**; jangan perlakukan tabel itu
sebagai otoritas. Untuk kasus yang menentukan, KBBI Daring resmi tetap rujukannya.

KBBI hanya untuk bahasa. Ia **tidak pernah** menjadi bukti untuk klaim teknis
atau ilmiah. Detail ragam akademik ada di `references/bahasa-akademik.md`.

## Word adalah artefak pengguna

Markdown adalah artefak kerja; dokumen Word adalah artefak yang dikelola
pengguna untuk diserahkan. Tiga mode izin, dan izin **tidak berpindah** antar
tugas, berkas, atau topik:

- `markdown_only` (default) — jangan buka, parse, render, ekspor, atau ubah Word.
- `read_only_audit` — periksa hanya berkas yang disebut pengguna untuk audit ini;
  jangan simpan, ubah, ekspor, atau buat salinan turunan.
- `edit_authorized` — ubah hanya berkas yang disebut, hanya untuk perubahan yang
  diminta eksplisit.

Kembali ke `markdown_only` setelah tugas yang diizinkan selesai. Hook plugin ini
memblokir penulisan ke `.docx`/`.doc` secara deterministik; hook itu jaring
pengaman, bukan pengganti aturan di atas.

Jangan mengklaim format Word, field Mendeley, komentar, penomoran halaman,
caption, daftar isi, atau referensi silang sudah diverifikasi dari Markdown.
Status sinkronisasi adalah informasi yang dipelihara pengguna — jangan
disimpulkan dari timestamp berkas. Bila statusnya tidak diketahui, lanjutkan
dari Markdown sambil menyebut bahwa Word mungkin berbeda. Bila pengguna
menyatakan Word lebih baru, minta Markdown terbaru sebelum mengubah bagian itu.
