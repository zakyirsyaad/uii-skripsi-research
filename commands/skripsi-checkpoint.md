---
description: Simpan keputusan atau perubahan status material ke ledger konteks
argument-hint: "[apa yang perlu disimpan]"
---

Checkpoint ke `references/thesis-context.md`: $ARGUMENTS

Sebelum menulis apa pun, pastikan yang akan disimpan memang layak:

**Layak** — pengguna secara eksplisit menyetujui, menolak, mengoreksi, atau
mengganti keputusan proyek; unit drafting yang disetujui mengubah unit aktif
atau status bab; audit menetapkan blocker atau status kesiapan baru; atau ada
serah-terima dengan item belum selesai yang berpengaruh material.

**Tidak layak** — opsi brainstorming, usulanmu sendiri, inferensi, fakta
eksternal yang belum terverifikasi, keluaran perkakas sementara, atau "lanjut"
yang ambigu. Bila yang diminta termasuk kategori ini, katakan dan jangan tulis.

Saat menulis:

1. Isi `kind` dengan tepat: `factual_claim`, `user_decision`,
   `assistant_proposal`, atau `inference`. Jangan mencatat usulanmu sebagai
   keputusan pengguna.
2. Isi `provenance` — tanpa ini entri tidak bisa dipercaya di sesi berikutnya.
3. Untuk keputusan yang menggantikan yang lama: tandai yang lama `superseded`
   dan isi kolom penggantinya. **Jangan hapus** — penguji bisa menanyakan
   mengapa sebuah keputusan berubah.
4. Perbarui `last_checkpoint_at` dan `active_unit` bila memang berubah.
5. Biarkan `word_sync_status` tetap `unknown` kecuali pengguna menyatakannya.
6. Jangan simpan rekaman wawancara, kontak responden, kredensial, atau data
   sensitif lain.

Bila tidak ada yang berubah secara material, katakan dan jangan tulis ulang
ledger hanya untuk memperbarui timestamp.
