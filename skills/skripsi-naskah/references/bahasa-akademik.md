# Ragam Bahasa Akademik Indonesia

## Baku, bukan sekadar terdengar ilmiah

Kesalahan tersering pada skripsi Informatika adalah bentuk tidak baku yang
terlanjur lazim di industri. Periksa dengan `kbbi_lookup.py`, jangan dari
ingatan — daftar ini contoh, bukan penggantinya:

| Tidak baku | Baku |
|---|---|
| analisa | analisis |
| sistim | sistem |
| praktek | praktik |
| resiko | risiko |
| standarisasi | standardisasi |
| kwalitas | kualitas |
| obyek | objek |
| jadual | jadwal |

Kedelapan pasangan di atas **sudah diverifikasi terhadap KBBI Edisi IV**
(115.978 lema) pada 2026-09-05, bukan ditulis dari ingatan. `analisa`,
`sistim`, `praktek`, dan `obyek` ada di KBBI sebagai rujukan silang ke bentuk
bakunya; `resiko`, `standarisasi`, `kwalitas`, dan `jadual` tidak ada sama
sekali.

Karena itu memakai tabel ini untuk kedelapan kata tersebut **sah**. Untuk kata
di luar daftar, jalankan `kbbi_lookup.py` — daftar ini tidak pernah menjadi
alasan menebak.

Istilah teknis asing yang belum punya padanan baku ditulis miring pada
kemunculan pertama, lalu konsisten. Jangan memaksakan padanan yang tidak dikenal
pembaca — konsistensi lebih penting daripada kemurnian.

## Kalimat

- Kalimat pasif lazim di ragam akademik Indonesia, tapi jangan sampai
  menghilangkan pelaku ketika pelakunya penting. "Data dianalisis" boleh;
  "kesalahan telah terjadi" menyembunyikan siapa yang keliru.
- Satu gagasan per kalimat. Kalimat bertingkat tiga klausa hampir selalu bisa
  dipecah tanpa kehilangan makna.
- Hindari intensifier tanpa isi: "sangat penting", "sangat signifikan". Bila
  memang signifikan, tunjukkan angkanya.

## Jangan menulis sok-berat

Ini kesalahan paling umum pada skripsi S1, dan paling merugikan. Mahasiswa
mengira makin berat bahasanya makin ilmiah, lalu menulis kalimat yang pengujinya
sendiri harus baca dua kali.

Penguji menilai apakah gagasanmu terbaca. Kalimat yang sulit dibaca tidak
terlihat pintar — ia terlihat seperti penulis yang belum yakin dengan
gagasannya.

### Kata kerja, bukan kata benda

Bahasa Indonesia akademik gampang membengkak karena kata kerja diubah jadi
kata benda. Kembalikan jadi kata kerja:

| Membengkak | Langsung |
|---|---|
| melakukan analisis terhadap data | menganalisis data |
| melakukan pengujian terhadap sistem | menguji sistem |
| memberikan pengaruh terhadap kinerja | memengaruhi kinerja |
| melakukan implementasi | mengimplementasikan |
| mengadakan perbandingan antara | membandingkan |

### Buang frasa yang tidak membawa apa-apa

Frasa ini bisa dihapus tanpa mengubah makna kalimat sama sekali:

- "dapat dikatakan bahwa"
- "pada dasarnya", "pada hakikatnya"
- "dalam rangka untuk" → cukup "untuk"
- "sebagaimana yang telah dijelaskan sebelumnya" → "seperti dijelaskan di atas"
- "hal ini menunjukkan bahwa" → "ini menunjukkan"
- "berdasarkan pada" → "berdasarkan"

Uji cepat: hapus frasanya, lalu baca ulang kalimatnya. Kalau maknanya tetap,
frasa itu memang tidak perlu.

### Pecah kalimat bertingkat

Berat:

> Berdasarkan hasil pengujian yang telah dilakukan terhadap sistem crowdfunding
> berbasis smart contract yang dikembangkan dalam penelitian ini, dapat
> dikatakan bahwa sistem tersebut pada dasarnya telah mampu memberikan
> kemudahan bagi pengguna dalam melakukan proses pendanaan proyek.

Ringan:

> Hasil pengujian menunjukkan pengguna dapat mendanai proyek melalui sistem ini
> tanpa hambatan berarti.

Yang kedua lebih pendek, lebih jelas, dan **klaimnya lebih jujur** — ia tidak
lagi menyembunyikan kekosongan bukti di balik "dapat dikatakan bahwa".

### Berapa panjang yang wajar

Contoh di atas dipangkas jauh untuk menunjukkan bedanya. Jangan jadikan
panjangnya sebagai target.

Pengukuran atas skripsi Informatika UII yang sudah lolos sidang menunjukkan
ragam yang sebenarnya diterima:

| | Angka |
|---|---|
| Rata-rata panjang kalimat | **19–23 kata** |
| Median | 18–21 kata |
| Kalimat di atas 25 kata | 21–35% |
| Kalimat di atas 35 kata | 6–13% |

Jadi sasarannya **sekitar 20 kata**, bukan 13. Kalimat panjang boleh ada, asal
tidak mendominasi. Prosa yang seluruhnya di bawah 15 kata justru terbaca
patah-patah dan tidak seperti skripsi.

Yang perlu dipangkas adalah kalimat 35 kata ke atas, terutama yang bertingkat
tiga klausa. Bukan setiap kalimat panjang.

Ukur naskahmu sendiri dengan `analisis_dspace.py`, lalu bandingkan dengan
rentang di atas.

### Batasnya

Sederhana bukan berarti seadanya. Istilah teknis yang memang tepat tetap
dipakai — `smart contract` tidak perlu diganti "kontrak pintar" kalau bidangmu
memakai istilah aslinya. Yang dibuang adalah kerumitan yang tidak menambah
makna, bukan ketelitiannya.

## Klaim harus sepadan dengan bukti

Sesuaikan kekuatan kata kerja dengan kekuatan bukti:

| Bukti | Kata yang tepat |
|---|---|
| Satu studi, konteks terbatas | "menunjukkan", "mengindikasikan" |
| Beberapa studi sejalan | "menunjukkan secara konsisten" |
| Hasil bertentangan | "masih diperdebatkan", "belum konklusif" |
| Belum ada bukti langsung | "diduga", "berpotensi" — dan tandai sebagai inferensi |

"Membuktikan" hampir tidak pernah tepat untuk satu penelitian S1.

## Konsistensi terminologi

Satu konsep, satu istilah, sepanjang naskah. Bila istilah berubah di tengah —
misalnya "pengguna" menjadi "pemakai" — itu bukan variasi gaya, itu cacat yang
akan ditanyakan penguji. Perubahan istilah setelah ada bab yang disetujui
memicu impact sweep.
