---
name: skripsi-uii
description: Use at the start of any UII Informatics (S1 Informatika UII) thesis task — loading and reconciling the persistent project context ledger, resolving conflicts between user decisions and verified evidence, choosing a research method that matches the actual study, and routing to the citation, literature, drafting, or audit skills.
---

# Skripsi UII — Inti

Pintu masuk untuk pekerjaan skripsi. Muat konteks, selesaikan konflik, lalu
arahkan ke skill yang tepat.

## Muat konteks lebih dulu

Ledger kontinuitas ada di `references/thesis-context.md`, relatif terhadap root
proyek skripsi. Hook `SessionStart` plugin ini sudah menyuntikkan ringkasannya —
tapi ringkasan bukan isi lengkap. Baca berkasnya sendiri sebelum drafting
substantif, saran metodologi, perubahan cakupan, audit, atau melanjutkan unit
sebelumnya.

Muat hanya keputusan yang status dan provenance-nya jelas. Perlakukan
`proposed`, `unconfirmed`, `rejected`, dan `superseded` sesuai statusnya —
jangan naikkan derajatnya karena kelihatan masuk akal.

Rekonsiliasi ledger dengan permintaan saat ini dan artefak proyek terverifikasi
**sebelum** memakainya. Lanjutkan dari unit aktif dan item terbuka tanpa meminta
pengguna mengulang konteks yang sudah disetujui.

Bila ledger tidak ada, jangan berpura-pura punya kontinuitas. Katakan apa
adanya, lalu tawarkan `/skripsi-init`.

Ledger **bukan bukti ilmiah** dan tidak pernah boleh disitasi.

## Urutan kepercayaan saat konflik

1. Instruksi eksplisit pengguna yang terbaru.
2. Artefak proyek atau rekaman sumber yang terverifikasi saat ini.
3. Entri ledger yang disetujui, dengan provenance teridentifikasi.
4. Konteks percakapan sebelumnya.
5. Inferensi asisten.

Ungkapkan konflik material, jangan diam-diam memilih salah satu.

Keputusan pengguna yang lebih baru boleh menggantikan pilihan proyek
sebelumnya, tapi **tidak** memverifikasi klaim faktual eksternal. Sebaliknya,
bukti terverifikasi yang lebih baru boleh menggantikan rekaman faktual yang
basi, bahkan ketika kalimat lamanya sudah disetujui.

## Empat jenis catatan, jangan dicampur

| Kind | Artinya |
|---|---|
| `factual_claim` | Pernyataan tentang dunia; butuh sumber terverifikasi |
| `user_decision` | Pilihan proyek yang ditetapkan pengguna |
| `assistant_proposal` | Usulanmu; belum berlaku sampai disetujui |
| `inference` | Simpulanmu dari hal lain; bukan bukti |

Status keputusan (`proposed`/`approved`/`rejected`/`superseded`/`unconfirmed`)
dan status bukti (`verified`/`unverified`/`unverifiable`/`mismatch`/
`not_found`/`retracted`) adalah dua sumbu terpisah. Keduanya berbeda isi:
`superseded` sah untuk keputusan, tapi ditolak parser bila ditulis ke
`status_verifikasi`. Usulan yang disetujui menjadi keputusan, bukan
fakta yang terverifikasi.

Jangan mengubah saran, contoh, atau diskusi tentatif menjadi keputusan proyek.

Detail kapan harus checkpoint ada di `references/ledger.md`.

## Memilih metode

Pilih metodologi dari proses penelitian yang **benar-benar akan dijalankan**,
bukan dari kata kunci judul, pilihan teknologi, atau metode skripsi orang lain.

Pisahkan tiga lapis:

1. **Metode penelitian** — bagaimana studi menjawab pertanyaannya dan
   menghasilkan bukti.
2. **Proses pengembangan sistem** — bagaimana artefak dirancang dan dibangun,
   bila ada artefak.
3. **Metode evaluasi** — bagaimana artefak atau hipotesis dinilai.

Sebelum merekomendasikan metode, petakan dulu: aktivitas yang direncanakan,
masukan, keluaran, partisipan atau data, kriteria evaluasi, dan bukti yang
diharapkan. Jelaskan mengapa metode itu cocok dengan aktivitas tersebut.

Tandai rekomendasi sebagai `proposed` sampai pengguna menyetujuinya. Bila
prosesnya belum lengkap, **sebutkan keputusan metodologis yang masih hilang** —
jangan menempelkan label familiar seperti DSRM, R&D, waterfall, agile,
eksperimen, atau studi kasus hanya karena mirip.

## Arahkan ke skill yang tepat

| Kebutuhan | Skill |
|---|---|
| Menambah, memeriksa, mengekspor sitasi; kelayakan sumber; kuota 20% | `skripsi-sitasi` |
| Mencari literatur, menyaring kandidat, celah penelitian | `skripsi-pustaka` |
| Menulis dan merevisi prosa, status unit, impact sweep, bahasa | `skripsi-naskah` |
| Memeriksa kesiapan bab atau sidang | `skripsi-kesiapan` |

## Rujukan lanjutan

- `references/ledger.md` — kapan checkpoint, kapan jangan, dan apa yang tidak
  boleh disimpan.
- `references/format-uii.md` — cara memakai DSpace UII sebagai rujukan kerangka
  tanpa menyalin, dan mengapa ia tidak pernah menjadi sitasi.
