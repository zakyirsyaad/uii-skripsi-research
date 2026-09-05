# Batas Pemeriksaan KBBI

Dibaca saat memutuskan seberapa jauh keluaran `kbbi_lookup.py` boleh dipercaya.

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
bentuk bakunya: `analisa ? analisis`, `praktek Lihat praktik`. Karena itu
"ketemu di kamus" tidak membuktikan apa pun.

`kbbi_lookup.py --check` sudah mendeteksi rujukan silang ini dan melaporkan tiga
keadaan: `baku`, `TIDAK BAKU -> pakai: X`, atau `TIDAK ADA`. Percayai keluarannya,
jangan menilai ulang dari ingatan.

### Batas basis data KBBI

Yang sahih hanya pemeriksaan **ada/tidaknya lema di kamus utama**, turunan KBBI
Edisi IV. Basis data yang beredar juga memuat tabel pasangan baku/tidak-baku,
sinonim, dan antonim yang **sebagian dihasilkan AI**; jangan perlakukan tabel itu
sebagai otoritas. Untuk kasus yang menentukan, KBBI Daring resmi tetap rujukannya.

## Kenapa tidak boleh menebak

Ejaan bahasa Indonesia justru bidang yang sering salah diingat model. Bentuk
tidak baku seperti `analisa`, `praktek`, dan `obyek` terasa benar karena sangat
lazim dipakai sehari-hari, dan ketiganya memang ada di KBBI, hanya sebagai
rujukan ke bentuk bakunya.

Menebak di sini bukan sekadar berisiko salah; ia salah dengan cara yang
terdengar meyakinkan.
