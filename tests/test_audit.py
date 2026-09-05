"""Tes audit daftar pustaka. Murni aritmetika, tanpa jaringan."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from skripsi.audit import VERDICT_NOT_READY, VERDICT_READY, audit_sources  # noqa: E402
from skripsi.config import Config  # noqa: E402
from skripsi.ledger import Source  # noqa: E402

CFG = Config(recency_years=5, article_cap_ratio=0.20)


# Judul harus benar-benar berbeda satu sama lain: judul yang hanya beda satu
# angka mirip >90% dan akan menyalakan detektor duplikat, mengaburkan tes lain.
TITLES = [
    "Analisis performa jaringan sensor nirkabel",
    "Deteksi anomali lalu lintas data memakai autoencoder",
    "Evaluasi usability aplikasi pertanian presisi",
    "Optimasi penjadwalan kontainer pada klaster tepi",
    "Model prediksi gagal panen berbasis citra satelit",
    "Klasifikasi sentimen ulasan produk berbahasa Indonesia",
    "Arsitektur mikroservis untuk sistem rekam medis",
    "Kompresi model bahasa untuk perangkat bergerak",
    "Tata kelola data pribadi pada layanan publik digital",
    "Verifikasi formal protokol konsensus terdistribusi",
    "Segmentasi citra medis dengan transformer",
    "Pengujian ketahanan sistem pembayaran daring",
]


def src(i, tipe="jurnal", tahun=2024, status="verified", **kw):
    return Source(
        id=f"s{i:03d}", tipe=tipe, penulis="Penulis", tahun=tahun,
        judul=kw.pop("judul", TITLES[i % len(TITLES)]),
        venue=kw.pop("venue", "Jurnal X"),
        doi_url=kw.pop("doi_url", f"10.1000/contoh.{i}"),
        klaim="Klaim", status_verifikasi=status, tgl_verifikasi="2026-09-01",
        line=10 + i, **kw,
    )


class TestArticleCap(unittest.TestCase):
    def test_within_cap_passes(self):
        # 10 sumber, kuota floor(10*0.2)=2, ada 2 artikel → aman
        sources = [src(i) for i in range(8)] + [src(i, tipe="artikel") for i in range(8, 10)]
        rep = audit_sources(sources, CFG, ref_year=2026)
        self.assertEqual(2, rep.article_cap)
        self.assertEqual([], [f for f in rep.blockers if f.code == "article_cap"])

    def test_over_cap_is_a_blocker(self):
        # 12 sumber, kuota floor(12*0.2)=2, ada 4 artikel → melanggar
        sources = [src(i) for i in range(8)] + [src(i, tipe="artikel") for i in range(8, 12)]
        rep = audit_sources(sources, CFG, ref_year=2026)
        self.assertEqual(2, rep.article_cap)
        self.assertEqual(4, rep.articles)
        self.assertEqual(VERDICT_NOT_READY, rep.verdict)
        self.assertEqual(1, rep.exit_code)
        cap = next(f for f in rep.blockers if f.code == "article_cap")
        self.assertIn("Kurangi 2 artikel", cap.message)

    def test_institusi_counts_as_academic_not_article(self):
        sources = [src(i) for i in range(9)] + [src(9, tipe="institusi")]
        rep = audit_sources(sources, CFG, ref_year=2026)
        self.assertEqual(10, rep.academic)
        self.assertEqual(0, rep.articles)


class TestVerificationStatus(unittest.TestCase):
    def test_not_found_is_a_blocker(self):
        rep = audit_sources([src(0, status="not_found")], CFG, ref_year=2026)
        self.assertEqual(VERDICT_NOT_READY, rep.verdict)
        self.assertTrue(any("fiktif" in f.message for f in rep.blockers))

    def test_retracted_is_a_blocker(self):
        rep = audit_sources([src(0, status="retracted")], CFG, ref_year=2026)
        self.assertTrue(any(f.code == "status_retracted" for f in rep.blockers))

    def test_unverified_is_only_a_warning(self):
        rep = audit_sources([src(0, status="unverified")], CFG, ref_year=2026)
        self.assertEqual([], rep.blockers)
        self.assertTrue(any(f.code == "status_unverified" for f in rep.warnings))


class TestRecency(unittest.TestCase):
    def test_old_journal_is_flagged(self):
        rep = audit_sources([src(0, tahun=2010)], CFG, ref_year=2026)
        self.assertTrue(any(f.code == "recency" for f in rep.warnings))

    def test_old_book_is_exempt(self):
        rep = audit_sources([src(0, tipe="buku", tahun=1975)], CFG, ref_year=2026)
        self.assertEqual([], [f for f in rep.warnings if f.code == "recency"])

    def test_old_standard_is_exempt(self):
        rep = audit_sources([src(0, tipe="standar", tahun=1998)], CFG, ref_year=2026)
        self.assertEqual([], [f for f in rep.warnings if f.code == "recency"])


class TestCompleteness(unittest.TestCase):
    def test_missing_link_is_flagged(self):
        rep = audit_sources([src(0, doi_url="")], CFG, ref_year=2026)
        self.assertTrue(any(f.code == "missing_link" for f in rep.warnings))

    def test_duplicate_doi_is_flagged(self):
        rep = audit_sources([src(0, doi_url="10.1000/x"), src(1, doi_url="10.1000/x")],
                            CFG, ref_year=2026)
        self.assertTrue(any(f.code == "duplicate_doi" for f in rep.warnings))

    def test_near_identical_titles_are_flagged(self):
        a = src(0, judul="Blockchain untuk crowdfunding UMKM di Indonesia", doi_url="10.1000/a")
        b = src(1, judul="Blockchain untuk crowdfunding UMKM di Indonesia.", doi_url="10.1000/b")
        rep = audit_sources([a, b], CFG, ref_year=2026)
        self.assertTrue(any(f.code == "duplicate_title" for f in rep.warnings))


class TestVerdict(unittest.TestCase):
    def test_clean_ledger_is_ready(self):
        rep = audit_sources([src(i) for i in range(5)], CFG, ref_year=2026)
        self.assertEqual(VERDICT_READY, rep.verdict)
        self.assertEqual(0, rep.exit_code)

    def test_empty_ledger_is_a_blocker(self):
        rep = audit_sources([], CFG, ref_year=2026)
        self.assertEqual(VERDICT_NOT_READY, rep.verdict)


if __name__ == "__main__":
    unittest.main()


class TestDuplicateWithoutDoi(unittest.TestCase):
    def test_duplicate_plain_url_is_flagged(self):
        """Sumber institusi/web sering tanpa DOI — duplikatnya tetap harus ketahuan."""
        a = src(0, tipe="institusi", doi_url="https://bps.go.id/publikasi/2025")
        b = src(1, tipe="institusi", doi_url="https://bps.go.id/publikasi/2025/")
        rep = audit_sources([a, b], CFG, ref_year=2026)
        self.assertTrue(any(f.code == "duplicate_doi" for f in rep.warnings))


class TestInstitusiTidakKenaKuota(unittest.TestCase):
    """`institusi` masuk ACADEMIC_TYPES, jadi kuota 20% tidak menyentuhnya.

    Selama tiga versi README dan dua skill menyatakan melabeli ulang `artikel`
    menjadi `institusi` "tidak menolong, pelanggarannya hanya berpindah". Itu
    keliru: pelanggarannya hilang sama sekali. Tidak ada cara mesin memutuskan
    apakah sebuah lembaga betul pemilik datanya, jadi yang bisa dijamin hanya
    satu — skrip tidak boleh diam.
    """

    def test_melabeli_ulang_artikel_jadi_institusi_menghapus_blocker(self):
        """Ini yang dulu diklaim tidak mungkin. Dikunci supaya tidak diklaim lagi."""
        empat = [src(i) for i in range(4)]
        dua_artikel = [src(4, tipe="artikel"), src(5, tipe="artikel")]
        self.assertTrue(any(
            f.code == "article_cap"
            for f in audit_sources(empat + dua_artikel, CFG, ref_year=2026).blockers))

        dua_institusi = [src(4, tipe="institusi"), src(5, tipe="institusi")]
        rep = audit_sources(empat + dua_institusi, CFG, ref_year=2026)
        self.assertFalse(any(f.code == "article_cap" for f in rep.blockers))

    def test_tapi_sumber_institusi_selalu_didaftar_untuk_dikonfirmasi(self):
        """Penggantinya: skrip mendaftarkannya, bukan meloloskannya diam-diam."""
        empat = [src(i) for i in range(4)]
        dua_institusi = [src(4, tipe="institusi"), src(5, tipe="institusi")]
        rep = audit_sources(empat + dua_institusi, CFG, ref_year=2026)
        temuan = [f for f in rep.warnings if f.code == "institusi_konfirmasi"]
        self.assertEqual(1, len(temuan))
        self.assertIn("s004", temuan[0].message)
        self.assertIn("s005", temuan[0].message)

    def test_tanpa_sumber_institusi_tidak_ada_temuan(self):
        """Peringatan yang selalu muncul akan diabaikan."""
        rep = audit_sources([src(i) for i in range(4)], CFG, ref_year=2026)
        self.assertFalse(any(f.code == "institusi_konfirmasi" for f in rep.findings))
