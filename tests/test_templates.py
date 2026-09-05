"""Templat tersalin ke proyek mahasiswa, jadi cacatnya ikut tersalin.

Dua kegagalan yang tes ini jaga, keduanya pernah terjadi:

- Baris placeholder-nya melanggar kuota yang templat itu sendiri ajarkan,
  sehingga `/skripsi-init` selalu berakhir `not_ready` exit 1 pada proyek yang
  belum berisi apa pun.
- Frontmatter-nya kehilangan kunci yang diparse ledger.py dan ditampilkan hook
  SessionStart, jadi mahasiswanya tidak punya tempat menuliskannya.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from skripsi.audit import VERDICT_NOT_READY, audit_sources  # noqa: E402
from skripsi.config import load_config  # noqa: E402
from skripsi.ledger import ThesisContext, load_context, load_sources  # noqa: E402


class TestProyekBaruLolosAuditnyaSendiri(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "references").mkdir()
        shutil.copy(ROOT / "templates" / "skripsi.yaml", root / ".skripsi.yaml")
        for nama in ("sources.md", "thesis-context.md"):
            shutil.copy(ROOT / "templates" / nama, root / "references" / nama)
        self.root = root

    def tearDown(self):
        self.tmp.cleanup()

    def test_audit_proyek_baru_tidak_menghasilkan_blocker(self):
        """/skripsi-init menutup dengan audit_references.py. Ia harus lolos.

        Sebelumnya templat mengirim satu baris `artikel`; dengan tiga sumber
        kuotanya floor(3 x 0.20) = 0, jadi proyek kosong langsung kena blocker.
        """
        sumber, _ = load_sources(self.root / "references" / "sources.md")
        rep = audit_sources(sumber, load_config(self.root), ref_year=2026)
        self.assertEqual(
            [], [f.code for f in rep.blockers],
            "proyek baru dari templat gagal audit inisialisasinya sendiri")
        self.assertNotEqual(VERDICT_NOT_READY, rep.verdict)

    def test_ledger_konteks_templat_terparse_tanpa_galat(self):
        _, issues = load_context(self.root / "references" / "thesis-context.md")
        berat = [i for i in issues if getattr(i, "level", "error") == "error"]
        self.assertEqual([], berat, f"templat thesis-context.md tidak terparse: {berat}")


class TestFrontmatterLengkap(unittest.TestCase):
    """Kunci yang diparse tapi tidak ada di templat tidak akan pernah diisi."""

    def test_setiap_kunci_skalar_ada_di_templat(self):
        teks = (ROOT / "templates" / "thesis-context.md").read_text(encoding="utf-8")
        depan = teks.split("---")[1]
        for nama, f in ThesisContext.__dataclass_fields__.items():
            if f.type not in ("str", "int"):
                continue
            self.assertIn(f"{nama}:", depan,
                          f"ThesisContext memparse '{nama}' tapi templat tidak memuatnya")


if __name__ == "__main__":
    unittest.main()
