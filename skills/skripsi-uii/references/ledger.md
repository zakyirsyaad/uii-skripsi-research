# Disiplin Ledger Konteks

## Kapan checkpoint

Checkpoint seminimal mungkin, dan hanya ketika:

- pengguna secara eksplisit menyetujui, menolak, mengoreksi, atau mengganti
  sebuah keputusan proyek;
- unit drafting yang disetujui mengubah unit aktif, status bab, atau item
  terbuka;
- audit menetapkan status kesiapan atau blocker baru; atau
- serah-terima meninggalkan keputusan atau item belum selesai yang berpengaruh
  material pada tugas berikutnya.

## Kapan JANGAN checkpoint

Jangan simpan sebagai status yang disetujui: opsi brainstorming, usulan
asisten, inferensi, fakta eksternal yang belum terverifikasi, keluaran perkakas
yang sementara, atau "lanjut" yang ambigu.

Jangan menulis ulang ledger hanya untuk memperbarui timestamp ketika tidak ada
yang berubah secara material. Riwayat yang penuh checkpoint kosong menyulitkan
penelusuran perubahan yang sungguhan.

## Yang tidak boleh masuk ledger

Rekaman wawancara, data kontak responden, kredensial, kunci API, seed frase
dompet, atau data sensitif lain yang tidak diperlukan untuk kontinuitas.

## Menjaga riwayat

Tandai entri yang digantikan sebagai `superseded` beserta id penggantinya —
jangan dihapus. Penguji bisa menanyakan mengapa sebuah keputusan berubah, dan
jawabannya harus ada.

## Sinkronisasi Word

Biarkan `word_sync_status` bernilai `unknown` kecuali pengguna menyatakannya
secara eksplisit. **Jangan pernah** menyimpulkannya dari timestamp berkas —
timestamp berubah karena banyak hal yang tidak berarti isinya berubah.

## Saat serah-terima

Sebutkan konteks yang dimuat atau diperbarui **hanya bila memengaruhi hasil**.
Jangan menuangkan seluruh isi ledger ke setiap respons; itu membuat pengguna
berhenti membacanya, dan ledger yang tidak dibaca sama saja dengan tidak ada.

## Membuat ledger baru

Dengan izin menulis berkas, buat ledger ringkas hanya dari keputusan eksplisit
pengguna dan artefak terverifikasi saat ini. Tanpa izin itu, berikan templat
Markdown yang siap tempel. Jangan menulis diam-diam.
