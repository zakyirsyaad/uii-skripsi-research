"""Jaga agar aturan yang diuji eval benar-benar ada di skill-nya.

`claude plugin eval` menguji PERILAKU model, dan itu butuh menjalankan agen.
Tes ini tidak menggantikannya. Ia menjaga hal yang lebih sempit tapi tetap
penting: bahwa aturan yang jadi dasar tiap kasus eval masih tertulis di skill.

Menghapus aturannya akan membuat eval gagal — tapi eval mahal dan jarang
dijalankan. Tes ini menangkapnya dalam hitungan milidetik.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"


def isi(*jalur: str) -> str:
    return "\n".join((ROOT / p).read_text(encoding="utf-8") for p in jalur).lower()


class TestStrukturEval(unittest.TestCase):
    def test_setiap_kasus_punya_prompt_dan_grader(self):
        kasus = [d for d in EVALS.iterdir() if d.is_dir() and d.name != "results"]
        self.assertGreaterEqual(len(kasus), 8, "suite eval menyusut")
        for d in kasus:
            self.assertTrue((d / "prompt.md").is_file(), f"{d.name}: prompt.md hilang")
            grader = list((d / "graders").glob("*.md")) if (d / "graders").is_dir() else []
            self.assertTrue(grader, f"{d.name}: tidak ada grader")

    def test_grader_menyatakan_lulus_dan_gagal(self):
        """Grader tanpa kriteria gagal tidak bisa membedakan apa pun."""
        for g in EVALS.rglob("graders/*.md"):
            t = g.read_text(encoding="utf-8").lower()
            self.assertIn("lulus bila", t, f"{g.parent.parent.name}: tanpa kriteria lulus")
            self.assertIn("gagal bila", t, f"{g.parent.parent.name}: tanpa kriteria gagal")

    def test_prompt_tidak_kosong(self):
        for p in EVALS.rglob("prompt.md"):
            self.assertGreater(len(p.read_text(encoding="utf-8").split()), 10,
                               f"{p.parent.name}: prompt terlalu pendek")


class TestAturanMasihTertulis(unittest.TestCase):
    """Tiap tes memetakan satu kasus eval ke aturan yang mendasarinya."""

    def test_kbbi_absen_dilarang_menebak(self):
        t = isi("skills/skripsi-naskah/SKILL.md",
                "skills/skripsi-naskah/references/kbbi.md")
        self.assertIn("jangan menyimpulkan", t)
        self.assertIn("kbbi.kemdikbud.go.id", t)

    def test_ada_di_kbbi_bukan_berarti_baku(self):
        t = isi("skills/skripsi-naskah/references/kbbi.md")
        self.assertIn("tidak baku", t)
        self.assertRegex(t, r"analisa|praktek|obyek")

    def test_unverifiable_dibedakan_dari_not_found(self):
        t = isi("skills/skripsi-sitasi/SKILL.md",
                "skills/skripsi-sitasi/references/status-sitasi.md")
        self.assertIn("unverifiable", t)
        self.assertIn("not_found", t)
        self.assertRegex(t, r"di luar jangkauan|tidak diindeks")

    def test_unverified_bukan_temuan(self):
        t = isi("skills/skripsi-sitasi/SKILL.md",
                "skills/skripsi-sitasi/references/status-sitasi.md")
        self.assertIn("unverified", t)
        self.assertRegex(t, r"ketiadaan temuan|belum sempat dicari|bukan bukti")

    def test_dspace_tidak_pernah_disitasi(self):
        t = isi("skills/skripsi-sitasi/SKILL.md",
                "skills/skripsi-uii/references/format-uii.md")
        self.assertIn("dspace", t)
        self.assertIn("tidak pernah", t)
        self.assertIn("daftar pustaka", t)

    def test_lanjut_tidak_menyetujui(self):
        t = isi("skills/skripsi-naskah/SKILL.md")
        self.assertIn("lanjut", t)
        self.assertRegex(t, r"bukan persetujuan|tidak menyetujui|tidak mengesahkan")

    def test_persetujuan_kata_bukan_verifikasi_klaim(self):
        t = isi("skills/skripsi-naskah/SKILL.md", "skills/skripsi-uii/SKILL.md")
        self.assertRegex(t, r"kata-katanya, bukan kebenaran|bukan kebenaran klaim")

    def test_word_tidak_ditulisi_secara_bawaan(self):
        t = isi("skills/skripsi-naskah/SKILL.md")
        self.assertIn("markdown_only", t)
        self.assertRegex(t, r"jangan buka|jangan.*ubah word|tidak boleh.*word")

    def test_metode_dari_aktivitas_bukan_judul(self):
        t = isi("skills/skripsi-uii/SKILL.md")
        self.assertRegex(t, r"bukan dari kata kunci judul|benar-benar akan dijalankan")
        self.assertIn("proposed", t)

    def test_apa6_bukan_ieee(self):
        t = isi("skills/skripsi-sitasi/SKILL.md")
        self.assertIn("apa 6th", t)
        self.assertIn("bukan ieee", t)


class TestSetiapKasusPunyaPenjaga(unittest.TestCase):
    def test_tidak_ada_kasus_eval_tanpa_tes_kontrak(self):
        """Kasus eval baru harus disertai tes yang menjaga aturannya."""
        kasus = {d.name for d in EVALS.iterdir() if d.is_dir() and d.name != "results"}
        sumber = Path(__file__).read_text(encoding="utf-8")
        # Tiap nama kasus dipetakan longgar ke nama tes lewat kata kuncinya.
        petakan = {
            "kbbi-tidak-terpasang": "kbbi_absen_dilarang_menebak",
            "sumber-institusi-bukan-fiktif": "unverifiable_dibedakan_dari_not_found",
            "jaringan-gagal-bukan-temuan": "unverified_bukan_temuan",
            "dspace-tidak-boleh-disitasi": "dspace_tidak_pernah_disitasi",
            "lanjut-bukan-persetujuan": "lanjut_tidak_menyetujui",
            "setuju-paragraf-bukan-verifikasi": "persetujuan_kata_bukan_verifikasi_klaim",
            "word-tidak-ditulisi": "word_tidak_ditulisi_secara_bawaan",
            "metode-dari-aktivitas": "metode_dari_aktivitas_bukan_judul",
        }
        for nama in kasus:
            self.assertIn(nama, petakan, f"kasus '{nama}' belum punya tes kontrak")
            self.assertIn(petakan[nama], sumber)


if __name__ == "__main__":
    unittest.main()


class TestAturanMenulisLedger(unittest.TestCase):
    """Menambah sumber sendiri adalah komitmen atas nama mahasiswa."""

    def test_baris_baru_butuh_permintaan_eksplisit(self):
        t = isi("skills/skripsi-sitasi/SKILL.md")
        self.assertRegex(t, r"tambah baris baru.*tidak|butuh permintaan eksplisit")

    def test_status_verifikasi_boleh_ditulis_perkakas(self):
        t = isi("skills/skripsi-sitasi/SKILL.md")
        self.assertIn("status_verifikasi", t)
        self.assertRegex(t, r"temuan perkakas|bukan komitmen")

    def test_jelas_dibutuhkan_bukan_izin(self):
        """Peffers untuk DSRM memang tak terhindarkan — itu tetap bukan izin."""
        t = isi("skills/skripsi-sitasi/SKILL.md")
        self.assertRegex(t, r"bukan izin")

    def test_sajikan_siap_tempel_sebagai_gantinya(self):
        t = isi("skills/skripsi-sitasi/SKILL.md")
        self.assertRegex(t, r"siap tempel")
        self.assertRegex(t, r"klaim.*dikosongkan|belum membacanya")
