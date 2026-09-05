"""Tes pembaca .docx dan audit naskah. Tanpa jaringan, .docx dibuat di sini."""
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from skripsi.docx import daftar_isi, is_docx, judul, paragraf, teks  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "audit_naskah", ROOT / "scripts" / "audit_naskah.py")
audit_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit_mod)


def buat_docx(path: Path, paragraf_list):
    """paragraf_list: (gaya, teks); gaya kosong berarti tanpa style."""
    isi = []
    for gaya, t in paragraf_list:
        st = f'<w:pPr><w:pStyle w:val="{gaya}"/></w:pPr>' if gaya else ""
        isi.append(f"<w:p>{st}<w:r><w:t>{t}</w:t></w:r></w:p>")
    doc = ('<?xml version="1.0"?><w:document '
           'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           "<w:body>" + "".join(isi) + "</w:body></w:document>")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", doc)
        z.writestr("[Content_Types].xml", "<Types/>")
    return path


PARAS = [
    ("Heading2", "HALAMAN JUDUL"),
    ("Heading2", "SARI"),
    ("", "Bagian sari adalah bagian laporan yang berisi ide pokok laporan yang meliputi hal ini."),
    ("Heading2", "GLOSARIUM"),
    ("TOC1", "BAB I TULISKAN JUDUL BAB DI BARIS INI PAGEREF _Toc123"),
    ("Heading2", "BAB IPENDAHULUAN"),
    ("", "Sistem ini dibangun untuk menjawab kebutuhan pengguna (Nakamoto, 2008)."),
]


class DocxCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = buat_docx(Path(cls.tmp.name) / "naskah.docx", PARAS)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestPembacaDocx(DocxCase):
    def test_membaca_seluruh_teks(self):
        self.assertIn("Bagian sari adalah bagian laporan", teks(self.f))

    def test_paragraf_membawa_gayanya(self):
        self.assertIn(("Heading2", "SARI"), paragraf(self.f))

    def test_judul_menyaring_entri_daftar_isi(self):
        """Cache daftar isi bisa jauh tertinggal — jangan dikira judul bab."""
        judul_teks = [t for _, t in judul(self.f)]
        self.assertIn("BAB IPENDAHULUAN", judul_teks)
        self.assertNotIn("BAB I TULISKAN JUDUL BAB DI BARIS INI PAGEREF _Toc123", judul_teks)

    def test_daftar_isi_terbaca_terpisah(self):
        self.assertTrue(any("PAGEREF" in x for x in daftar_isi(self.f)))

    def test_is_docx_menolak_yang_bukan(self):
        lain = Path(self.tmp.name) / "bukan.docx"
        lain.write_text("ini teks biasa", encoding="utf-8")
        self.assertFalse(is_docx(lain))
        self.assertFalse(is_docx(Path(self.tmp.name) / "tidak-ada.docx"))


class TestKlasifikasiSisaTemplate(unittest.TestCase):
    TPL = ("Bagian sari adalah bagian laporan yang berisi ide pokok laporan yang meliputi hal ini. "
           "Setelah proses editing dianggap selesai isi halaman ini harus di-update dengan klik kanan. "
           "Apabila di kemudian hari terbukti ada bagian dari karya ini bukan hasil karya sendiri maka ditarik.")

    def klasifikasi(self, naskah):
        return audit_mod.sisa_template(naskah, self.TPL)

    def test_instruksi_template_ditandai_hapus(self):
        n = "GLOSARIUM\nSetelah proses editing dianggap selesai isi halaman ini harus di-update dengan klik kanan."
        self.assertEqual("hapus", self.klasifikasi(n)[0]["aksi"])

    def test_instruksi_di_bagian_berisi_mengingatkan_isi_sendiri(self):
        """Menghapus instruksi di SARI meninggalkan bagian itu kosong."""
        n = "SARI\nBagian sari adalah bagian laporan yang berisi ide pokok laporan yang meliputi hal ini."
        h = self.klasifikasi(n)[0]
        self.assertEqual("hapus", h["aksi"])
        self.assertEqual("SARI", h["bagian"])
        self.assertIn("tulis isi bagian ini sendiri", h["alasan"])

    def test_teks_resmi_ditandai_tetap(self):
        """Pernyataan keaslian memang teks resmi — jangan disuruh hapus."""
        n = ("HALAMAN PERNYATAAN KEASLIAN TUGAS AKHIR\nApabila di kemudian hari terbukti "
             "ada bagian dari karya ini bukan hasil karya sendiri maka ditarik.")
        self.assertEqual("tetap", self.klasifikasi(n)[0]["aksi"])

    def test_kalimat_sendiri_tidak_dilaporkan(self):
        n = "BAB I PENDAHULUAN\nSistem crowdfunding ini dibangun di atas jaringan Base Sepolia untuk menekan biaya."
        self.assertEqual([], self.klasifikasi(n))


class TestAudit(DocxCase):
    def test_mendeteksi_daftar_isi_basi(self):
        a = audit_mod.audit(self.f, None)
        self.assertTrue(a["daftar_isi_basi"])

    def test_mendeteksi_halaman_awal_yang_hilang(self):
        a = audit_mod.audit(self.f, None)
        self.assertFalse(a["halaman_awal"]["DAFTAR TABEL"])
        self.assertTrue(a["halaman_awal"]["SARI"])

    def test_sari_bukan_abstrak(self):
        """Template UII memakai SARI. Mencari 'ABSTRAK' menghasilkan temuan palsu."""
        self.assertIn("SARI", audit_mod.HALAMAN_AWAL)
        self.assertNotIn("ABSTRAK", audit_mod.HALAMAN_AWAL)

    def test_mengenali_gaya_apa(self):
        a = audit_mod.audit(self.f, None)
        self.assertEqual(0, a["sitasi"]["ieee"])
        self.assertGreater(a["sitasi"]["apa"], 0)


if __name__ == "__main__":
    unittest.main()
