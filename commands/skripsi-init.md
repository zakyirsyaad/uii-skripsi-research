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
   otomatis dari konfigurasi plugin. Bila `audit_references.py` mengeluh
   `mailto` kosong, arahkan ke `/plugin configure uii-skripsi-research` —
   jangan menambahkannya ke `.skripsi.yaml`, dan jangan mengisinya sendiri dari
   sumber mana pun.
4. Isi frontmatter `references/thesis-context.md` dengan `project_id` yang sama.
5. Validasi hasilnya:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_references.py`
6. Laporkan apa yang dibuat dan apa langkah berikutnya.

Jangan mengisi keputusan, sumber, atau item terbuka apa pun. Ledger baru harus
kosong sampai pengguna menetapkan isinya.
