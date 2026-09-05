---
name: skripsi-kesiapan
description: Use before declaring a thesis chapter complete, moving to the next chapter, or preparing for a defense in a UII Informatics thesis — a read-only consistency and readiness check covering claims without evidence, terminology drift, alignment between research questions and results, the 20% source quota, and unresolved drafting state.
---

# Audit Naskah

Audit bersifat **read-only**. Jangan menulis ulang naskah yang sudah disetujui
selama audit. Temuan dilaporkan; perbaikan dikerjakan hanya bila pengguna
memintanya dan izin artefaknya mengizinkan.

## Jalankan yang bisa dihitung lebih dulu

```bash
python3 <plugin>/scripts/audit_references.py
python3 <plugin>/scripts/verify_citation.py --ledger references/sources.md --only-unverified
python3 <plugin>/scripts/audit_naskah.py naskah.docx
```

`audit_naskah.py` **membaca** naskah Word. Membaca berbeda dari menulis:
menyunting `.docx` tetap diblokir hook, tapi memeriksanya justru wajib. Naskah
yang diserahkan ke pembimbing berformat Word, dan sebagian cacat hanya kelihatan
di sana. Skrip ini menemukan sisa teks template, daftar isi yang belum
di-update, halaman awal yang hilang, dan gaya sitasi yang salah.

Ini sudah menutup kuota 20%, kebaruan, duplikat, kelengkapan metadata, dan
keberadaan sumber. Jangan menilai ulang hal-hal itu dengan mata; bacalah
keluarannya.

## Yang harus dinilai manusia/model

Setelah skrip bersih, periksa yang tidak bisa dihitung mesin:

1. **Klaim tanpa bukti.** Tiap klaim faktual menunjuk ke entri source ledger?
   Klaim yang sebenarnya inferensi peneliti harus ditulis sebagai inferensi,
   bukan disamarkan dengan sitasi yang menyerempet.
2. **Sitasi mendukung klaimnya.** Sumbernya nyata (sudah dipastikan skrip), tapi
   apakah bagian yang ditunjuk benar menopang kalimat itu?
3. **Tiap sumber benar-benar dipakai.** Bandingkan `references/sources.md`
   dengan sitasi di naskah. Entri yang tidak pernah dirujuk melanggar aturan
   template resmi dan harus dibuang atau dipakai. Skrip tidak bisa memeriksa
   ini karena tidak membaca naskahmu.
4. **Keselarasan rantai.** Rumusan masalah → pertanyaan penelitian → tujuan →
   metodologi → implementasi → evaluasi → kesimpulan. Setiap pertanyaan
   terjawab? Setiap tujuan tercapai atau dinyatakan tidak tercapai?
5. **Konsistensi terminologi.** Satu konsep satu istilah, sepanjang naskah.
6. **Status unit drafting.** Ada revisi yang belum selesai? Untuk materi lama
   yang ditulis borongan tanpa riwayat status, laporkan status "tidak diketahui"
   hanya bila itu menyembunyikan revisi yang belum tuntas. Kalau tidak,
   perlakukan sebagai catatan, bukan penghalang.
7. **Keputusan cocok dengan ledger.** Yang tertulis di naskah sesuai keputusan
   `approved` terakhir, bukan yang sudah `superseded`.
8. **Konsistensi internal Markdown.** Hierarki heading, penomoran tabel dan
   gambar, referensi silang, dan entri daftar pustaka.
9. **Celah yang harus dinyatakan.** Teks lengkap yang tidak bisa diakses,
   metadata yang belum tuntas, dan status sinkronisasi Word.

## Vonis

Tutup dengan salah satu:

- `ready` — tidak ada temuan.
- `ready_with_notes` — ada peringatan, tapi tidak ada yang menghalangi.
- `not_ready` — ada blocker. Sebutkan tiap blocker dan perbaikan yang disarankan.

Blocker minimal: sitasi `not_found` atau `retracted`, kuota 20% jebol, klaim
faktual tanpa bukti, pertanyaan penelitian yang tidak terjawab, atau revisi
yang belum selesai pada unit yang diklaim selesai.

`audit_naskah.py` menutup sebagian celah Word, tapi tidak seluruhnya. Audit
**tidak bisa** mengesahkan hal yang hanya ada di Word:
penomoran halaman, field Mendeley, komentar, caption, daftar isi, referensi
silang. Nyatakan batas ini, jangan diam-diam melewatinya.

## Audit besar

Untuk audit lintas bab atau menjelang sidang, delegasikan ke subagent
`skripsi-auditor` supaya pembacaan menyeluruh tidak memenuhi konteks utama.
