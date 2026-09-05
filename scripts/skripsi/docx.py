"""Baca berkas .docx dengan pustaka standar saja.

Naskah yang diserahkan ke pembimbing berformat Word, jadi tanpa ini ada seluruh
kelas pemeriksaan yang tidak pernah bisa dijalankan plugin.

.docx adalah arsip zip berisi XML, sehingga `zipfile` sudah cukup — tidak perlu
python-docx. Yang diambil hanya teks dan gaya paragraf; format visual diabaikan.

MEMBACA saja. Menulis ke .docx tetap diblokir hook, dan itu memang disengaja.
"""
from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path

_PARA = re.compile(r"<w:p[ >].*?</w:p>", re.S)
_STYLE = re.compile(r'w:pStyle w:val="([^"]*)"')
_TAG = re.compile(r"<[^>]+>")


def _bersih(xml: str) -> str:
    return html.unescape(_TAG.sub("", xml)).strip()


def teks(path: str | Path) -> str:
    """Seluruh teks dokumen, satu paragraf per baris."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    return html.unescape(_TAG.sub("", xml))


def paragraf(path: str | Path) -> list[tuple[str, str]]:
    """(gaya, teks) untuk tiap paragraf. Gaya kosong bila tanpa style."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    hasil = []
    for p in _PARA.findall(xml):
        st = _STYLE.search(p)
        t = _bersih(p)
        if t:
            hasil.append((st.group(1) if st else "", t))
    return hasil


def judul(path: str | Path) -> list[tuple[str, str]]:
    """Paragraf bergaya heading — struktur dokumen yang sesungguhnya.

    Entri daftar isi disaring keluar: ia menyimpan teks hasil render terakhir,
    yang bisa jauh tertinggal dari judul bab yang sebenarnya.
    """
    return [
        (gaya, t) for gaya, t in paragraf(path)
        if ("eading" in gaya or "Judul" in gaya)
        and "PAGEREF" not in t and "TOC" not in t
    ]


def daftar_isi(path: str | Path) -> list[str]:
    """Isi field daftar isi — dipakai untuk mendeteksi cache yang basi."""
    return [t for gaya, t in paragraf(path) if "PAGEREF" in t or gaya.startswith("TOC")]


def is_docx(path: str | Path) -> bool:
    p = Path(path)
    if p.suffix.lower() != ".docx" or not p.is_file():
        return False
    try:
        with zipfile.ZipFile(p) as z:
            return "word/document.xml" in z.namelist()
    except zipfile.BadZipFile:
        return False
