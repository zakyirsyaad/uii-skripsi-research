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
3. Tanyakan hal yang hanya pengguna yang tahu, lalu isikan ke `.skripsi.yaml`:
   - `project_id` — pengenal proyek yang stabil
   - `mailto` — email untuk polite pool Crossref/OpenAlex. Jelaskan bahwa ini
     dikirim ke API publik sebagai perkenalan, bukan autentikasi, dan tanpa itu
     verifikasi akan lambat. Jangan isi sendiri dari sumber mana pun.
   - `kbbi_db_path` — opsional, jalur SQLite KBBI lokal bila punya
   - `recency_years` — default 5
4. Isi frontmatter `references/thesis-context.md` dengan `project_id` yang sama.
5. Validasi hasilnya:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_references.py`
6. Laporkan apa yang dibuat dan apa langkah berikutnya.

Jangan mengisi keputusan, sumber, atau item terbuka apa pun. Ledger baru harus
kosong sampai pengguna menetapkan isinya.
