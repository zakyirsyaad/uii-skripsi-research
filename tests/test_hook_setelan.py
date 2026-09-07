"""Hook harus mengatakan setelan yang belum lengkap, bukan diam.

Penulis plugin ini sendiri terjebak: sesi skripsinya menyuruh membuka
`/plugin configure`, perintah yang tidak tersedia di tab Code aplikasi
desktop, dan tidak ada satu pun tempat yang menyebut jalan lain. Sementara
itu KBBI tidak terpasang tanpa pemberitahuan apa pun.

`CLAUDE.md` sudah memuat aturannya untuk Python yang hilang — perkakas yang
tidak bisa berjalan harus mengatakannya, bukan tampak bekerja. Tes ini
menerapkan aturan yang sama untuk konfigurasi yang kosong.
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "hooks"))

from session_start_context import setup_lines  # noqa: E402

ENV = ("CLAUDE_PLUGIN_OPTION_MAILTO", "CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH")


class SetelanCase(unittest.TestCase):
    def setUp(self):
        self._env = {k: os.environ.get(k) for k in ENV}
        for k in ENV:
            os.environ.pop(k, None)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "references").mkdir()
        shutil.copy(ROOT / "templates" / "skripsi.yaml", self.root / ".skripsi.yaml")
        self.kbbi = self.root / "kbbi.sqlite"
        self.kbbi.write_bytes(b"")

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def teks(self):
        return "\n".join(setup_lines(self.root))


class TestMenyebutYangKurang(SetelanCase):
    def test_tanpa_konfigurasi_menyebut_keduanya(self):
        t = self.teks()
        self.assertIn("KBBI belum terpasang", t)
        self.assertIn("belum diisi", t)

    def test_kbbi_terpasang_maka_hanya_mailto(self):
        os.environ["CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH"] = str(self.kbbi)
        t = self.teks()
        self.assertNotIn("KBBI belum terpasang", t)
        self.assertIn("belum diisi", t)

    def test_jalur_kbbi_menunjuk_berkas_yang_tidak_ada_tetap_diperingatkan(self):
        """Jalur yang salah ketik lebih berbahaya daripada jalur kosong.

        Konfigurasinya terlihat terisi, padahal validasi bahasa tetap mati.
        """
        os.environ["CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH"] = str(self.root / "tidak-ada.sqlite")
        self.assertIn("KBBI belum terpasang", self.teks())


class TestDiamSaatLengkap(SetelanCase):
    def test_konfigurasi_lengkap_tidak_menghasilkan_apa_apa(self):
        """Peringatan yang muncul terus akan diabaikan."""
        os.environ["CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH"] = str(self.kbbi)
        os.environ["CLAUDE_PLUGIN_OPTION_MAILTO"] = "a@b.id"
        self.assertEqual([], setup_lines(self.root))


class TestMemberiJalanKeluar(SetelanCase):
    """Menyebut masalah tanpa menyebut perbaikannya sama saja jalan buntu."""

    def test_menyebut_perintah_unduh_kbbi(self):
        self.assertIn("setup_kbbi.py", self.teks())

    def test_menyebut_alternatif_saat_panel_tidak_tersedia(self):
        """Ini jalan buntu yang benar-benar dialami penulis pluginnya."""
        t = self.teks()
        self.assertIn("settings.json", t)
        self.assertIn("CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH", t)

    def test_memperingatkan_agar_mailto_tidak_masuk_git(self):
        self.assertIn(".skripsi.yaml", self.teks())


class TestTidakPernahMenggagalkanSesi(SetelanCase):
    def test_proyek_tanpa_skripsi_yaml_tidak_meledak(self):
        (self.root / ".skripsi.yaml").unlink()
        setup_lines(self.root)          # cukup: tidak melempar

    def test_konfigurasi_rusak_diam_bukan_melempar(self):
        """Galat konfigurasi dilaporkan skripnya sendiri, bukan lewat hook."""
        (self.root / ".skripsi.yaml").write_text("a:\n  b: nested\n", encoding="utf-8")
        self.assertEqual([], setup_lines(self.root))


if __name__ == "__main__":
    unittest.main()
