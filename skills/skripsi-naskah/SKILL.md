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

Tandai `approved` **hanya** dari jawaban tidak ambigu yang merujuk unit itu —
"setuju", "oke", "sudah".

**"lanjut" bukan persetujuan.** Itu instruksi maju ke unit berikutnya; ia tidak
menyelesaikan keberatan yang sudah dinyatakan dan tidak mengesahkan draf yang
ambigu. Bila ada keberatan belum dijawab lalu pengguna menulis "lanjut",
majulah, tapi biarkan unit sebelumnya `revision_requested` dan katakan itu.

Saat pengguna meminta revisi, jaga versi sebelumnya tetap bisa ditelusuri;
tandai `superseded` hanya setelah penggantinya diterima. Jangan diam-diam
menulis ulang unit `approved` karena draf berikutnya memakai istilah atau
cakupan berbeda — sebutkan ketergantungannya, lalu jalankan impact sweep.

Untuk alur pendek, penanda status di dalam respons sudah cukup. Jangan membuat
berkas pelacak kecuali diminta.

## Persetujuan kata ≠ verifikasi klaim

Pemisahan yang paling sering runtuh. Persetujuan pengguna atas sebuah paragraf
mengesahkan **kata-katanya**, bukan kebenaran klaim di dalamnya.

Paragraf `approved` boleh jadi provenance untuk keputusan proyek atau pilihan
diksi, tapi **tidak pernah** jadi bukti klaim faktual: tiap klaim tetap harus
menunjuk ke `references/sources.md` atau berkas proyek terverifikasi.

Jangan menandai status bukti sebuah inferensi atau klaim faktual sebagai
`verified` hanya karena pengguna menerima paragrafnya.

## Baca ledgernya sebelum menandai klaim tanpa sumber

Menulis `[SUMBER BELUM DITETAPKAN]` tanpa membuka `references/sources.md` lebih
dulu menghasilkan temuan yang tidak bisa ditindaklanjuti.

Kolom `klaim` sebuah entri menutupi klaim ini? Pakai. Bertopik sama tapi tidak
sejauh itu? **Sebut entri dan celahnya**, lalu tawarkan memeriksa teks
lengkapnya atau mencari sumber lain. Tidak ada yang bersinggungan? Baru tandai
belum bersumber, sambil menyebut apa yang sudah diperiksa.

Menempelkan sumber hanya karena ia ada di daftar tetap dilarang
(`skripsi-sitasi`). Prosedur lengkap dan contoh laporannya ada di
`references/sumber-saat-drafting.md`.

## Impact sweep setelah keputusan berubah

Ketika pengguna menolak, mempersempit, mengganti, atau mengoreksi keputusan
proyek, telusuri elemen yang bergantung padanya sebelum melanjutkan: judul,
rumusan masalah, pertanyaan penelitian, tujuan, batasan, terminologi,
metodologi, rancangan sistem, rencana evaluasi, kerangka bab, prosa yang sudah
disetujui, tabel dan gambar, source ledger, sitasi, dan jejak sitasi.

Laporkan tiap elemen sebagai `unaffected`, `needs_revision`, `superseded`, atau
`needs_confirmation`. Berhenti memakai bahasa dan bukti yang `superseded`.

Untuk koreksi kecil, jaga sweep tetap proporsional: laporkan hanya
ketergantungan yang benar-benar ada. Sweep yang membengkak untuk perbaikan
sepele sama tidak bergunanya dengan sweep yang dilewatkan.

## Bahasa

Validasi istilah dengan basis data KBBI lokal, bukan dari ingatan:

```bash
python3 <plugin>/scripts/kbbi_lookup.py --word kualitatif
python3 <plugin>/scripts/kbbi_lookup.py --check "analisa,sistim,praktek"
```

Kode keluar 2 berarti KBBI belum terpasang. Dalam keadaan itu **jangan
menyimpulkan baku atau tidak-baku dari ingatan.** Katakan bahwa kebakuannya belum
terverifikasi, arahkan ke <https://kbbi.kemdikbud.go.id>, lalu lanjutkan menulis.

Percayai keluaran skripnya: `baku`, `TIDAK BAKU -> pakai: X`, atau `TIDAK ADA`.
Jangan menilai ulang dari ingatan. Alasannya, dan batas apa yang sebenarnya
sahih diperiksa, ada di `references/kbbi.md`.

KBBI hanya untuk bahasa dan **tidak pernah** menjadi bukti untuk klaim teknis
atau ilmiah. Detail ragam akademik ada di `references/bahasa-akademik.md`.

## Word adalah artefak pengguna

Markdown adalah artefak kerja; dokumen Word adalah artefak yang dikelola
pengguna untuk diserahkan. Tiga mode izin, dan izin **tidak berpindah** antar
tugas, berkas, atau topik:

- `markdown_only` (default) — jangan buka, parse, render, ekspor, atau ubah
  Word. Satu pengecualian: `audit_naskah.py` atas berkas yang disebut pengguna
  untuk audit, karena itu naik ke `read_only_audit` (lihat `skripsi-kesiapan`).
- `read_only_audit` — periksa hanya berkas yang disebut pengguna; jangan simpan,
  ubah, ekspor, atau buat salinan turunan.
- `edit_authorized` — ubah hanya berkas yang disebut, hanya untuk perubahan yang
  diminta eksplisit.

Kembali ke `markdown_only` setelah tugas yang diizinkan selesai. Hook plugin
memblokir `Write`, `Edit`, dan `NotebookEdit` ke berkas Word. Hook
**tidak** mencegat Bash: membongkar `.docx` lewat `unzip`, menyunting XML-nya,
lalu memampatkannya kembali secara teknis bisa dilakukan. **Jangan lakukan
itu** — mengakali pelindung mengalahkan gunanya, dan memampatkan ulang arsip
Word dengan tangan bisa merusak bagian yang tidak kamu sentuh. Hook ini jaring
pengaman untuk kelalaian, bukan tantangan.

Jangan mengklaim format Word, field Mendeley, komentar, penomoran halaman,
caption, daftar isi, atau referensi silang sudah diverifikasi dari Markdown.
Status sinkronisasi dipelihara pengguna, jangan disimpulkan dari timestamp.
Bila tidak diketahui, lanjutkan dari Markdown sambil menyebut Word mungkin
berbeda; bila pengguna menyatakan Word lebih baru, minta Markdown terbaru dulu.
