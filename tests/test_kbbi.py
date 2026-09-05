"""Tes deteksi kebakuan. Basis data sintetis — tanpa jaringan, tanpa unduhan."""
import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

_spec = importlib.util.spec_from_file_location(
    "kbbi_lookup", ROOT / "scripts" / "kbbi_lookup.py")
kbbi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kbbi)

# Bentuk entri persis seperti di data KBBI Edisi IV yang beredar: bentuk tidak
# baku dicatat sebagai lema tersendiri yang hanya merujuk ke bentuk bakunya,
# dan tanda panah aslinya sudah rusak menjadi "?".
ROWS = [
    ("analisis", "ana·li·sis n penyelidikan terhadap suatu peristiwa", 1),
    ("analisa", "ana·li·sa ? analisis", 1),
    ("praktik", "prak·tik n pelaksanaan secara nyata", 1),
    ("praktek", "prak·tek ? praktik", 1),
    ("praktek", "prak.tek Lihat praktik", 2),
    ("obyek", "ob·yek /obyék/ ? objek", 1),
    # Lema dengan makna sendiri DI SAMPING rujukan silang tetap sah.
    ("bisa", "bi·sa n zat racun dari ular", 1),
    ("bisa", "bi·sa ? dapat", 1),
    # Sebagian dump menyimpan lema dengan spasi di belakang.
    ("metode ", "me·to·de n cara teratur yang digunakan", 1),
]


class KbbiCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / "kbbi.sqlite"
        conn = sqlite3.connect(cls.db)
        conn.execute('CREATE TABLE dictionary (word TEXT, arti TEXT, "type" INTEGER)')
        conn.executemany("INSERT INTO dictionary VALUES (?,?,?)", ROWS)
        conn.commit(); conn.close()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, word):
        conn = sqlite3.connect(f"file:{self.db}?mode=ro", uri=True)
        try:
            schema = kbbi.discover_schema(conn)
            return kbbi.classify(kbbi.lookup(conn, schema, word))
        finally:
            conn.close()


class TestStandardForm(unittest.TestCase):
    def test_arrow_crossref_yields_standard_form(self):
        self.assertEqual("analisis", kbbi.standard_form("ana·li·sa ? analisis"))

    def test_lihat_crossref_yields_standard_form(self):
        self.assertEqual("praktik", kbbi.standard_form("prak.tek Lihat praktik"))

    def test_crossref_with_pronunciation_is_handled(self):
        self.assertEqual("objek", kbbi.standard_form("ob·yek /obyék/ ? objek"))

    def test_real_definition_is_not_a_crossref(self):
        self.assertIsNone(kbbi.standard_form("ana·li·sis n penyelidikan terhadap"))

    def test_question_mark_inside_a_definition_is_not_a_crossref(self):
        self.assertIsNone(kbbi.standard_form("ta·nya v apa kabar? sapaan sehari-hari"))


class TestClassify(KbbiCase):
    def test_standard_word_passes(self):
        self.assertEqual(("baku", ""), self.check("analisis"))

    def test_nonstandard_word_is_flagged_with_its_standard_form(self):
        """Inti perbaikannya: `analisa` ADA di KBBI, tapi tidak baku."""
        self.assertEqual(("tidak_baku", "analisis"), self.check("analisa"))

    def test_nonstandard_word_with_multiple_crossref_entries(self):
        status, baku = self.check("praktek")
        self.assertEqual("tidak_baku", status)
        self.assertEqual("praktik", baku)

    def test_word_absent_from_kbbi(self):
        self.assertEqual(("tidak_ada", ""), self.check("kwalitas"))

    def test_word_with_own_meaning_beside_a_crossref_stays_valid(self):
        """Satu entri berdefinisi sungguhan sudah cukup membuat lema itu sah."""
        self.assertEqual(("baku", ""), self.check("bisa"))

    def test_trailing_space_in_stored_lemma_still_matches(self):
        self.assertEqual(("baku", ""), self.check("metode"))

    def test_lookup_is_case_insensitive(self):
        self.assertEqual(("baku", ""), self.check("ANALISIS"))


if __name__ == "__main__":
    unittest.main()
