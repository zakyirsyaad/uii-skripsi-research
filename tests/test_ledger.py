"""Tes parser ledger. Jalankan: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from skripsi.ledger import parse_context, parse_sources  # noqa: E402

VALID_TABLE = dedent("""\
    # Source Ledger

    Prosa pengantar yang harus diabaikan parser.

    | id | tipe | penulis | tahun | judul | venue | doi_url | klaim | status_verifikasi | tgl_verifikasi |
    |---|---|---|---|---|---|---|---|---|---|
    | s001 | jurnal | Nakamoto | 2008 | Bitcoin | Whitepaper | 10.1000/x | Klaim A | verified | 2026-09-01 |
    | s002 | artikel | Kompas | 2024 | Tren fintech | Kompas.com | https://kompas.com/a | Klaim B | unverified |  |
    """)


class TestParseSources(unittest.TestCase):
    def test_parses_valid_table(self):
        sources, issues = parse_sources(VALID_TABLE)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual(2, len(sources))
        self.assertEqual("s001", sources[0].id)
        self.assertEqual(2008, sources[0].tahun)
        self.assertIs(int, type(sources[0].tahun))
        self.assertEqual("Nakamoto", sources[0].penulis)
        self.assertEqual("verified", sources[0].status_verifikasi)

    def test_reports_line_numbers(self):
        sources, _ = parse_sources(VALID_TABLE)
        # baris tabel pertama ada di baris ke-7 (1-indexed)
        self.assertEqual(7, sources[0].line)

    def test_classifies_academic_vs_article(self):
        sources, _ = parse_sources(VALID_TABLE)
        self.assertTrue(sources[0].is_academic)
        self.assertFalse(sources[1].is_academic)

    def test_rejects_unknown_tipe_with_line_number(self):
        bad = VALID_TABLE.replace("| s001 | jurnal |", "| s001 | koran |")
        _, issues = parse_sources(bad)
        errs = [i for i in issues if i.severity == "error"]
        self.assertEqual(1, len(errs))
        self.assertEqual("tipe", errs[0].field)
        self.assertEqual(7, errs[0].line)
        self.assertIn("koran", errs[0].message)

    def test_rejects_unknown_status(self):
        bad = VALID_TABLE.replace("| verified |", "| oke |")
        _, issues = parse_sources(bad)
        self.assertTrue(any(i.field == "status_verifikasi" for i in issues))

    def test_rejects_non_iso_date(self):
        bad = VALID_TABLE.replace("2026-09-01", "01/09/2026")
        _, issues = parse_sources(bad)
        self.assertTrue(any(i.field == "tgl_verifikasi" for i in issues))

    def test_rejects_bad_year(self):
        bad = VALID_TABLE.replace("| 2008 |", "| dua ribu delapan |")
        sources, issues = parse_sources(bad)
        self.assertTrue(any(i.field == "tahun" for i in issues))
        self.assertIsNone(sources[0].tahun)

    def test_rejects_missing_column(self):
        bad = VALID_TABLE.replace(" | tgl_verifikasi |", " |")
        _, issues = parse_sources(bad)
        errs = [i for i in issues if i.severity == "error"]
        self.assertTrue(errs)
        self.assertIn("tgl_verifikasi", errs[0].message)

    def test_rejects_reordered_columns(self):
        bad = VALID_TABLE.replace("| id | tipe |", "| tipe | id |")
        _, issues = parse_sources(bad)
        self.assertTrue([i for i in issues if i.severity == "error"])

    def test_missing_table_is_an_error_not_a_crash(self):
        sources, issues = parse_sources("# Kosong\n\nTidak ada tabel.\n")
        self.assertEqual([], sources)
        self.assertTrue([i for i in issues if i.severity == "error"])

    def test_header_only_table_is_valid_and_empty(self):
        header_only = "\n".join(VALID_TABLE.splitlines()[:6]) + "\n"
        sources, issues = parse_sources(header_only)
        self.assertEqual([], sources)
        self.assertEqual([], [i for i in issues if i.severity == "error"])

    def test_preserves_escaped_pipe_in_claim(self):
        piped = VALID_TABLE.replace("| Klaim A |", r"| Throughput A \| B |")
        sources, issues = parse_sources(piped)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual("Throughput A | B", sources[0].klaim)

    def test_flags_duplicate_ids(self):
        dup = VALID_TABLE.replace("| s002 |", "| s001 |")
        _, issues = parse_sources(dup)
        self.assertTrue(any("s001" in i.message and i.field == "id" for i in issues))


VALID_CONTEXT = dedent("""\
    ---
    schema_version: 1
    project_id: skripsi-uii
    last_checkpoint_at: "2026-09-01"
    word_sync_status: unknown
    active_unit: "Bab 3 paragraf 4"
    ---

    # Konteks

    ## Keputusan

    | id | kind | pernyataan | status | provenance | scope | pengganti |
    |---|---|---|---|---|---|---|
    | d001 | user_decision | Pakai DSRM | approved | Percakapan 2026-09-01 | Bab 3 | |
    | d002 | assistant_proposal | Pakai waterfall | superseded | Usulan asisten | Bab 3 | d001 |

    ## Item terbuka

    - [ ] Konfirmasi jumlah responden
    - [x] Sudah selesai

    ## Artefak

    | peran | path |
    |---|---|
    | source ledger | references/sources.md |
    """)


class TestParseContext(unittest.TestCase):
    def test_parses_frontmatter(self):
        ctx, issues = parse_context(VALID_CONTEXT)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual("skripsi-uii", ctx.project_id)
        self.assertEqual("unknown", ctx.word_sync_status)
        self.assertEqual("Bab 3 paragraf 4", ctx.active_unit)

    def test_parses_decisions(self):
        ctx, _ = parse_context(VALID_CONTEXT)
        self.assertEqual(2, len(ctx.decisions))
        self.assertEqual("approved", ctx.decisions[0].status)
        self.assertEqual("d001", ctx.decisions[1].pengganti)

    def test_parses_only_unchecked_open_items(self):
        ctx, _ = parse_context(VALID_CONTEXT)
        self.assertEqual(["Konfirmasi jumlah responden"],
                         [i.item for i in ctx.open_items])
        self.assertEqual(2, len(ctx.items))  # yang selesai tetap tercatat

    def test_parses_artifacts(self):
        ctx, _ = parse_context(VALID_CONTEXT)
        self.assertEqual("references/sources.md", ctx.artifacts["source ledger"])

    def test_missing_frontmatter_is_an_error(self):
        _, issues = parse_context("# Tanpa frontmatter\n")
        self.assertTrue([i for i in issues if i.severity == "error"])

    def test_rejects_unknown_decision_status(self):
        bad = VALID_CONTEXT.replace("| approved |", "| mantap |")
        _, issues = parse_context(bad)
        self.assertTrue(any(i.field == "status" for i in issues))

    def test_rejects_unknown_kind(self):
        bad = VALID_CONTEXT.replace("user_decision", "tebakan")
        _, issues = parse_context(bad)
        self.assertTrue(any(i.field == "kind" for i in issues))

    def test_word_sync_defaults_to_unknown_when_absent(self):
        bare = VALID_CONTEXT.replace("word_sync_status: unknown\n", "")
        ctx, _ = parse_context(bare)
        self.assertEqual("unknown", ctx.word_sync_status)

    def test_context_without_optional_sections_still_parses(self):
        minimal = dedent("""\
            ---
            schema_version: 1
            project_id: p
            ---

            # Konteks
            """)
        ctx, issues = parse_context(minimal)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual([], ctx.decisions)
        self.assertEqual([], ctx.open_items)


if __name__ == "__main__":
    unittest.main()


class TestUpdateSourceRows(unittest.TestCase):
    def test_writes_status_and_date_back(self):
        from skripsi.ledger import update_source_rows
        out = update_source_rows(VALID_TABLE, {"s002": ("verified", "2026-09-05")})
        sources, issues = parse_sources(out)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual("verified", sources[1].status_verifikasi)
        self.assertEqual("2026-09-05", sources[1].tgl_verifikasi)

    def test_leaves_other_columns_untouched(self):
        from skripsi.ledger import update_source_rows
        out = update_source_rows(VALID_TABLE, {"s001": ("mismatch", "2026-09-05")})
        sources, _ = parse_sources(out)
        self.assertEqual("Nakamoto", sources[0].penulis)
        self.assertEqual("Klaim A", sources[0].klaim)
        self.assertEqual(2008, sources[0].tahun)
        self.assertEqual("s002", sources[1].id)
        self.assertEqual("unverified", sources[1].status_verifikasi)

    def test_roundtrips_escaped_pipe(self):
        from skripsi.ledger import update_source_rows
        piped = VALID_TABLE.replace("| Klaim A |", r"| Throughput A \| B |")
        out = update_source_rows(piped, {"s001": ("verified", "2026-09-05")})
        sources, issues = parse_sources(out)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual("Throughput A | B", sources[0].klaim)

    def test_unknown_id_is_a_noop(self):
        from skripsi.ledger import update_source_rows
        out = update_source_rows(VALID_TABLE, {"s999": ("verified", "2026-09-05")})
        self.assertEqual(VALID_TABLE, out)


TABLE_CONTEXT = dedent("""\
    ---
    schema_version: 1
    project_id: uji
    active_workstream: BAB II
    active_unit: 2.3 Blockchain dan Ethereum
    active_unit_status: awaiting_review
    active_markdown_artifact: unavailable
    ---

    ## Item terbuka

    | ID | Item | Status | Dampak |
    |---|---|---|---|
    | O-001 | Metadata Mendeley sudah diselaraskan | resolved | BAB II |
    | O-002 | Pastikan penomoran Tabel 2.2 | open | Konsistensi BAB II |
    | O-003 | Verifikasi sumber Gambar 2.1 | open | Keterlacakan BAB II |
    | O-004 | Cakupan lama sebelum objek berubah | superseded | BAB I |
    """)


class TestStatusTrackedItems(unittest.TestCase):
    """Bentuk tabel berstatus lebih kaya daripada checkbox dan harus didukung."""

    def test_parses_all_items_with_status(self):
        ctx, issues = parse_context(TABLE_CONTEXT)
        self.assertEqual([], [i for i in issues if i.severity == "error"])
        self.assertEqual(4, len(ctx.items))
        self.assertEqual("O-001", ctx.items[0].id)
        self.assertEqual("resolved", ctx.items[0].status)
        self.assertEqual("Konsistensi BAB II", ctx.items[1].dampak)

    def test_open_items_excludes_resolved_and_superseded(self):
        ctx, _ = parse_context(TABLE_CONTEXT)
        self.assertEqual(["O-002", "O-003"], [i.id for i in ctx.open_items])

    def test_extra_frontmatter_fields_are_kept(self):
        ctx, _ = parse_context(TABLE_CONTEXT)
        self.assertEqual("BAB II", ctx.active_workstream)
        self.assertEqual("awaiting_review", ctx.active_unit_status)
        self.assertEqual("unavailable", ctx.active_artifact)

    def test_unknown_item_status_is_reported(self):
        bad = TABLE_CONTEXT.replace("| open | Konsistensi", "| beres | Konsistensi")
        _, issues = parse_context(bad)
        self.assertTrue(any(i.field == "status" for i in issues))

    def test_unknown_unit_status_is_reported(self):
        bad = TABLE_CONTEXT.replace("awaiting_review", "lagi-dikerjakan")
        _, issues = parse_context(bad)
        self.assertTrue(any(i.field == "active_unit_status" for i in issues))

    def test_checked_checkbox_is_recorded_as_resolved(self):
        ctx, _ = parse_context(VALID_CONTEXT)
        done = [i for i in ctx.items if i.status == "resolved"]
        self.assertEqual(["Sudah selesai"], [i.item for i in done])
