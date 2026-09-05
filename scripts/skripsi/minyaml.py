"""Parser untuk subhimpunan YAML datar yang dipakai plugin ini.

Kenapa bukan PyYAML: PyYAML bukan pustaka standar. Menjadikannya syarat berarti
plugin gagal dipasang di laptop yang tidak punya, padahal kedua berkas yang kita
parse — `.skripsi.yaml` dan frontmatter ledger — formatnya kita sendiri yang
tentukan dan seluruhnya datar.

Memakai PyYAML "kalau tersedia" justru lebih buruk: perilakunya jadi berbeda
antar mesin. Parser sendiri memberi hasil identik di mana pun, dan bisa
melaporkan nomor baris seperti parser lain di plugin ini.

Yang didukung: `kunci: nilai`, komentar, string berkutip, integer, float,
boolean, dan nilai kosong. Yang TIDAK didukung — dan dilaporkan sebagai galat,
bukan diabaikan diam-diam: struktur bersarang, daftar, dan blok multibaris.
"""
from __future__ import annotations

import re

_TRUE = {"true", "yes", "on"}
_FALSE = {"false", "no", "off"}
_NULL = {"", "null", "~"}
_KEY_LINE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z_][\w.-]*)\s*:(?P<rest>.*)$")


class MiniYamlError(ValueError):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
        super().__init__(f"baris {line}: {message}")


def _strip_comment(text: str) -> str:
    """Buang komentar, hormati tanda kutip."""
    out, quote = [], None
    for ch in text:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).strip()


def _coerce(raw: str, lineno: int):
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    low = raw.lower()
    if low in _NULL:
        return None
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    if re.fullmatch(r"[+-]?\d+", raw):
        return int(raw)
    if re.fullmatch(r"[+-]?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?", raw):
        return float(raw)
    if raw.startswith(("[", "{", "-")):
        raise MiniYamlError(lineno, "daftar dan struktur bersarang tidak didukung")
    return raw


def safe_load(text: str) -> dict:
    """Parse pemetaan datar. Lempar MiniYamlError untuk yang di luar dukungan."""
    data: dict = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        body = _strip_comment(line)
        if not body:
            continue
        if body == "---":
            continue

        m = _KEY_LINE.match(line)
        if not m:
            if body.startswith("-"):
                raise MiniYamlError(lineno, "daftar YAML tidak didukung")
            raise MiniYamlError(lineno, f"tidak bisa diurai: {body!r}")
        if m.group("indent"):
            raise MiniYamlError(lineno, "struktur bersarang tidak didukung")

        key = m.group("key")
        raw = _strip_comment(m.group("rest"))
        if raw in ("|", ">"):
            raise MiniYamlError(lineno, "blok multibaris tidak didukung")
        if key in data:
            raise MiniYamlError(lineno, f"kunci ganda: {key}")
        data[key] = _coerce(raw, lineno)

    return data
