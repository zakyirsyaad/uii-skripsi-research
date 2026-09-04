"""Tes ekspor BibTeX/RIS, terutama penanganan penulis korporat."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "export_mendeley",
    Path(__file__).resolve().parents[1] / "scripts" / "export_mendeley.py",
)
export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export)

from skripsi.ledger import Source  # noqa: E402


def src(**kw):
    base = dict(id="s001", tipe="jurnal", penulis="Nakamoto", tahun=2008,
                judul="Judul", venue="Jurnal X", doi_url="10.1000/x",
                klaim="Klaim", status_verifikasi="verified", tgl_verifikasi="2026-09-01")
    base.update(kw)
    return Source(**base)


class TestCorporateAuthors(unittest.TestCase):
    def test_personal_name_is_not_braced(self):
        out = export.to_bibtex(src(penulis="Nakamoto"))
        self.assertIn("author = {Nakamoto}", out)

    def test_organisation_is_double_braced(self):
        """Tanpa kurung ganda, BibTeX memecah nama organisasi jadi nama orang."""
        out = export.to_bibtex(src(penulis="Badan Pusat Statistik", tipe="institusi"))
        self.assertIn("author = {{Badan Pusat Statistik}}", out)

    def test_organisation_with_and_is_not_split(self):
        out = export.to_bibtex(src(penulis="Ministry of Health and Welfare"))
        self.assertIn("{{Ministry of Health and Welfare}}", out)

    def test_ris_strips_comma_so_mendeley_does_not_invert(self):
        out = export.to_ris(src(penulis="Badan Pusat Statistik, RI", tipe="institusi"))
        self.assertIn("AU  - Badan Pusat Statistik RI", out)


class TestTypeMapping(unittest.TestCase):
    def test_journal_maps_to_article_with_journal_field(self):
        out = export.to_bibtex(src(tipe="jurnal", venue="Jurnal Informatika"))
        self.assertTrue(out.startswith("@article{"))
        self.assertIn("journal = {Jurnal Informatika}", out)

    def test_proceedings_maps_to_inproceedings_with_booktitle(self):
        out = export.to_bibtex(src(tipe="prosiding", venue="Prosiding SNATI"))
        self.assertTrue(out.startswith("@inproceedings{"))
        self.assertIn("booktitle = {Prosiding SNATI}", out)

    def test_article_maps_to_electronic_in_ris(self):
        self.assertIn("TY  - ELEC", export.to_ris(src(tipe="artikel")))

    def test_doi_preferred_over_raw_url(self):
        out = export.to_bibtex(src(doi_url="https://doi.org/10.1000/x"))
        self.assertIn("doi = {10.1000/x}", out)
        self.assertNotIn("url =", out)

    def test_plain_url_used_when_no_doi(self):
        out = export.to_bibtex(src(doi_url="https://bps.go.id/x", tipe="institusi"))
        self.assertIn("url = {https://bps.go.id/x}", out)


class TestCiteKey(unittest.TestCase):
    def test_key_combines_author_and_year(self):
        self.assertEqual("Nakamoto2008", export.cite_key(src()))

    def test_key_strips_punctuation(self):
        self.assertEqual("OReilly2020", export.cite_key(src(penulis="O'Reilly", tahun=2020)))


if __name__ == "__main__":
    unittest.main()
