"""Muat `.skripsi.yaml` milik proyek skripsi.

Config ini tinggal di proyek skripsi pengguna, bukan di plugin. Plugin netral;
semua yang spesifik proyek diparameterisasi lewat file ini.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from .minyaml import MiniYamlError
from .minyaml import safe_load as _yaml_load

CONFIG_FILENAME = ".skripsi.yaml"


class ConfigError(ValueError):
    """`.skripsi.yaml` ada tapi tidak bisa dibaca — jangan diam-diam pakai default."""

# Setelan milik PENGGUNA, bukan proyek: satu mahasiswa punya satu email dan satu
# basis data KBBI untuk semua skripsinya. Claude Code menanyakannya sekali saat
# install (userConfig di plugin.json) dan mengeksposnya lewat env var ini, jadi
# `/skripsi-init` tidak perlu bertanya lagi di tiap proyek baru.
USER_SCOPED = {
    "mailto": "CLAUDE_PLUGIN_OPTION_MAILTO",
    "kbbi_db_path": "CLAUDE_PLUGIN_OPTION_KBBI_DB_PATH",
}

# `citation_style` bawaannya APA6, bukan pilihan bebas: template resmi
# Informatika UII menetapkannya, dan proyek yang `.skripsi.yaml`-nya tidak
# memuat kunci ini harus tetap mendarat di gaya yang benar.
DEFAULTS = {
    "schema_version": 1,
    "project_id": "",
    "mailto": "",
    "kbbi_db_path": "",
    "recency_years": 5,
    "article_cap_ratio": 0.20,
    "citation_style": "APA6",
    "cache_dir": ".skripsi-cache",
}


@dataclass
class Config:
    schema_version: int = 1
    project_id: str = ""
    mailto: str = ""
    kbbi_db_path: str = ""
    recency_years: int = 5
    article_cap_ratio: float = 0.20
    citation_style: str = "APA6"
    cache_dir: str = ".skripsi-cache"
    root: Path = field(default_factory=Path.cwd)
    source_path: Path | None = None

    def article_cap(self, total_sources: int) -> int:
        """Jumlah absolut sumber non-akademik yang masih boleh."""
        return math.floor(total_sources * self.article_cap_ratio)

    @property
    def has_mailto(self) -> bool:
        return bool(self.mailto and "@" in self.mailto)

    def resolved_cache_dir(self) -> Path:
        p = Path(self.cache_dir).expanduser()
        return p if p.is_absolute() else self.root / p

    def resolved_kbbi_path(self) -> Path | None:
        if not self.kbbi_db_path:
            return None
        p = Path(self.kbbi_db_path).expanduser()
        return p if p.is_absolute() else self.root / p


def find_config(start: Path | None = None) -> Path | None:
    """Cari `.skripsi.yaml` dari `start` ke atas sampai root filesystem."""
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        probe = candidate / CONFIG_FILENAME
        if probe.is_file():
            return probe
    return None


def load_config(start: Path | None = None) -> Config:
    """Muat config; kalau tidak ada, kembalikan default agar perkakas tetap jalan."""
    path = find_config(start)
    if path is None:
        # Tanpa .skripsi.yaml pun, setelan tingkat pengguna tetap berlaku.
        return Config(
            root=(start or Path.cwd()).resolve(),
            **{k: os.environ.get(env, "").strip() for k, env in USER_SCOPED.items()},
        )

    try:
        raw = _yaml_load(path.read_text(encoding="utf-8")) or {}
    except MiniYamlError as exc:
        raise ConfigError(f"{path}: {exc}") from exc

    merged = {**DEFAULTS, **{k: v for k, v in raw.items() if k in DEFAULTS}}
    # Nilai kosong di YAML (`mailto: ""`) sah; nilai None diperlakukan sebagai absen.
    for key, default in DEFAULTS.items():
        if merged.get(key) is None:
            merged[key] = default

    # Urutan: nilai eksplisit di .skripsi.yaml menang (override per proyek),
    # kalau kosong ambil dari userConfig plugin, kalau tidak ada juga baru default.
    for key, env in USER_SCOPED.items():
        if not merged.get(key):
            merged[key] = os.environ.get(env, "").strip() or DEFAULTS[key]

    return Config(
        **merged,
        root=path.parent,
        source_path=path,
    )
