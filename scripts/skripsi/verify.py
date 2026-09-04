"""Pencocokan sitasi terhadap metadata kanonik.

Dipisah dari `sources.py` supaya logika keputusannya bisa diuji tanpa jaringan.

Lima status, dan perbedaan di antaranya penting:

- `OK`         — karya ditemukan dan metadata cocok.
- `MISMATCH`   — karyanya ada, tapi metadata yang ditulis salah.
- `NOT_FOUND`  — sudah dicari di semua sumber, karyanya tidak ada.
                 **Dugaan kuat sitasi halusinasi.**
- `RETRACTED`  — karyanya ada tapi sudah ditarik; tidak boleh dipakai.
- `UNVERIFIED` — jaringan gagal. Bukan bukti apa-apa; jangan diperlakukan
                 sebagai OK maupun NOT_FOUND.
- `UNVERIFIABLE`— sumber ini di luar jangkauan Crossref/OpenAlex (halaman
                 institusi, artikel berita). Ketidakhadirannya di sana tidak
                 berarti apa-apa; harus diperiksa manual.

Pembedaan terakhir itu penting: menandai publikasi BPS atau artikel Kontan
sebagai NOT_FOUND berarti menuduh sumber sah sebagai fiktif, hanya karena
basis data sitasi ilmiah memang tidak mengindeks jenis itu.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .sources import (
    MetadataClient, NetworkUnavailable, Work, url_is_reachable,
)

STATUS_OK = "OK"
STATUS_MISMATCH = "MISMATCH"
STATUS_NOT_FOUND = "NOT_FOUND"
STATUS_RETRACTED = "RETRACTED"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_UNVERIFIABLE = "UNVERIFIABLE"

EXIT_CODES = {
    STATUS_OK: 0, STATUS_MISMATCH: 1, STATUS_NOT_FOUND: 2,
    STATUS_UNVERIFIED: 3, STATUS_RETRACTED: 4, STATUS_UNVERIFIABLE: 5,
}

# Jenis sumber yang benar-benar diindeks Crossref/OpenAlex. Hanya untuk jenis
# ini ketidakhadiran menjadi bukti; selebihnya hanya berarti di luar jangkauan.
INDEXED_TYPES = {"jurnal", "prosiding", "buku", "standar"}

TITLE_MATCH = 0.90
TITLE_PLAUSIBLE = 0.75

# Status ledger yang sepadan, untuk ditulis balik ke references/sources.md.
LEDGER_STATUS = {
    STATUS_OK: "verified",
    STATUS_MISMATCH: "mismatch",
    STATUS_NOT_FOUND: "not_found",
    STATUS_RETRACTED: "retracted",
    STATUS_UNVERIFIED: "unverified",
    STATUS_UNVERIFIABLE: "unverifiable",
}


def normalize(text: str) -> str:
    """Buang diakritik, tanda baca, dan beda spasi agar judul bisa dibandingkan."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


@dataclass
class FieldDiff:
    field: str
    ditulis: str
    kanonik: str
    ok: bool
    severity: str = "error"   # error | warning
    note: str = ""


@dataclass
class Claim:
    """Sitasi seperti yang ditulis mahasiswa, sebelum diverifikasi."""
    doi: str = ""
    title: str = ""
    author: str = ""
    year: int | None = None
    id: str = ""
    tipe: str = ""      # jenis sumber; menentukan apakah "tidak ada" bermakna
    url: str = ""       # tautan non-DOI, dicek keterjangkauannya


@dataclass
class Result:
    status: str
    claim: Claim
    work: Work | None = None
    diffs: list[FieldDiff] = field(default_factory=list)
    confidence: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return EXIT_CODES[self.status]

    @property
    def ledger_status(self) -> str:
        return LEDGER_STATUS[self.status]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "confidence": round(self.confidence, 3),
            "ditulis": {
                "id": self.claim.id, "doi": self.claim.doi, "judul": self.claim.title,
                "penulis": self.claim.author, "tahun": self.claim.year,
                "tipe": self.claim.tipe, "url": self.claim.url,
            },
            "kanonik": self.work.to_dict() if self.work else None,
            "selisih": [
                {"field": d.field, "ditulis": d.ditulis, "kanonik": d.kanonik,
                 "ok": d.ok, "severity": d.severity, "catatan": d.note}
                for d in self.diffs
            ],
            "catatan": self.notes,
        }


def compare(claim: Claim, work: Work) -> list[FieldDiff]:
    diffs: list[FieldDiff] = []

    if claim.title:
        sim = similarity(claim.title, work.title)
        if sim >= TITLE_MATCH:
            ok, sev, note = True, "warning", ""
        elif sim >= TITLE_PLAUSIBLE:
            ok, sev, note = False, "warning", f"kemiripan {sim:.0%} — periksa manual"
        else:
            ok, sev, note = False, "error", f"kemiripan hanya {sim:.0%}"
        diffs.append(FieldDiff("judul", claim.title, work.title, ok, sev, note))

    if claim.author:
        want = normalize(claim.author)
        got = [normalize(a) for a in work.authors]
        ok = any(want == g or want in g or g in want for g in got if g)
        diffs.append(FieldDiff(
            "penulis", claim.author, "; ".join(work.authors), ok,
            "error", "" if ok else "tidak ada di daftar penulis kanonik",
        ))

    if claim.year and work.year:
        delta = abs(claim.year - work.year)
        if delta == 0:
            ok, sev, note = True, "warning", ""
        elif delta == 1:
            ok, sev, note = False, "warning", "beda 1 tahun — lazim pada terbitan online-first"
        else:
            ok, sev, note = False, "error", f"beda {delta} tahun"
        diffs.append(FieldDiff("tahun", str(claim.year), str(work.year), ok, sev, note))

    return diffs


def _decide(claim: Claim, work: Work, confidence: float, notes: list[str]) -> Result:
    if work.is_retracted:
        return Result(STATUS_RETRACTED, claim, work, compare(claim, work), confidence,
                      notes + ["Karya ini sudah DITARIK (retracted). Jangan dipakai."])
    diffs = compare(claim, work)
    status = STATUS_MISMATCH if any(
        not d.ok and d.severity == "error" for d in diffs) else STATUS_OK
    return Result(status, claim, work, diffs, confidence, notes)


def _unverifiable(claim: Claim) -> Result:
    """Sumber di luar jangkauan API sitasi ilmiah — periksa manual, jangan tuduh."""
    notes = [
        f"Jenis `{claim.tipe or 'tanpa jenis'}` tidak diindeks Crossref/OpenAlex, "
        "jadi ketidakhadirannya di sana bukan bukti apa pun.",
        "Periksa manual: tautannya masih hidup, penerbit bernama, tanggal terbit "
        "ada, dan lembaga itu benar pemilik datanya.",
    ]
    reachable = url_is_reachable(claim.url) if claim.url else None
    if reachable is False:
        notes.append(f"Tautannya TIDAK bisa dijangkau: {claim.url}")
    elif reachable is True:
        notes.append("Tautannya bisa dijangkau.")
    return Result(STATUS_UNVERIFIABLE, claim, notes=notes)


def verify(claim: Claim, client: MetadataClient) -> Result:
    """Verifikasi satu sitasi. Lewat DOI bila ada, kalau tidak lewat pencarian judul."""
    if claim.doi:
        try:
            work = client.by_doi(claim.doi)
        except NetworkUnavailable as exc:
            return Result(STATUS_UNVERIFIED, claim, notes=[f"Jaringan gagal: {exc}"])
        if work is None:
            return Result(STATUS_NOT_FOUND, claim, notes=[
                "DOI tidak terdaftar di Crossref, OpenAlex, maupun DataCite. "
                "Periksa ulang DOI-nya; bila memang tidak ada, sitasi ini kemungkinan besar fiktif.",
            ])
        return _decide(claim, work, 1.0, [f"Dicocokkan lewat DOI ({work.api})."])

    if not claim.title:
        return Result(STATUS_UNVERIFIED, claim, notes=["Butuh minimal DOI atau judul."])

    # Sumber tanpa DOI yang jenisnya memang tidak diindeks basis data sitasi
    # ilmiah tidak boleh dinilai lewat pencarian judul sama sekali.
    if claim.tipe and claim.tipe not in INDEXED_TYPES:
        return _unverifiable(claim)

    try:
        candidates = client.search(claim.title, claim.author, claim.year)
    except NetworkUnavailable as exc:
        return Result(STATUS_UNVERIFIED, claim, notes=[f"Jaringan gagal: {exc}"])

    if not candidates:
        return Result(STATUS_NOT_FOUND, claim, notes=[
            "Tidak ada kandidat sama sekali untuk judul ini.",
        ])

    scored = sorted(
        ((similarity(claim.title, w.title), w) for w in candidates),
        key=lambda t: t[0], reverse=True,
    )
    best_score, best = scored[0]

    if best_score < TITLE_PLAUSIBLE:
        if claim.tipe and claim.tipe not in INDEXED_TYPES:
            return _unverifiable(claim)
        return Result(STATUS_NOT_FOUND, claim, confidence=best_score, notes=[
            f"Kandidat terdekat hanya mirip {best_score:.0%} "
            f"(“{best.title}”). Judul yang dicari kemungkinan besar tidak ada.",
        ])

    return _decide(claim, best, best_score, [
        f"Dicocokkan lewat pencarian judul, kemiripan {best_score:.0%} ({best.api}). "
        "Tanpa DOI, kecocokan ini lebih lemah daripada pencocokan DOI.",
    ])
