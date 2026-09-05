"""Audit daftar pustaka. Murni aritmetika dan pencocokan — tanpa jaringan.

Semua yang di sini dulunya adalah aturan prosa yang "diharapkan diingat model":
kuota 20%, batas kebaruan, kelengkapan metadata. Sekarang dihitung.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .config import Config
from .ledger import Source
from .verify import similarity

# Buku dan standar boleh tua: teori mendasar dan standar resmi tidak kedaluwarsa
# seperti bukti empiris. Selebihnya tunduk pada batas kebaruan.
RECENCY_EXEMPT = {"buku", "standar"}

VERDICT_READY = "ready"
VERDICT_NOTES = "ready_with_notes"
VERDICT_NOT_READY = "not_ready"

TITLE_DUPLICATE = 0.92


@dataclass
class Finding:
    level: str          # blocker | warning | info
    code: str
    message: str
    lines: list[int] = field(default_factory=list)

    def __str__(self) -> str:
        where = f" (baris {', '.join(map(str, self.lines))})" if self.lines else ""
        return f"[{self.level.upper()}] {self.message}{where}"


@dataclass
class AuditReport:
    total: int = 0
    academic: int = 0
    articles: int = 0
    article_cap: int = 0
    verified: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def blockers(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "blocker"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warning"]

    @property
    def verdict(self) -> str:
        if self.blockers:
            return VERDICT_NOT_READY
        return VERDICT_NOTES if self.warnings else VERDICT_READY

    @property
    def exit_code(self) -> int:
        return 1 if self.blockers else 0


def audit_sources(sources: list[Source], cfg: Config,
                  ref_year: int | None = None) -> AuditReport:
    ref_year = ref_year or date.today().year
    rep = AuditReport(total=len(sources))

    if not sources:
        rep.findings.append(Finding("blocker", "empty", "Source ledger kosong."))
        return rep

    academic = [s for s in sources if s.is_academic]
    articles = [s for s in sources if not s.is_academic]
    rep.academic = len(academic)
    rep.articles = len(articles)
    rep.article_cap = cfg.article_cap(len(sources))
    rep.verified = sum(1 for s in sources if s.is_verified)

    # -- kuota sumber non-akademik ---------------------------------------
    if rep.articles > rep.article_cap:
        rep.findings.append(Finding(
            "blocker", "article_cap",
            f"Sumber non-akademik {rep.articles} melebihi kuota {rep.article_cap} "
            f"(= floor({rep.total} × {cfg.article_cap_ratio:.0%})). "
            f"Kurangi {rep.articles - rep.article_cap} artikel atau tambah sumber akademik.",
            [s.line for s in articles],
        ))
    elif rep.articles == rep.article_cap and rep.article_cap > 0:
        rep.findings.append(Finding(
            "warning", "article_cap_full",
            f"Kuota non-akademik terpakai penuh ({rep.articles}/{rep.article_cap}). "
            "Menambah satu artikel lagi akan melanggar batas.",
        ))

    # -- sumber `institusi` minta konfirmasi -------------------------------
    # `institusi` masuk ACADEMIC_TYPES, jadi TIDAK dihitung dalam kuota 20%.
    # Artinya melabeli ulang sebuah `artikel` menjadi `institusi` benar-benar
    # menghapus pelanggaran kuota, dan tidak ada cara mesin memutuskan apakah
    # sebuah lembaga betul pemilik datanya. Yang bisa dilakukan skrip adalah
    # menolak diam: daftarkan tiap sumber `institusi` supaya keputusannya
    # dibuat sadar, bukan lolos begitu saja.
    institusi = [s for s in sources if s.tipe == "institusi"]
    if institusi:
        rep.findings.append(Finding(
            "warning", "institusi_konfirmasi",
            f"{len(institusi)} sumber `institusi` tidak dihitung dalam kuota "
            f"non-akademik: {', '.join(s.id for s in institusi)}. Pastikan tiap "
            "lembaga itu benar PEMILIK datanya, bukan penerbit berita atau "
            "explainer yang dilabeli ulang. Bila salah satunya sebenarnya "
            "`artikel`, ubah `tipe`-nya dan jalankan ulang.",
            [s.line for s in institusi],
        ))

    # -- status verifikasi ------------------------------------------------
    by_status: dict[str, list[Source]] = {}
    for s in sources:
        by_status.setdefault(s.status_verifikasi, []).append(s)

    for status, level, msg in (
        ("not_found", "blocker",
         "tidak ditemukan di Crossref/OpenAlex/DataCite — dugaan kuat sitasi fiktif"),
        ("retracted", "blocker", "sudah DITARIK (retracted) dan tidak boleh dipakai"),
        ("mismatch", "blocker", "metadatanya tidak cocok dengan rekaman kanonik"),
        ("unverified", "warning", "belum diverifikasi"),
        ("unverifiable", "warning",
         "di luar jangkauan Crossref/OpenAlex — periksa manual bahwa tautannya "
         "hidup, penerbitnya bernama, dan tanggalnya ada"),
    ):
        hits = by_status.get(status, [])
        if hits:
            rep.findings.append(Finding(
                level, f"status_{status}",
                f"{len(hits)} sumber {msg}: {', '.join(s.id for s in hits)}",
                [s.line for s in hits],
            ))

    # -- kebaruan ---------------------------------------------------------
    stale = [
        s for s in sources
        if s.tipe not in RECENCY_EXEMPT and s.tahun
        and (ref_year - s.tahun) > cfg.recency_years
    ]
    if stale:
        rep.findings.append(Finding(
            "warning", "recency",
            f"{len(stale)} sumber lebih tua dari {cfg.recency_years} tahun "
            f"({', '.join(f'{s.id}:{s.tahun}' for s in stale)}). "
            "Justifikasi terpisah bila ini teori/metode mendasar.",
            [s.line for s in stale],
        ))

    # -- kelengkapan metadata ---------------------------------------------
    no_link = [s for s in sources if not s.doi_url.strip()]
    if no_link:
        rep.findings.append(Finding(
            "warning", "missing_link",
            f"{len(no_link)} sumber tanpa DOI maupun URL stabil: "
            f"{', '.join(s.id for s in no_link)}. Tidak bisa diverifikasi otomatis.",
            [s.line for s in no_link],
        ))

    academic_no_venue = [s for s in academic if not s.venue.strip()]
    if academic_no_venue:
        rep.findings.append(Finding(
            "warning", "missing_venue",
            f"{len(academic_no_venue)} sumber akademik tanpa venue/penerbit: "
            f"{', '.join(s.id for s in academic_no_venue)}.",
            [s.line for s in academic_no_venue],
        ))

    # -- duplikat ---------------------------------------------------------
    # Kunci identitas: DOI bila ada, kalau tidak URL stabil yang dinormalkan.
    # Tanpa fallback URL, duplikat sumber institusi/web tidak akan pernah ketahuan.
    seen: dict[str, Source] = {}
    for s in sources:
        key = s.doi or s.doi_url.strip().rstrip("/").lower()
        if not key:
            continue
        if key in seen:
            rep.findings.append(Finding(
                "warning", "duplicate_doi",
                f"Tautan ganda antara {seen[key].id} dan {s.id}: {key}",
                [seen[key].line, s.line],
            ))
        else:
            seen[key] = s

    # Kelompokkan judul mirip jadi klaster, bukan laporkan tiap pasangan: lima
    # judul serupa menghasilkan sepuluh pasangan dan membanjiri keluaran.
    clusters: list[list[Source]] = []
    for s in sources:
        if not s.judul:
            continue
        for cluster in clusters:
            if similarity(cluster[0].judul, s.judul) >= TITLE_DUPLICATE:
                cluster.append(s)
                break
        else:
            clusters.append([s])

    for cluster in clusters:
        if len(cluster) < 2:
            continue
        # DOI/tautan identik sudah dilaporkan di atas; jangan laporkan dua kali.
        keys = {s.doi or s.doi_url.strip().rstrip("/").lower() for s in cluster}
        if len(keys) == 1 and keys != {""}:
            continue
        rep.findings.append(Finding(
            "warning", "duplicate_title",
            f"{len(cluster)} entri berjudul nyaris identik "
            f"({', '.join(s.id for s in cluster)}) — mungkin karya yang sama "
            "dicatat berulang, atau versi preprint dan versi terbit.",
            [s.line for s in cluster],
        ))

    return rep
