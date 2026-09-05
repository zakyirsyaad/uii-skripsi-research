"""Tes logika pencocokan sitasi. Tanpa jaringan — klien di-stub."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import skripsi.verify as verify_mod  # noqa: E402
from skripsi.sources import NetworkUnavailable, Work  # noqa: E402
from skripsi.verify import (  # noqa: E402
    STATUS_MISMATCH, STATUS_NOT_FOUND, STATUS_OK, STATUS_RETRACTED,
    STATUS_UNVERIFIED, Claim, verify,
)

REAL = Work(
    doi="10.1145/3313831.3376234",
    title="Bitcoin: A Peer-to-Peer Electronic Cash System",
    authors=["Nakamoto"],
    year=2008,
    venue="Whitepaper",
    api="crossref",
)


class FakeClient:
    """Klien stub: kembalikan apa yang diminta tes, atau lempar error jaringan."""

    def __init__(self, by_doi_result=None, search_results=None, raise_network=False):
        self._by_doi = by_doi_result
        self._search = search_results or []
        self._raise = raise_network

    def by_doi(self, doi):
        if self._raise:
            raise NetworkUnavailable("simulasi jaringan mati")
        return self._by_doi

    def search(self, title, author="", year=None, rows=5):
        if self._raise:
            raise NetworkUnavailable("simulasi jaringan mati")
        return self._search


class TestVerifyByDoi(unittest.TestCase):
    def test_matching_doi_is_ok(self):
        claim = Claim(doi=REAL.doi, title=REAL.title, author="Nakamoto", year=2008)
        r = verify(claim, FakeClient(by_doi_result=REAL))
        self.assertEqual(STATUS_OK, r.status)
        self.assertEqual(0, r.exit_code)
        self.assertEqual("verified", r.ledger_status)

    def test_unregistered_doi_is_not_found(self):
        r = verify(Claim(doi="10.9999/tidak-ada"), FakeClient(by_doi_result=None))
        self.assertEqual(STATUS_NOT_FOUND, r.status)
        self.assertEqual(2, r.exit_code)
        self.assertEqual("not_found", r.ledger_status)

    def test_wrong_author_is_mismatch(self):
        claim = Claim(doi=REAL.doi, title=REAL.title, author="Wijaya", year=2008)
        r = verify(claim, FakeClient(by_doi_result=REAL))
        self.assertEqual(STATUS_MISMATCH, r.status)
        self.assertTrue(any(d.field == "penulis" and not d.ok for d in r.diffs))

    def test_year_off_by_one_is_tolerated_as_warning(self):
        claim = Claim(doi=REAL.doi, title=REAL.title, author="Nakamoto", year=2009)
        r = verify(claim, FakeClient(by_doi_result=REAL))
        self.assertEqual(STATUS_OK, r.status)
        year_diff = next(d for d in r.diffs if d.field == "tahun")
        self.assertEqual("warning", year_diff.severity)

    def test_year_off_by_many_is_mismatch(self):
        claim = Claim(doi=REAL.doi, title=REAL.title, author="Nakamoto", year=2015)
        r = verify(claim, FakeClient(by_doi_result=REAL))
        self.assertEqual(STATUS_MISMATCH, r.status)

    def test_retracted_work_is_flagged_even_when_metadata_matches(self):
        retracted = Work(**{**REAL.to_dict(), "is_retracted": True})
        claim = Claim(doi=REAL.doi, title=REAL.title, author="Nakamoto", year=2008)
        r = verify(claim, FakeClient(by_doi_result=retracted))
        self.assertEqual(STATUS_RETRACTED, r.status)
        self.assertTrue(any("DITARIK" in n for n in r.notes))

    def test_corporate_author_matches_without_being_split(self):
        org = Work(doi="10.1/x", title="Statistik Indonesia 2025",
                   authors=["Badan Pusat Statistik"], year=2025)
        claim = Claim(doi="10.1/x", title="Statistik Indonesia 2025",
                      author="Badan Pusat Statistik", year=2025)
        r = verify(claim, FakeClient(by_doi_result=org))
        self.assertEqual(STATUS_OK, r.status)


class TestVerifyByTitle(unittest.TestCase):
    def test_close_title_match_is_ok(self):
        claim = Claim(title="Bitcoin: a peer to peer electronic cash system",
                      author="Nakamoto", year=2008)
        r = verify(claim, FakeClient(search_results=[REAL]))
        self.assertEqual(STATUS_OK, r.status)
        self.assertGreater(r.confidence, 0.9)

    def test_fabricated_title_is_not_found(self):
        """Mode kegagalan utama: judul yang dikarang model."""
        claim = Claim(title="Blockchain crowdfunding framework for Indonesian SMEs",
                      author="Wijaya", year=2023)
        r = verify(claim, FakeClient(search_results=[REAL]))
        self.assertEqual(STATUS_NOT_FOUND, r.status)

    def test_no_candidates_at_all_is_not_found(self):
        r = verify(Claim(title="Judul yang tidak ada"), FakeClient(search_results=[]))
        self.assertEqual(STATUS_NOT_FOUND, r.status)

    def test_picks_best_candidate_not_first(self):
        noise = Work(doi="10.2/y", title="Sesuatu yang lain sama sekali",
                     authors=["Lain"], year=2020)
        claim = Claim(title="Bitcoin: A Peer-to-Peer Electronic Cash System",
                      author="Nakamoto", year=2008)
        r = verify(claim, FakeClient(search_results=[noise, REAL]))
        self.assertEqual(STATUS_OK, r.status)
        self.assertEqual(REAL.doi, r.work.doi)


class TestNetworkFailure(unittest.TestCase):
    def test_network_failure_is_unverified_not_not_found(self):
        """Jaringan mati tidak boleh terbaca sebagai 'sumbernya tidak ada'."""
        r = verify(Claim(doi="10.1/x"), FakeClient(raise_network=True))
        self.assertEqual(STATUS_UNVERIFIED, r.status)
        self.assertEqual("unverified", r.ledger_status)
        self.assertNotEqual(STATUS_NOT_FOUND, r.status)

    def test_network_failure_during_title_search_is_unverified(self):
        r = verify(Claim(title="Apa saja"), FakeClient(raise_network=True))
        self.assertEqual(STATUS_UNVERIFIED, r.status)

    def test_claim_without_doi_or_title_is_unverified(self):
        r = verify(Claim(author="Nakamoto", year=2008), FakeClient())
        self.assertEqual(STATUS_UNVERIFIED, r.status)


if __name__ == "__main__":
    unittest.main()


class TestUnindexedSourceTypes(unittest.TestCase):
    """Halaman institusi dan artikel berita memang tidak diindeks Crossref.

    Menandainya NOT_FOUND berarti menuduh sumber sah sebagai fiktif.

    Jalur UNVERIFIABLE memanggil `url_is_reachable`, yang mengirim HEAD sungguhan
    ke situs sumbernya. Tanpa stub, tes ini menghubungi bps.go.id dan
    kontan.co.id tiap kali dijalankan — melanggar janji "tidak menyentuh
    jaringan" dan membuat hasilnya bergantung koneksi.
    """

    def setUp(self):
        self._asli = verify_mod.url_is_reachable
        verify_mod.url_is_reachable = lambda url, timeout=10: True

    def tearDown(self):
        verify_mod.url_is_reachable = self._asli

    def test_institutional_source_without_doi_is_unverifiable(self):
        from skripsi.verify import STATUS_UNVERIFIABLE
        claim = Claim(title="Statistik UMKM Indonesia 2025",
                      author="Badan Pusat Statistik", year=2025,
                      tipe="institusi", url="https://bps.go.id/x")
        r = verify(claim, FakeClient(search_results=[REAL]))
        self.assertEqual(STATUS_UNVERIFIABLE, r.status)
        self.assertEqual("unverifiable", r.ledger_status)

    def test_news_article_without_doi_is_unverifiable(self):
        from skripsi.verify import STATUS_UNVERIFIABLE
        claim = Claim(title="Tren pendanaan digital UMKM", author="Kontan",
                      year=2025, tipe="artikel", url="https://kontan.co.id/x")
        r = verify(claim, FakeClient(search_results=[]))
        self.assertEqual(STATUS_UNVERIFIABLE, r.status)

    def test_journal_without_doi_still_gets_not_found(self):
        """Untuk jurnal, ketidakhadiran TETAP bukti kuat — jangan dilonggarkan."""
        claim = Claim(title="Blockchain crowdfunding framework for Indonesian SMEs",
                      author="Wijaya", year=2023, tipe="jurnal")
        r = verify(claim, FakeClient(search_results=[REAL]))
        self.assertEqual(STATUS_NOT_FOUND, r.status)

    def test_fake_doi_is_not_found_regardless_of_type(self):
        """DOI palsu adalah bukti kuat apa pun jenis sumbernya."""
        claim = Claim(doi="10.9999/palsu", tipe="institusi",
                      url="https://bps.go.id/x")
        r = verify(claim, FakeClient(by_doi_result=None))
        self.assertEqual(STATUS_NOT_FOUND, r.status)
