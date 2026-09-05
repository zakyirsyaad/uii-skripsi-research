"""Tes parser YAML minimal. Menggantikan ketergantungan PyYAML."""
import sys
import unittest
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from skripsi.minyaml import MiniYamlError, safe_load  # noqa: E402


class TestScalars(unittest.TestCase):
    def test_parses_strings_numbers_bools(self):
        d = safe_load(dedent("""\
            project_id: skripsi-uii
            recency_years: 5
            article_cap_ratio: 0.20
            aktif: true
            nonaktif: false
        """))
        self.assertEqual("skripsi-uii", d["project_id"])
        self.assertEqual(5, d["recency_years"])
        self.assertIs(int, type(d["recency_years"]))
        self.assertAlmostEqual(0.20, d["article_cap_ratio"])
        self.assertIs(True, d["aktif"])
        self.assertIs(False, d["nonaktif"])

    def test_empty_value_is_none(self):
        self.assertIsNone(safe_load("mailto:\n")["mailto"])

    def test_quoted_string_keeps_content(self):
        d = safe_load('last_checkpoint_at: "2026-09-01"\n')
        self.assertEqual("2026-09-01", d["last_checkpoint_at"])
        self.assertIs(str, type(d["last_checkpoint_at"]))

    def test_quoted_empty_string_is_not_none(self):
        self.assertEqual("", safe_load('mailto: ""\n')["mailto"])

    def test_value_containing_colon(self):
        d = safe_load("active_unit: Bab 3: paragraf 4\n")
        self.assertEqual("Bab 3: paragraf 4", d["active_unit"])

    def test_path_value_survives(self):
        d = safe_load("kbbi_db_path: ~/data/kbbi.sqlite\n")
        self.assertEqual("~/data/kbbi.sqlite", d["kbbi_db_path"])


class TestComments(unittest.TestCase):
    def test_full_line_and_trailing_comments_ignored(self):
        d = safe_load(dedent("""\
            # komentar penuh
            recency_years: 5   # batas kebaruan
        """))
        self.assertEqual({"recency_years": 5}, d)

    def test_hash_inside_quotes_is_kept(self):
        d = safe_load('project_id: "skripsi #1"\n')
        self.assertEqual("skripsi #1", d["project_id"])


class TestUnsupportedIsLoudNotSilent(unittest.TestCase):
    """Yang tidak didukung harus bersuara — bukan hilang diam-diam."""

    def test_nested_mapping_raises_with_line_number(self):
        with self.assertRaises(MiniYamlError) as cm:
            safe_load("owner:\n  name: zaky\n")
        self.assertEqual(2, cm.exception.line)

    def test_list_raises(self):
        with self.assertRaises(MiniYamlError):
            safe_load("plugins:\n- satu\n")

    def test_multiline_block_raises(self):
        with self.assertRaises(MiniYamlError):
            safe_load("description: |\n  baris satu\n")

    def test_duplicate_key_raises(self):
        with self.assertRaises(MiniYamlError):
            safe_load("mailto: a@b.c\nmailto: d@e.f\n")

    def test_garbage_line_raises(self):
        with self.assertRaises(MiniYamlError):
            safe_load("ini bukan yaml sama sekali\n")


class TestRealFiles(unittest.TestCase):
    def test_parses_shipped_config_template(self):
        root = Path(__file__).resolve().parents[1]
        d = safe_load((root / "templates" / "skripsi.yaml").read_text(encoding="utf-8"))
        self.assertIn("project_id", d)
        self.assertEqual(5, d["recency_years"])

    def test_parses_shipped_context_frontmatter(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "templates" / "thesis-context.md").read_text(encoding="utf-8")
        fm = text.split("---")[1]
        d = safe_load(fm)
        self.assertIn("project_id", d)
        self.assertEqual("unknown", d["word_sync_status"])


if __name__ == "__main__":
    unittest.main()
