"""Tes prioritas konfigurasi: userConfig plugin vs .skripsi.yaml per proyek."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from skripsi.config import USER_SCOPED, ConfigError, load_config  # noqa: E402

MINIMAL = "project_id: uji\nrecency_years: 3\n"


class ConfigCase(unittest.TestCase):
    def setUp(self):
        self._saved = {v: os.environ.get(v) for v in USER_SCOPED.values()}
        for v in USER_SCOPED.values():
            os.environ.pop(v, None)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def write(self, body):
        (self.root / ".skripsi.yaml").write_text(body, encoding="utf-8")


class TestUserConfigFallback(ConfigCase):
    def test_env_supplies_mailto_when_yaml_omits_it(self):
        """Inti fiturnya: /skripsi-init tak perlu bertanya lagi."""
        self.write(MINIMAL)
        os.environ["CLAUDE_PLUGIN_OPTION_MAILTO"] = "a@uii.ac.id"
        cfg = load_config(self.root)
        self.assertEqual("a@uii.ac.id", cfg.mailto)
        self.assertTrue(cfg.has_mailto)

    def test_env_applies_even_without_any_config_file(self):
        os.environ["CLAUDE_PLUGIN_OPTION_MAILTO"] = "a@uii.ac.id"
        self.assertEqual("a@uii.ac.id", load_config(self.root).mailto)

    def test_project_yaml_overrides_user_config(self):
        self.write(MINIMAL + 'mailto: khusus@proyek.id\n')
        os.environ["CLAUDE_PLUGIN_OPTION_MAILTO"] = "umum@uii.ac.id"
        self.assertEqual("khusus@proyek.id", load_config(self.root).mailto)

    def test_empty_yaml_value_does_not_shadow_user_config(self):
        """`mailto: ""` berarti 'tidak diisi', bukan 'sengaja dikosongkan'."""
        self.write(MINIMAL + 'mailto: ""\n')
        os.environ["CLAUDE_PLUGIN_OPTION_MAILTO"] = "umum@uii.ac.id"
        self.assertEqual("umum@uii.ac.id", load_config(self.root).mailto)

    def test_no_env_and_no_yaml_leaves_it_empty(self):
        self.write(MINIMAL)
        cfg = load_config(self.root)
        self.assertEqual("", cfg.mailto)
        self.assertFalse(cfg.has_mailto)

    def test_kbbi_path_comes_from_user_config(self):
        self.write(MINIMAL)
        os.environ["CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH"] = "/data/kbbi.sqlite"
        self.assertEqual(Path("/data/kbbi.sqlite"), load_config(self.root).resolved_kbbi_path())


class TestProjectScopedSettings(ConfigCase):
    def test_project_values_are_read(self):
        self.write(MINIMAL)
        cfg = load_config(self.root)
        self.assertEqual("uji", cfg.project_id)
        self.assertEqual(3, cfg.recency_years)

    def test_article_cap_is_floor_of_ratio(self):
        self.write(MINIMAL + "article_cap_ratio: 0.20\n")
        cfg = load_config(self.root)
        self.assertEqual(2, cfg.article_cap(12))
        self.assertEqual(0, cfg.article_cap(4))

    def test_gaya_sitasi_bawaan_apa_bukan_ieee(self):
        """Template resmi Informatika UII mewajibkan APA 6th.

        Bawaannya pernah IEEE selama delapan versi sementara template, README,
        dan skill semuanya menyatakan APA. Proyek yang `.skripsi.yaml`-nya tidak
        memuat kunci ini mendarat di gaya yang justru dilarang template, dan
        `audit_naskah.py` memperingatkan bawaan pluginnya sendiri.
        """
        self.write(MINIMAL)
        self.assertEqual("APA6", load_config(self.root).citation_style)

    def test_templat_yang_dikirim_memakai_gaya_yang_sama(self):
        """Templat dan bawaan skrip tidak boleh berbeda gaya sitasi."""
        root = Path(__file__).resolve().parents[1]
        templat = (root / "templates" / "skripsi.yaml").read_text(encoding="utf-8")
        self.assertIn("citation_style: APA6", templat)

    def test_broken_config_raises_instead_of_silently_defaulting(self):
        """Config rusak tidak boleh diam-diam jadi default — itu menyembunyikan galat."""
        self.write("project_id: uji\n  nested: tidak-didukung\n")
        with self.assertRaises(ConfigError):
            load_config(self.root)


if __name__ == "__main__":
    unittest.main()
