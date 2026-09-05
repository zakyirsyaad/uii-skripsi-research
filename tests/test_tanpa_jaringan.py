"""Buktikan janji "tidak menyentuh jaringan", jangan cuma menuliskannya.

README dan CLAUDE.md sama-sama menyatakan tes unit tidak menyentuh jaringan.
Selama beberapa versi itu tidak benar: jalur UNVERIFIABLE di `verify.py`
memanggil `url_is_reachable`, yang mengirim HEAD sungguhan, dan dua tes
memberinya URL. Tiap kali suite dijalankan, bps.go.id dan kontan.co.id
dihubungi.

Akibatnya bukan cuma lambat. Tes yang bergantung jaringan memberi hasil berbeda
di kereta, di CI tanpa egress, dan saat situs sumbernya sedang mati — lalu
ketidakcocokan itu dikira bug di kode.

Modul ini menjalankan seluruh modul tes lain dengan `urlopen` disadap, dan gagal
bila ada satu pun permintaan keluar.
"""
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INI = Path(__file__).stem


def modul_tes_lain():
    """Nama modul harus lengkap dengan paketnya kalau suite dimuat sebagai
    `tests.test_*`; kalau tidak, pemuatan gagal diam-diam dan tidak ada yang
    berjalan — penjaga yang tampak lulus padahal tidak menguji apa pun."""
    prefix = f"{__package__}." if __package__ else ""
    return sorted(prefix + f.stem for f in (ROOT / "tests").glob("test_*.py")
                  if f.stem != INI)


class TestSuiteTidakMenyentuhJaringan(unittest.TestCase):
    def test_tidak_ada_permintaan_keluar(self):
        panggilan: list[str] = []
        asli = urllib.request.urlopen

        def sadap(req, *a, **k):
            panggilan.append(getattr(req, "full_url", str(req)))
            raise urllib.error.URLError("jaringan diblokir oleh tes")

        urllib.request.urlopen = sadap
        try:
            suite = unittest.TestLoader().loadTestsFromNames(modul_tes_lain())
            hasil = unittest.TextTestRunner(
                stream=open("/dev/null", "w"), verbosity=0).run(suite)
        finally:
            urllib.request.urlopen = asli

        self.assertEqual(
            [], panggilan,
            f"{len(panggilan)} permintaan jaringan dari tes: {panggilan}")
        # Kalau tes lain gagal justru karena jaringan diblokir, itu juga
        # ketergantungan jaringan — hanya bentuknya berbeda.
        self.assertTrue(hasil.wasSuccessful(),
                        "tes lain gagal saat jaringan diblokir")


if __name__ == "__main__":
    unittest.main()
