"""Parser untuk dua artefak Markdown milik proyek skripsi.

- `references/sources.md`  — source ledger (tabel berkontrak ketat)
- `references/thesis-context.md` — ledger kontinuitas antar-sesi

Keduanya sengaja Markdown, bukan YAML/JSON: mahasiswa harus bisa membaca dan
menyuntingnya di editor apa pun. Konsekuensinya parser di sini harus ketat dan
melaporkan nomor baris, supaya kesalahan format bisa diperbaiki tanpa menebak.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .minyaml import MiniYamlError
from .minyaml import safe_load as _yaml_load

SOURCE_COLUMNS = [
    "id", "tipe", "penulis", "tahun", "judul", "venue",
    "doi_url", "klaim", "status_verifikasi", "tgl_verifikasi",
]
DECISION_COLUMNS = [
    "id", "kind", "pernyataan", "status", "provenance", "scope", "pengganti",
]
ARTIFACT_COLUMNS = ["peran", "path"]
# Item terbuka boleh berupa tabel berstatus, bukan sekadar checkbox. Bentuk tabel
# ini lebih kaya — ia membedakan yang selesai dari yang digantikan, dan mencatat
# dampaknya — jadi didukung sebagai warga kelas satu, bukan sekadar kompatibilitas.
ITEM_COLUMNS = ["id", "item", "status", "dampak"]

ACADEMIC_TYPES = {"jurnal", "prosiding", "buku", "standar", "institusi"}
ARTICLE_TYPES = {"artikel"}
SOURCE_TYPES = ACADEMIC_TYPES | ARTICLE_TYPES

VERIFY_STATES = {"verified", "unverified", "unverifiable", "mismatch",
                 "not_found", "retracted"}
DECISION_KINDS = {"factual_claim", "user_decision", "assistant_proposal", "inference"}
DECISION_STATES = {"proposed", "approved", "rejected", "superseded", "unconfirmed"}
WORD_SYNC_STATES = {"unknown", "markdown_newer", "word_newer", "in_sync"}
ITEM_STATES = {"open", "resolved", "superseded"}
UNIT_STATES = {"draft", "awaiting_review", "approved", "revision_requested", "superseded"}

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SEPARATOR_ROW = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


@dataclass
class Issue:
    line: int
    field: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        where = f"baris {self.line}" if self.line else "dokumen"
        return f"[{self.severity}] {where} ({self.field}): {self.message}"


@dataclass
class Source:
    id: str = ""
    tipe: str = ""
    penulis: str = ""
    tahun: int | None = None
    judul: str = ""
    venue: str = ""
    doi_url: str = ""
    klaim: str = ""
    status_verifikasi: str = "unverified"
    tgl_verifikasi: str = ""
    line: int = 0

    @property
    def is_academic(self) -> bool:
        return self.tipe in ACADEMIC_TYPES

    @property
    def is_verified(self) -> bool:
        return self.status_verifikasi == "verified"

    @property
    def doi(self) -> str:
        """DOI telanjang bila `doi_url` memuat DOI; string kosong bila hanya URL."""
        m = re.search(r"\b(10\.\d{4,9}/\S+)", self.doi_url)
        return m.group(1).rstrip(".,;)") if m else ""


@dataclass
class Decision:
    id: str = ""
    kind: str = ""
    pernyataan: str = ""
    status: str = ""
    provenance: str = ""
    scope: str = ""
    pengganti: str = ""
    line: int = 0


@dataclass
class OpenItem:
    id: str = ""
    item: str = ""
    status: str = "open"
    dampak: str = ""
    line: int = 0

    @property
    def is_open(self) -> bool:
        return self.status == "open"

    def __str__(self) -> str:
        return f"[{self.id}] {self.item}" if self.id else self.item


@dataclass
class ThesisContext:
    schema_version: int = 1
    project_id: str = ""
    last_checkpoint_at: str = ""
    last_checkpoint_source: str = ""
    word_sync_status: str = "unknown"
    active_unit: str = ""
    active_artifact: str = ""
    active_workstream: str = ""
    active_unit_status: str = ""
    decisions: list[Decision] = field(default_factory=list)
    items: list[OpenItem] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)

    @property
    def approved_decisions(self) -> list[Decision]:
        return [d for d in self.decisions if d.status == "approved"]

    @property
    def open_items(self) -> list[OpenItem]:
        """Hanya yang benar-benar belum selesai — bukan yang resolved/superseded."""
        return [i for i in self.items if i.is_open]


# --------------------------------------------------------------------------
# Primitif tabel Markdown
# --------------------------------------------------------------------------

def _split_row(row: str) -> list[str]:
    """Pecah baris tabel, menghormati pipa ter-escape (`\\|`) di dalam sel."""
    body = row.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith(r"\|"):
        body = body[:-1]
    cells = re.split(r"(?<!\\)\|", body)
    return [c.strip().replace(r"\|", "|") for c in cells]


def _find_table(lines: list[str], expected: list[str]) -> tuple[int, list[str]] | None:
    """Cari tabel yang headernya persis `expected`. Kembalikan (idx_header, header)."""
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        cells = [c.lower() for c in _split_row(line)]
        if cells == expected:
            return i, cells
    return None


def _looks_like_table_header(line: str, expected: list[str]) -> bool:
    """Header yang *hampir* cocok — dipakai untuk pesan error yang berguna."""
    if "|" not in line:
        return False
    cells = {c.lower() for c in _split_row(line)}
    return len(cells & set(expected)) >= max(2, len(expected) // 2)


def _table_rows(lines: list[str], header_idx: int, width: int):
    """Hasilkan (nomor_baris_1indexed, sel) untuk tiap baris data setelah header."""
    for offset, line in enumerate(lines[header_idx + 1:], start=header_idx + 2):
        if not line.strip():
            break
        if "|" not in line:
            break
        if _SEPARATOR_ROW.match(line):
            continue
        yield offset, _split_row(line)


def _column_issue(lines: list[str], expected: list[str], label: str) -> Issue:
    """Bangun error yang menyebut kolom mana yang salah/hilang."""
    for i, line in enumerate(lines, start=1):
        if _looks_like_table_header(line, expected):
            found = [c.lower() for c in _split_row(line)]
            missing = [c for c in expected if c not in found]
            extra = [c for c in found if c not in expected]
            parts = []
            if missing:
                parts.append(f"kolom hilang: {', '.join(missing)}")
            if extra:
                parts.append(f"kolom asing: {', '.join(extra)}")
            if not parts:
                parts.append(f"urutan kolom harus persis: {' | '.join(expected)}")
            return Issue(i, "header", f"Header tabel {label} tidak sesuai — " + "; ".join(parts))
    return Issue(
        0, "header",
        f"Tabel {label} tidak ditemukan. Header wajib: | {' | '.join(expected)} |",
    )


# --------------------------------------------------------------------------
# Source ledger
# --------------------------------------------------------------------------

def parse_sources(text: str) -> tuple[list[Source], list[Issue]]:
    lines = text.splitlines()
    issues: list[Issue] = []

    found = _find_table(lines, SOURCE_COLUMNS)
    if found is None:
        return [], [_column_issue(lines, SOURCE_COLUMNS, "source ledger")]

    header_idx, _ = found
    sources: list[Source] = []
    seen_ids: dict[str, int] = {}

    for lineno, cells in _table_rows(lines, header_idx, len(SOURCE_COLUMNS)):
        if len(cells) != len(SOURCE_COLUMNS):
            issues.append(Issue(
                lineno, "row",
                f"Baris punya {len(cells)} kolom, seharusnya {len(SOURCE_COLUMNS)}. "
                r"Escape pipa di dalam sel sebagai \|.",
            ))
            continue

        row = dict(zip(SOURCE_COLUMNS, cells))
        src = Source(line=lineno, **{k: row[k] for k in SOURCE_COLUMNS if k != "tahun"})

        if not src.id:
            issues.append(Issue(lineno, "id", "`id` tidak boleh kosong."))
        elif src.id in seen_ids:
            issues.append(Issue(
                lineno, "id",
                f"`id` ganda: {src.id} sudah dipakai di baris {seen_ids[src.id]}.",
            ))
        else:
            seen_ids[src.id] = lineno

        if src.tipe not in SOURCE_TYPES:
            issues.append(Issue(
                lineno, "tipe",
                f"`tipe` tidak dikenal: {src.tipe!r}. Pilih salah satu: "
                f"{', '.join(sorted(SOURCE_TYPES))}.",
            ))

        raw_year = row["tahun"]
        if raw_year:
            if raw_year.isdigit() and 1000 <= int(raw_year) <= 2999:
                src.tahun = int(raw_year)
            else:
                issues.append(Issue(
                    lineno, "tahun", f"`tahun` harus empat digit, dapat {raw_year!r}."))
        else:
            issues.append(Issue(lineno, "tahun", "`tahun` tidak boleh kosong."))

        if src.status_verifikasi not in VERIFY_STATES:
            issues.append(Issue(
                lineno, "status_verifikasi",
                f"Status tidak dikenal: {src.status_verifikasi!r}. Pilih: "
                f"{', '.join(sorted(VERIFY_STATES))}.",
            ))

        if src.tgl_verifikasi and not _ISO_DATE.match(src.tgl_verifikasi):
            issues.append(Issue(
                lineno, "tgl_verifikasi",
                f"Tanggal harus ISO YYYY-MM-DD, dapat {src.tgl_verifikasi!r}.",
            ))

        if src.is_verified and not src.tgl_verifikasi:
            issues.append(Issue(
                lineno, "tgl_verifikasi",
                "Entri `verified` wajib punya tanggal verifikasi.", "warning",
            ))

        if not src.klaim:
            issues.append(Issue(
                lineno, "klaim",
                "Sumber tanpa klaim tidak bisa diaudit — sebutkan klaim yang didukung.",
                "warning",
            ))

        sources.append(src)

    return sources, issues


def load_sources(path: str | Path) -> tuple[list[Source], list[Issue]]:
    p = Path(path)
    if not p.is_file():
        return [], [Issue(0, "file", f"Source ledger tidak ditemukan: {p}")]
    return parse_sources(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Context ledger
# --------------------------------------------------------------------------

def _parse_frontmatter(lines: list[str]) -> tuple[dict, list[Issue]]:
    if not lines or lines[0].strip() != "---":
        return {}, [Issue(
            1, "frontmatter",
            "Ledger konteks wajib diawali frontmatter YAML di antara garis `---`.",
        )]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, [Issue(1, "frontmatter", "Frontmatter tidak pernah ditutup dengan `---`.")]

    try:
        data = _yaml_load("\n".join(lines[1:end])) or {}
    except MiniYamlError as exc:
        # Nomor baris dari parser relatif ke isi frontmatter; geser 1
        # agar menunjuk baris sebenarnya di berkas.
        return {}, [Issue(exc.line + 1, "frontmatter",
                          f"Frontmatter tidak valid: {exc.message}")]

    if not isinstance(data, dict):
        return {}, [Issue(1, "frontmatter", "Frontmatter harus berupa peta kunci-nilai.")]
    return data, []


def parse_context(text: str) -> tuple[ThesisContext, list[Issue]]:
    lines = text.splitlines()
    meta, issues = _parse_frontmatter(lines)

    ctx = ThesisContext(
        schema_version=int(meta.get("schema_version") or 1),
        project_id=str(meta.get("project_id") or ""),
        last_checkpoint_at=str(meta.get("last_checkpoint_at") or ""),
        last_checkpoint_source=str(meta.get("last_checkpoint_source") or ""),
        word_sync_status=str(meta.get("word_sync_status") or "unknown"),
        active_unit=str(meta.get("active_unit") or ""),
        active_artifact=str(meta.get("active_artifact")
                           or meta.get("active_markdown_artifact") or ""),
        active_workstream=str(meta.get("active_workstream") or ""),
        active_unit_status=str(meta.get("active_unit_status") or ""),
    )

    if meta and not ctx.project_id:
        issues.append(Issue(1, "project_id", "`project_id` wajib diisi agar konteks "
                                             "satu proyek tidak terbawa ke proyek lain."))

    if ctx.word_sync_status not in WORD_SYNC_STATES:
        issues.append(Issue(
            1, "word_sync_status",
            f"Status sinkronisasi Word tidak dikenal: {ctx.word_sync_status!r}. "
            f"Pilih: {', '.join(sorted(WORD_SYNC_STATES))}.",
        ))

    if ctx.last_checkpoint_at and not _ISO_DATE.match(ctx.last_checkpoint_at):
        issues.append(Issue(
            1, "last_checkpoint_at",
            f"Tanggal harus ISO YYYY-MM-DD, dapat {ctx.last_checkpoint_at!r}.",
        ))

    # Tabel keputusan bersifat opsional: ledger baru boleh belum punya keputusan.
    found = _find_table(lines, DECISION_COLUMNS)
    if found is not None:
        header_idx, _ = found
        seen: dict[str, int] = {}
        for lineno, cells in _table_rows(lines, header_idx, len(DECISION_COLUMNS)):
            if len(cells) != len(DECISION_COLUMNS):
                issues.append(Issue(
                    lineno, "row",
                    f"Baris keputusan punya {len(cells)} kolom, "
                    f"seharusnya {len(DECISION_COLUMNS)}.",
                ))
                continue
            row = dict(zip(DECISION_COLUMNS, cells))
            dec = Decision(line=lineno, **row)

            if dec.id in seen:
                issues.append(Issue(
                    lineno, "id",
                    f"`id` keputusan ganda: {dec.id} (lihat baris {seen[dec.id]}).",
                ))
            elif dec.id:
                seen[dec.id] = lineno

            if dec.kind not in DECISION_KINDS:
                issues.append(Issue(
                    lineno, "kind",
                    f"`kind` tidak dikenal: {dec.kind!r}. Pilih: "
                    f"{', '.join(sorted(DECISION_KINDS))}.",
                ))
            if dec.status not in DECISION_STATES:
                issues.append(Issue(
                    lineno, "status",
                    f"`status` tidak dikenal: {dec.status!r}. Pilih: "
                    f"{', '.join(sorted(DECISION_STATES))}.",
                ))
            if dec.status == "superseded" and not dec.pengganti:
                issues.append(Issue(
                    lineno, "pengganti",
                    "Keputusan `superseded` harus menyebut id penggantinya.", "warning",
                ))
            if not dec.provenance:
                issues.append(Issue(
                    lineno, "provenance",
                    "Keputusan tanpa provenance tidak bisa dipercaya lintas sesi.",
                    "warning",
                ))
            ctx.decisions.append(dec)
    elif any(_looks_like_table_header(ln, DECISION_COLUMNS) for ln in lines):
        issues.append(_column_issue(lines, DECISION_COLUMNS, "keputusan"))

    if ctx.active_unit_status and ctx.active_unit_status not in UNIT_STATES:
        issues.append(Issue(
            1, "active_unit_status",
            f"Status unit tidak dikenal: {ctx.active_unit_status!r}. "
            f"Pilih: {', '.join(sorted(UNIT_STATES))}.",
        ))

    # Bentuk tabel lebih dulu; bila tidak ada, jatuh ke checkbox sederhana.
    found = _find_table(lines, ITEM_COLUMNS)
    if found is not None:
        header_idx, _ = found
        for lineno, cells in _table_rows(lines, header_idx, len(ITEM_COLUMNS)):
            if len(cells) != len(ITEM_COLUMNS):
                issues.append(Issue(
                    lineno, "row",
                    f"Baris item punya {len(cells)} kolom, "
                    f"seharusnya {len(ITEM_COLUMNS)}.",
                ))
                continue
            row = dict(zip(ITEM_COLUMNS, cells))
            item = OpenItem(line=lineno, **row)
            if item.status not in ITEM_STATES:
                issues.append(Issue(
                    lineno, "status",
                    f"Status item tidak dikenal: {item.status!r}. "
                    f"Pilih: {', '.join(sorted(ITEM_STATES))}.",
                ))
            ctx.items.append(item)
    else:
        for lineno, line in enumerate(lines, start=1):
            m = re.match(r"^\s*[-*]\s*\[([ xX])\]\s+(.+?)\s*$", line)
            if m:
                ctx.items.append(OpenItem(
                    item=m.group(2), line=lineno,
                    status="open" if m.group(1) == " " else "resolved",
                ))

    found = _find_table(lines, ARTIFACT_COLUMNS)
    if found is not None:
        header_idx, _ = found
        for _lineno, cells in _table_rows(lines, header_idx, len(ARTIFACT_COLUMNS)):
            if len(cells) == len(ARTIFACT_COLUMNS) and cells[0]:
                ctx.artifacts[cells[0]] = cells[1]

    return ctx, issues


def load_context(path: str | Path) -> tuple[ThesisContext, list[Issue]]:
    p = Path(path)
    if not p.is_file():
        return ThesisContext(), [Issue(0, "file", f"Ledger konteks tidak ditemukan: {p}")]
    return parse_context(p.read_text(encoding="utf-8"))


def errors(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == "error"]


def warnings(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == "warning"]


def today() -> str:
    return date.today().isoformat()


# --------------------------------------------------------------------------
# Penulisan balik ke source ledger
# --------------------------------------------------------------------------

def _join_row(cells: list[str]) -> str:
    escaped = [c.replace("|", r"\|") for c in cells]
    return "| " + " | ".join(escaped) + " |"


def update_source_rows(text: str, updates: dict[str, tuple[str, str]]) -> str:
    """Tulis balik `status_verifikasi` dan `tgl_verifikasi` untuk id tertentu.

    Hanya dua kolom itu yang disentuh; kolom lain — termasuk yang ditulis
    mahasiswa — dibiarkan apa adanya. `updates` memetakan id sumber ke
    (status, tanggal ISO).
    """
    lines = text.splitlines(keepends=True)
    stripped = [ln.rstrip("\n").rstrip("\r") for ln in lines]

    found = _find_table(stripped, SOURCE_COLUMNS)
    if found is None:
        return text

    header_idx, _ = found
    i_status = SOURCE_COLUMNS.index("status_verifikasi")
    i_date = SOURCE_COLUMNS.index("tgl_verifikasi")

    for idx in range(header_idx + 1, len(stripped)):
        line = stripped[idx]
        if not line.strip() or "|" not in line:
            break
        if _SEPARATOR_ROW.match(line):
            continue
        cells = _split_row(line)
        if len(cells) != len(SOURCE_COLUMNS):
            continue
        if cells[0] in updates:
            status, when = updates[cells[0]]
            cells[i_status] = status
            cells[i_date] = when
            newline = "\n" if lines[idx].endswith("\n") else ""
            lines[idx] = _join_row(cells) + newline

    return "".join(lines)
