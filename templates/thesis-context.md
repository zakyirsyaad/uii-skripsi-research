---
schema_version: 1
project_id: skripsi-informatika-uii
last_checkpoint_at: ""
last_checkpoint_source: ""
word_sync_status: unknown
active_unit: ""
active_unit_status: ""
active_artifact: ""
active_workstream: ""
---

# Konteks Skripsi

Ledger kontinuitas antar-sesi. **Bukan bukti ilmiah** — tidak pernah boleh
disitasi di dalam skripsi. Isinya hanya keputusan eksplisit dan status
material, bukan brainstorming atau usulan yang belum disetujui.

## Keputusan

`kind`: `factual_claim` | `user_decision` | `assistant_proposal` | `inference`
`status`: `proposed` | `approved` | `rejected` | `superseded` | `unconfirmed`

`active_unit_status` di frontmatter memakai daftar sendiri: `draft`,
`awaiting_review`, `approved`, `revision_requested`, `superseded`. Hook
SessionStart menampilkannya di samping unit aktif.

Status keputusan dan status bukti adalah dua sumbu terpisah: persetujuanmu atas
sebuah paragraf mengesahkan kata-katanya, bukan kebenaran klaim di dalamnya.
Klaim faktual tetap harus menunjuk ke `references/sources.md`.

| id | kind | pernyataan | status | provenance | scope | pengganti |
|---|---|---|---|---|---|---|
| d001 | user_decision | Contoh: ganti baris ini dengan keputusanmu sendiri | approved | Contoh: percakapan tanggal berapa, disetujui siapa | Bab berapa | |

## Item terbuka

- [ ] Contoh: konfirmasi jumlah responden pengujian usability ke pembimbing

## Artefak

| peran | path |
|---|---|
| source ledger | references/sources.md |
| bab aktif | naskah/bab3.md |

## Riwayat checkpoint

Entri yang digantikan ditandai `superseded` di tabel keputusan, tidak dihapus.
