---
description: Siapkan artefak proyek skripsi (konfigurasi, ledger konteks, source ledger)
---

Siapkan proyek skripsi di direktori kerja saat ini.

1. Periksa apa yang sudah ada: `.skripsi.yaml`, `references/thesis-context.md`,
   `references/sources.md`. **Jangan timpa berkas yang sudah ada** — laporkan
   dan tanyakan lebih dulu.
2. Untuk yang belum ada, salin dari `${CLAUDE_PLUGIN_ROOT}/templates/`:
   - `templates/skripsi.yaml` → `.skripsi.yaml`
   - `templates/thesis-context.md` → `references/thesis-context.md`
   - `templates/sources.md` → `references/sources.md`
3. Tanyakan hanya yang benar-benar khas proyek ini, lalu isikan ke
   `.skripsi.yaml`:
   - `project_id` — pengenal proyek yang stabil
   - `recency_years` — batas kebaruan sumber empiris, default 5

   **Jangan tanyakan `mailto` maupun `kbbi_db_path`.** Keduanya setelan tingkat
   pengguna yang sudah ditanyakan sekali saat plugin dipasang, dan dibaca
   otomatis dari konfigurasi plugin. Jangan menambahkannya ke `.skripsi.yaml`,
   dan jangan mengisi `mailto` sendiri dari sumber mana pun.

4. **Pastikan KBBI terpasang — init belum selesai tanpa ini.** Jalankan:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kbbi_lookup.py --check "analisa"
   ```

   Bila keluar dengan kode 2 (belum dikonfigurasi), hentikan langkah berikutnya
   dan tawarkan mengunduhnya:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup_kbbi.py
   ```

   Sampaikan lebih dulu bahwa data kamusnya milik Badan Pengembangan dan
   Pembinaan Bahasa, penggunaan komersial dilarang, dan unduhan itu atas nama
   pengguna sendiri. **Jangan jalankan dengan `--yes`** — biarkan pengguna yang
   mengonfirmasi. Setelah selesai, arahkan ke
   `/plugin configure uii-skripsi-research` untuk mengisi jalurnya.

   Tanpa KBBI, kebakuan kata tidak bisa diverifikasi dan naskah berisiko tidak
   sesuai standar. Bila pengguna menolak memasangnya, lanjutkan tetapi katakan
   dengan jelas bahwa validasi bahasa tidak akan tersedia.
5. Isi frontmatter `references/thesis-context.md` dengan `project_id` yang sama.
6. Validasi hasilnya:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_references.py`
7. Laporkan apa yang dibuat, status KBBI, dan langkah berikutnya.

Jangan mengisi keputusan, sumber, atau item terbuka apa pun. Ledger baru harus
kosong sampai pengguna menetapkan isinya.
