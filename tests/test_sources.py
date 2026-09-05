"""Tes lapisan jaringan. HTTP di-mock; tidak ada permintaan keluar.

Ini satu-satunya modul inti yang lama tidak punya tes langsung, padahal justru
di sinilah dua kegagalan terburuk plugin ini lahir:

- kegagalan jaringan diam-diam menjadi "tidak ditemukan", yang mengubah gangguan
  koneksi menjadi tuduhan sitasi fiktif;
- metadata salah petakan yang lolos sebagai `OK`.

Keduanya tidak muncul sebagai error. Karena itu diuji di sini, bukan lewat
`FakeClient` yang justru menggantikan kode aslinya.
"""
import io
import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import skripsi.sources as sources  # noqa: E402
from skripsi.sources import (  # noqa: E402
    MetadataClient, NetworkUnavailable, _crossref_to_work, _datacite_to_work,
    _openalex_to_work, fetch_json,
)


class Respons(io.BytesIO):
    """Cukup mirip respons urlopen untuk dipakai sebagai context manager."""

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def ok(body: dict) -> Respons:
    return Respons(json.dumps(body).encode())


def http_error(code: int, headers: dict | None = None) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://x", code, "uji", headers or {}, None)


class TransportCase(unittest.TestCase):
    """Sadap urlopen dan sleep. Tidak ada tes di sini yang menyentuh jaringan."""

    def setUp(self):
        self.diminta: list[urllib.request.Request] = []
        self._urlopen = urllib.request.urlopen
        self._sleep = sources.time.sleep
        sources.time.sleep = lambda d: None

    def tearDown(self):
        urllib.request.urlopen = self._urlopen
        sources.time.sleep = self._sleep

    def balas(self, *hasil):
        """Tiap panggilan berikutnya mengambil satu item; Exception dilempar."""
        antrean = list(hasil)

        def palsu(req, *a, **k):
            self.diminta.append(req)
            item = antrean.pop(0) if antrean else hasil[-1]
            if isinstance(item, Exception):
                raise item
            return item

        urllib.request.urlopen = palsu


class TestKegagalanJaringanBukanKetiadaan(TransportCase):
    """Pembedaan paling penting di seluruh plugin ini."""

    def test_404_berarti_karyanya_memang_tidak_ada(self):
        self.balas(http_error(404))
        self.assertIsNone(fetch_json("https://api.contoh/x"))

    def test_jaringan_mati_melempar_bukan_mengembalikan_none(self):
        """None berarti 'dicari, tidak ada'. Koneksi mati bukan itu."""
        self.balas(urllib.error.URLError("mati"))
        with self.assertRaises(NetworkUnavailable):
            fetch_json("https://api.contoh/x")

    def test_500_berulang_melempar_bukan_mengembalikan_none(self):
        self.balas(http_error(500))
        with self.assertRaises(NetworkUnavailable):
            fetch_json("https://api.contoh/x")

    def test_json_rusak_melempar_bukan_dianggap_kosong(self):
        self.balas(Respons(b"bukan json"))
        with self.assertRaises(NetworkUnavailable):
            fetch_json("https://api.contoh/x")


class TestBackoff(TransportCase):
    def test_429_dicoba_ulang_lalu_berhasil(self):
        self.balas(http_error(429), http_error(429), ok({"ok": True}))
        self.assertEqual({"ok": True}, fetch_json("https://api.contoh/x"))
        self.assertEqual(3, len(self.diminta))

    def test_400_tidak_dicoba_ulang(self):
        """Permintaan yang salah bentuk tidak akan membaik dengan diulang."""
        self.balas(http_error(400))
        with self.assertRaises(NetworkUnavailable):
            fetch_json("https://api.contoh/x")
        self.assertEqual(1, len(self.diminta))

    def test_percobaan_dibatasi(self):
        self.balas(http_error(503))
        with self.assertRaises(NetworkUnavailable):
            fetch_json("https://api.contoh/x", retries=2)
        self.assertEqual(2, len(self.diminta))


class TestCache(TransportCase):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        super().tearDown()
        self.tmp.cleanup()

    def test_panggilan_kedua_tidak_menghubungi_api_lagi(self):
        self.balas(ok({"nilai": 1}))
        url = "https://api.contoh/x"
        self.assertEqual({"nilai": 1}, fetch_json(url, cache_dir=self.dir))
        self.assertEqual({"nilai": 1}, fetch_json(url, cache_dir=self.dir))
        self.assertEqual(1, len(self.diminta), "cache tidak dipakai")

    def test_url_berbeda_tidak_saling_menimpa(self):
        self.balas(ok({"a": 1}), ok({"b": 2}))
        self.assertEqual({"a": 1}, fetch_json("https://api.contoh/a", cache_dir=self.dir))
        self.assertEqual({"b": 2}, fetch_json("https://api.contoh/b", cache_dir=self.dir))

    def test_cache_rusak_diambil_ulang_bukan_meledak(self):
        self.balas(ok({"nilai": 1}))
        url = "https://api.contoh/x"
        fetch_json(url, cache_dir=self.dir)
        for f in self.dir.glob("*.json"):
            f.write_text("rusak{{", encoding="utf-8")
        self.balas(ok({"nilai": 2}))
        self.assertEqual({"nilai": 2}, fetch_json(url, cache_dir=self.dir))


class TestPolitePool(TransportCase):
    def test_mailto_masuk_user_agent(self):
        self.balas(ok({}))
        fetch_json("https://api.contoh/x", mailto="a@b.id")
        self.assertIn("mailto:a@b.id", self.diminta[0].get_header("User-agent"))

    def test_tanpa_mailto_user_agent_tetap_ada_tanpa_alamat(self):
        self.balas(ok({}))
        fetch_json("https://api.contoh/x")
        ua = self.diminta[0].get_header("User-agent")
        self.assertTrue(ua)
        self.assertNotIn("mailto:", ua)


class TestPemetaanMetadata(unittest.TestCase):
    """Salah petakan tidak memunculkan error — ia lolos sebagai OK."""

    def test_crossref_mempertahankan_penulis_korporat_utuh(self):
        """Memecah "Badan Pusat Statistik" jadi nama orang merusak daftar pustaka."""
        w = _crossref_to_work({
            "DOI": "10.1000/X", "title": ["Judul"],
            "author": [{"name": "Badan Pusat Statistik"}, {"family": "Nakamoto"}],
            "issued": {"date-parts": [[2024]]},
        })
        self.assertEqual(["Badan Pusat Statistik", "Nakamoto"], w.authors)

    def test_crossref_doi_dinormalkan_huruf_kecil(self):
        w = _crossref_to_work({"DOI": "10.1000/ABC", "title": ["J"]})
        self.assertEqual("10.1000/abc", w.doi)

    def test_crossref_mendeteksi_penarikan(self):
        w = _crossref_to_work({
            "DOI": "10.1/x", "title": ["J"],
            "update-to": [{"type": "retraction"}],
        })
        self.assertTrue(w.is_retracted)

    def test_crossref_tanpa_tahun_tidak_meledak(self):
        w = _crossref_to_work({"DOI": "10.1/x", "title": ["J"], "issued": {}})
        self.assertIsNone(w.year)

    def test_openalex_mengambil_nama_keluarga(self):
        w = _openalex_to_work({
            "doi": "https://doi.org/10.1000/ABC", "title": "Judul",
            "authorships": [{"author": {"display_name": "Satoshi Nakamoto"}}],
            "publication_year": 2008,
        })
        self.assertEqual(["Nakamoto"], w.authors)
        self.assertEqual("10.1000/abc", w.doi, "prefiks doi.org harus dilucuti")

    def test_openalex_mendeteksi_penarikan(self):
        self.assertTrue(_openalex_to_work({"title": "J", "is_retracted": True}).is_retracted)

    def test_openalex_menggabung_halaman(self):
        w = _openalex_to_work({"title": "J",
                               "biblio": {"first_page": "10", "last_page": "25"}})
        self.assertEqual("10-25", w.pages)

    def test_datacite_memakai_name_bila_tidak_ada_familyname(self):
        w = _datacite_to_work({"attributes": {
            "doi": "10.5281/ZENODO.1", "titles": [{"title": "Dataset"}],
            "creators": [{"name": "Lembaga X"}, {"familyName": "Sari"}],
            "publicationYear": 2023,
        }})
        self.assertEqual(["Lembaga X", "Sari"], w.authors)
        self.assertEqual("10.5281/zenodo.1", w.doi)

    def test_ketiganya_menandai_api_asalnya(self):
        """Tanpa ini, laporan tidak bisa menyebut sumber metadatanya."""
        self.assertEqual("crossref", _crossref_to_work({"title": ["J"]}).api)
        self.assertEqual("openalex", _openalex_to_work({"title": "J"}).api)
        self.assertEqual("datacite", _datacite_to_work({"attributes": {}}).api)


class TestPenjenjanganByDoi(TransportCase):
    def klien(self, **kw):
        return MetadataClient(**kw)

    def test_crossref_kena_openalex_tidak_dipanggil(self):
        self.balas(ok({"message": {"DOI": "10.1/x", "title": ["Judul"]}}))
        w = self.klien().by_doi("10.1/x")
        self.assertEqual("crossref", w.api)
        self.assertEqual(1, len(self.diminta), "API berikutnya tidak boleh dihubungi")

    def test_crossref_404_jatuh_ke_openalex(self):
        self.balas(http_error(404), ok({"title": "Judul", "publication_year": 2020}))
        w = self.klien().by_doi("10.1/x")
        self.assertEqual("openalex", w.api)

    def test_semua_tidak_terjangkau_melempar_bukan_mengembalikan_none(self):
        """Kalau ini mengembalikan None, gangguan koneksi jadi tuduhan fiktif."""
        self.balas(urllib.error.URLError("mati"))
        with self.assertRaises(NetworkUnavailable):
            self.klien().by_doi("10.1/x")

    def test_terjangkau_tapi_tidak_ada_mengembalikan_none(self):
        self.balas(http_error(404))
        self.assertIsNone(self.klien().by_doi("10.1/x"))

    def test_body_cacat_dilewati_ke_api_berikutnya(self):
        """Bentuk tak terduga dari satu API tidak boleh menjatuhkan verifikasi."""
        self.balas(ok({"tanpa_message": True}),
                   ok({"title": "Judul", "publication_year": 2020}))
        self.assertEqual("openalex", self.klien().by_doi("10.1/x").api)

    def test_doi_dinormalkan_sebelum_dikirim(self):
        self.balas(ok({"message": {"DOI": "10.1/x", "title": ["J"]}}))
        self.klien().by_doi("  https://doi.org/10.1/X  ")
        self.assertIn("10.1/x", self.diminta[0].full_url)

    def test_doi_kosong_tidak_memanggil_api(self):
        self.balas(ok({}))
        self.assertIsNone(self.klien().by_doi("   "))
        self.assertEqual([], self.diminta)

    def test_mailto_dikirim_ke_crossref_dan_openalex_tapi_tidak_datacite(self):
        """Perilaku yang dinyatakan bagian Privasi README; dikunci di sini."""
        self.balas(http_error(404), http_error(404), http_error(404))
        self.klien(mailto="a@b.id").by_doi("10.1/x")
        url = [r.full_url for r in self.diminta]
        self.assertIn("mailto=", url[0], "crossref harus dapat parameter mailto")
        self.assertIn("mailto=", url[1], "openalex harus dapat parameter mailto")
        self.assertNotIn("mailto=", url[2], "datacite tidak memakai polite pool")

    def test_api_yang_gagal_dicatat_untuk_dilaporkan(self):
        """Tiap API dicoba tiga kali sebelum dinyatakan tak terjangkau.

        Versi pertama tes ini cuma mengantre dua error dan mengira Crossref
        sudah menyerah — padahal percobaan ketiganya justru memakan respons
        yang disiapkan untuk DataCite.
        """
        mati = urllib.error.URLError("mati")
        self.balas(mati, mati, mati,          # crossref habis
                   mati, mati, mati,          # openalex habis
                   ok({"data": {"attributes": {"titles": [{"title": "J"}]}}}))
        k = self.klien()
        w = k.by_doi("10.1/x")
        self.assertEqual("datacite", w.api)
        self.assertEqual(["crossref", "openalex"], k.unreachable)


if __name__ == "__main__":
    unittest.main()
