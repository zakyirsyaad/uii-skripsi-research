"""Jaga dokumentasi agar tidak tertinggal dari skill dan skrip.

Tiga kali dalam pengembangan plugin ini, dokumentasi tertinggal dari kode:
checklist yang menduplikasi aturan lalu membusuk, skill yang melewati batas
baris, dan README yang tertinggal enam versi — sampai menjanjikan hal yang
tidak dipenuhi plugin.

Ketiganya ditemukan lewat audit manual. Tes ini menangkap yang bisa ditangkap
mesin, supaya sisanya tidak perlu diingat.

Yang TIDAK bisa dites di sini: apakah penjelasan di README benar. Hanya
keberadaan dan konsistensinya.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")

# Judul yang sengaja tidak dicantumkan di daftar isi.
TANPA_TOC = {"Daftar isi", "Lisensi"}


class TestKelengkapanREADME(unittest.TestCase):
    """Setiap yang bisa dipakai pengguna harus bisa ditemukan di README."""

    def test_semua_skrip_disebut(self):
        for f in sorted((ROOT / "scripts").glob("*.py")):
            self.assertIn(f.name, README, f"{f.name} tidak disebut di README")

    def test_semua_command_disebut(self):
        for f in sorted((ROOT / "commands").glob("*.md")):
            self.assertIn(f"/{f.stem}", README, f"/{f.stem} tidak disebut di README")

    def test_semua_skill_disebut(self):
        for d in sorted((ROOT / "skills").iterdir()):
            if d.is_dir():
                self.assertIn(d.name, README, f"skill {d.name} tidak disebut di README")

    def test_tidak_menyebut_nama_yang_sudah_dihapus(self):
        """skripsi-audit pernah jadi nama skill sebelum diganti skripsi-kesiapan.

        README yang menyebut nama lama akan menyesatkan pembaca ke sesuatu yang
        tidak ada lagi.
        """
        sah = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
        sah |= {f.stem for f in (ROOT / "commands").glob("*.md")}
        sah |= {f.stem for f in (ROOT / "agents").glob("*.md")}
        # Dua lookbehind: titik menyingkirkan nama berkas (.skripsi-cache,
        # .skripsi-word-authorized), "uii-" menyingkirkan nama plugin sendiri.
        # Pola multi-segmen supaya "skripsi-pencari-pustaka" tidak terpotong.
        for nama in re.findall(r"(?<!\.)(?<!uii-)\b(skripsi(?:-[a-z]+)+)", README):
            self.assertIn(nama, sah,
                          f"README menyebut '{nama}' yang bukan skill, command, maupun agent")


class TestDaftarIsi(unittest.TestCase):
    """Daftar isi rusak dua kali hari ini saat menyunting README."""

    def anchor(self, judul: str) -> str:
        return re.sub(r"[^\w\s-]", "", judul).strip().lower().replace(" ", "-")

    def test_setiap_anchor_menemukan_judulnya(self):
        judul = {self.anchor(h) for h in re.findall(r"^## (.+)$", README, re.M)}
        for a in re.findall(r"^- \[.+?\]\(#([^)]+)\)", README, re.M):
            self.assertIn(a, judul, f"anchor daftar isi '{a}' tidak menemukan judul")

    def test_setiap_judul_ada_di_daftar_isi(self):
        """Menambah bagian tanpa mendaftarkannya membuatnya tidak ditemukan."""
        toc = set(re.findall(r"^- \[.+?\]\(#([^)]+)\)", README, re.M))
        for h in re.findall(r"^## (.+)$", README, re.M):
            if h in TANPA_TOC:
                continue
            self.assertIn(self.anchor(h), toc, f"judul '{h}' tidak ada di daftar isi")


class TestAturanPentingTercantum(unittest.TestCase):
    """Aturan yang mengubah perilaku plugin harus terbaca pengguna, bukan cuma model.

    Tiap tes memetakan satu aturan skill ke pernyataannya di README.
    """

    def test_batas_pelindung_word_dinyatakan(self):
        """README pernah berbunyi 'hook memblokir' tanpa syarat — itu janji palsu."""
        self.assertRegex(README, r"unzip|bukan jaminan|bukan pengakalan")

    def test_plugin_tidak_menambah_sumber_sendiri(self):
        self.assertRegex(README, r"siap tempel")
        self.assertRegex(README, r"tidak akan.*menambahkan|tidak menambah sumber")

    def test_istilah_sari_dijelaskan(self):
        self.assertRegex(README, r"bernama SARI")

    def test_gaya_sitasi_apa_bukan_ieee(self):
        self.assertRegex(README, r"APA 6th")
        self.assertRegex(README, r"bukan IEEE")

    def test_kuota_tidak_diklaim_kebal_pelabelan_ulang(self):
        """README pernah berjanji `audit_references.py` menangkap pelabelan ulang.

        Tidak. Tipe `institusi` terhitung akademik, jadi melabeli ulang sebuah
        `artikel` menghapus blocker kuota sepenuhnya. Yang ada hanya peringatan
        yang mendaftarkan sumber `institusi` untuk dikonfirmasi. README harus
        menyebut daftar itu, bukan menjanjikan penangkal.
        """
        self.assertRegex(README, r"institusi` didaftarkan|didaftarkan supaya")
        self.assertNotRegex(
            README, r"[Pp]elanggaran(nya)? hanya\s+berpindah",
            "README kembali menjanjikan penangkal kuota yang tidak ada")

    def test_dspace_tidak_boleh_disitasi(self):
        self.assertIn("DSpace", README)
        self.assertRegex(README, r"bukan sumber|tidak pernah masuk")


class TestBatasBaris(unittest.TestCase):
    """SKILL.md dibatasi ~120 baris supaya kedalaman pindah ke references/.

    Batas ini sudah dilewati dua kali sambil menambahkan aturan yang sah, dan
    dua kali ketahuannya baru saat menghitung manual.
    """

    BATAS = 120

    def test_skill_tidak_melewati_batas(self):
        for f in sorted((ROOT / "skills").glob("*/SKILL.md")):
            n = len(f.read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(
                n, self.BATAS,
                f"{f.parent.name}/SKILL.md {n} baris, batasnya {self.BATAS}. "
                "Pindahkan kedalamannya ke references/, jangan naikkan batasnya.")


class TestPerintahBisaDijalankan(unittest.TestCase):
    """`<plugin>` adalah placeholder untuk pembaca manusia; command butuh env var.

    /skripsi-init sempat memakai keduanya dalam satu berkas, jadi dua blok
    bash-nya tidak bisa dijalankan apa adanya.
    """

    def test_command_tidak_memakai_placeholder_prosa(self):
        for f in sorted((ROOT / "commands").glob("*.md")):
            teks = f.read_text(encoding="utf-8")
            self.assertNotIn(
                "<plugin>", teks,
                f"commands/{f.name} memakai '<plugin>'; pakai "
                "${CLAUDE_PLUGIN_ROOT} supaya blok bash-nya bisa dijalankan")


class TestTipeDidokumentasikan(unittest.TestCase):
    """Tanpa --tipe, sumber institusi/artikel yang nyata dilaporkan NOT_FOUND.

    verify.py hanya memilih jalur UNVERIFIABLE bila claim.tipe terisi. Memeriksa
    satu sumber BPS tanpa flag itu menghasilkan tuduhan sitasi fiktif terhadap
    sumber yang benar ada — persis false positive yang INDEXED_TYPES dibuat
    untuk mencegah.
    """

    def test_flag_tipe_disebut_di_tempat_yang_memakainya(self):
        for path in ("README.md", "commands/skripsi-cek.md",
                     "skills/skripsi-sitasi/SKILL.md"):
            teks = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("--tipe", teks, f"{path} tidak menyebut --tipe")


class TestEvalTerdaftar(unittest.TestCase):
    """evals/README.md sempat berjudul "Delapan kasus" di atas tabel sembilan baris.

    Berkas yang sama bahkan punya bagian "Kasus kesembilan", jadi ia tahu ada
    sembilan dan tetap salah menghitung. README.md dan CLAUDE.md ikut salah.
    """

    def kasus(self):
        return {d.name for d in (ROOT / "evals").iterdir()
                if d.is_dir() and d.name != "results"}

    def baris_tabel(self):
        """Hanya baris tabel. Nama kasus juga muncul di prosa di bawahnya, jadi
        memeriksa keberadaan di seluruh berkas akan meloloskan baris yang hilang.
        """
        teks = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        return set(re.findall(r"^\| `([a-z-]+)` \|", teks, re.M))

    def test_tabel_cocok_persis_dengan_kasus_yang_ada(self):
        tabel, kasus = self.baris_tabel(), self.kasus()
        self.assertEqual(
            kasus, tabel,
            f"tabel evals/README.md tidak cocok. Hilang: {sorted(kasus - tabel)}; "
            f"tidak ada berkasnya: {sorted(tabel - kasus)}")

    def test_jumlah_kasus_yang_tertulis_benar(self):
        """Judulnya menyebut angka; angka itu harus cocok dengan isinya."""
        angka = {"delapan": 8, "sembilan": 9, "sepuluh": 10, "sebelas": 11}
        teks = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        m = re.search(r"^## (\w+) kasus$", teks, re.M)
        self.assertIsNotNone(m, "evals/README.md kehilangan judul '## <angka> kasus'")
        kata = m.group(1).lower()
        self.assertIn(kata, angka, f"angka '{kata}' tidak dikenali")
        self.assertEqual(len(self.kasus()), angka[kata],
                         f"judul menyebut {kata} kasus, yang ada {len(self.kasus())}")


class TestTanpaHitunganTesYangMembusuk(unittest.TestCase):
    """"diuji 139 tes unit" basi begitu satu tes ditambahkan.

    Angka yang tidak dihitung ulang oleh apa pun akan selalu tertinggal.
    """

    def test_dokumen_tidak_memaku_jumlah_tes(self):
        for path in ("README.md", "evals/README.md", "CLAUDE.md"):
            teks = (ROOT / path).read_text(encoding="utf-8")
            self.assertNotRegex(
                teks, r"\b\d{2,4}\s+tes\b|\b\d{2,4}\s+tests?\b",
                f"{path} memaku jumlah tes; angka itu akan membusuk")


class TestRujukanTidakYatim(unittest.TestCase):
    def test_setiap_berkas_rujukan_ditautkan_skill_nya(self):
        """Rujukan yang tidak ditautkan tidak akan pernah dibaca model."""
        for ref in sorted((ROOT / "skills").glob("*/references/*.md")):
            skill = (ref.parent.parent / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(ref.name, skill,
                          f"{ref.parent.parent.name}/SKILL.md tidak menautkan {ref.name}")


class TestVersiKonsisten(unittest.TestCase):
    def test_kedua_manifest_sama_versinya(self):
        p = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        m = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(p["version"], m["plugins"][0]["version"],
                         "versi plugin.json dan marketplace.json berbeda")

    def test_nama_plugin_sama_di_kedua_manifest(self):
        p = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        m = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(p["name"], m["plugins"][0]["name"])


if __name__ == "__main__":
    unittest.main()
