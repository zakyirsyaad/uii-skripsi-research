"""Klien metadata karya ilmiah: Crossref → OpenAlex → DataCite.

Tiga sumber berjenjang, bukan satu, karena masing-masing punya lubang:
Crossref paling lengkap untuk jurnal/prosiding tapi tidak memuat semua preprint;
OpenAlex punya cakupan lebih luas dan menandai retraksi; DataCite menutupi
dataset dan repositori.

Kegagalan jaringan **tidak pernah** diam-diam menjadi `OK`. Bila ketiga sumber
tidak bisa dihubungi, hasilnya `UNVERIFIED` — beda dari `NOT_FOUND` yang berarti
sumbernya benar-benar dicari dan tidak ada.

Hanya memakai stdlib supaya plugin bisa dipasang tanpa langkah instalasi.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

USER_AGENT_BASE = "uii-skripsi-research/1.0"
CACHE_TTL_SECONDS = 30 * 24 * 3600
DEFAULT_TIMEOUT = 20


class NetworkUnavailable(Exception):
    """Ketiga API tidak bisa dihubungi — hasil harus UNVERIFIED, bukan NOT_FOUND."""


@dataclass
class Work:
    """Metadata kanonik satu karya, dinormalkan lintas API."""
    doi: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str = ""
    publisher: str = ""
    type: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    url: str = ""
    is_retracted: bool = False
    open_access_url: str = ""
    cited_by: int = 0
    api: str = ""

    @property
    def first_author(self) -> str:
        return self.authors[0] if self.authors else ""

    def to_dict(self) -> dict:
        return {
            "doi": self.doi, "title": self.title, "authors": self.authors,
            "year": self.year, "venue": self.venue, "publisher": self.publisher,
            "type": self.type, "volume": self.volume, "issue": self.issue,
            "pages": self.pages, "url": self.url, "is_retracted": self.is_retracted,
            "open_access_url": self.open_access_url, "cited_by": self.cited_by,
            "api": self.api,
        }


# --------------------------------------------------------------------------
# Transport
# --------------------------------------------------------------------------

def _cache_path(cache_dir: Path, url: str) -> Path:
    return cache_dir / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".json")


def fetch_json(
    url: str,
    mailto: str = "",
    cache_dir: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> dict | None:
    """GET JSON dengan cache, polite pool, dan backoff.

    Kembalikan None bila server menjawab 404 (karyanya memang tidak ada).
    Lempar NetworkUnavailable bila jaringan/serverside gagal — pemanggil
    tidak boleh mengartikan kegagalan ini sebagai "tidak ditemukan".
    """
    if cache_dir is not None:
        cached = _cache_path(cache_dir, url)
        if cached.is_file() and (time.time() - cached.stat().st_mtime) < CACHE_TTL_SECONDS:
            try:
                payload = json.loads(cached.read_text(encoding="utf-8"))
                return payload.get("body")
            except (json.JSONDecodeError, OSError):
                pass  # cache rusak: ambil ulang

    ua = f"{USER_AGENT_BASE} (mailto:{mailto})" if mailto else USER_AGENT_BASE
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            if cache_dir is not None:
                cache_dir.mkdir(parents=True, exist_ok=True)
                _cache_path(cache_dir, url).write_text(
                    json.dumps({"url": url, "body": body}), encoding="utf-8")
            return body
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code in (429, 500, 502, 503, 504):
                wait = float(exc.headers.get("Retry-After") or 0) or (2 ** attempt)
                last_error = exc
                if attempt < retries - 1:
                    time.sleep(min(wait, 10))
                    continue
            last_error = exc
            break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            break

    raise NetworkUnavailable(f"{url}: {last_error}")


# --------------------------------------------------------------------------
# Normalisasi per-API
# --------------------------------------------------------------------------

def _crossref_to_work(item: dict) -> Work:
    authors = []
    for a in item.get("author") or []:
        if a.get("name"):                      # penulis korporat: pertahankan utuh
            authors.append(a["name"])
        elif a.get("family"):
            authors.append(a["family"])
    parts = (item.get("issued") or {}).get("date-parts") or [[]]
    year = parts[0][0] if parts and parts[0] else None
    container = item.get("container-title") or []
    updates = item.get("update-to") or []
    return Work(
        doi=(item.get("DOI") or "").lower(),
        title=(item.get("title") or [""])[0],
        authors=authors,
        year=int(year) if isinstance(year, int) else None,
        venue=container[0] if container else "",
        publisher=item.get("publisher") or "",
        type=item.get("type") or "",
        volume=item.get("volume") or "",
        issue=item.get("issue") or "",
        pages=item.get("page") or "",
        url=item.get("URL") or "",
        is_retracted=any(u.get("type") == "retraction" for u in updates),
        api="crossref",
    )


def _openalex_to_work(item: dict) -> Work:
    authors = []
    for a in item.get("authorships") or []:
        name = (a.get("author") or {}).get("display_name") or ""
        if name:
            authors.append(name.split()[-1] if " " in name else name)
    loc = item.get("primary_location") or {}
    src = loc.get("source") or {}
    oa = item.get("best_oa_location") or {}
    doi = (item.get("doi") or "").replace("https://doi.org/", "").lower()
    biblio = item.get("biblio") or {}
    pages = ""
    if biblio.get("first_page"):
        pages = biblio["first_page"]
        if biblio.get("last_page"):
            pages += f"-{biblio['last_page']}"
    return Work(
        doi=doi,
        title=item.get("title") or item.get("display_name") or "",
        authors=authors,
        year=item.get("publication_year"),
        venue=src.get("display_name") or "",
        publisher=src.get("host_organization_name") or "",
        type=item.get("type") or "",
        volume=biblio.get("volume") or "",
        issue=biblio.get("issue") or "",
        pages=pages,
        url=item.get("id") or "",
        is_retracted=bool(item.get("is_retracted")),
        open_access_url=oa.get("pdf_url") or oa.get("landing_page_url") or "",
        cited_by=item.get("cited_by_count") or 0,
        api="openalex",
    )


def _datacite_to_work(item: dict) -> Work:
    attrs = item.get("attributes") or {}
    authors = []
    for c in attrs.get("creators") or []:
        authors.append(c.get("familyName") or c.get("name") or "")
    titles = attrs.get("titles") or [{}]
    return Work(
        doi=(attrs.get("doi") or "").lower(),
        title=titles[0].get("title", "") if titles else "",
        authors=[a for a in authors if a],
        year=attrs.get("publicationYear"),
        venue=(attrs.get("container") or {}).get("title") or "",
        publisher=attrs.get("publisher") or "",
        type=((attrs.get("types") or {}).get("resourceTypeGeneral") or ""),
        url=attrs.get("url") or "",
        api="datacite",
    )


# --------------------------------------------------------------------------
# Klien berjenjang
# --------------------------------------------------------------------------

class MetadataClient:
    def __init__(self, mailto: str = "", cache_dir: Path | None = None,
                 timeout: int = DEFAULT_TIMEOUT):
        self.mailto = mailto
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.unreachable: list[str] = []

    def _get(self, url: str) -> dict | None:
        return fetch_json(url, self.mailto, self.cache_dir, self.timeout)

    def _polite(self, url: str) -> str:
        if not self.mailto:
            return url
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}mailto={urllib.parse.quote(self.mailto)}"

    # -- pencarian berdasarkan DOI ----------------------------------------

    def by_doi(self, doi: str) -> Work | None:
        doi = doi.strip().lower().removeprefix("https://doi.org/").removeprefix("doi:")
        if not doi:
            return None
        reached_any = False

        for name, url, adapt in (
            ("crossref", self._polite(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"),
             lambda b: _crossref_to_work(b["message"])),
            ("openalex", self._polite(f"https://api.openalex.org/works/https://doi.org/{doi}"),
             _openalex_to_work),
            ("datacite", f"https://api.datacite.org/dois/{urllib.parse.quote(doi, safe='')}",
             lambda b: _datacite_to_work(b["data"])),
        ):
            try:
                body = self._get(url)
                reached_any = True
            except NetworkUnavailable:
                self.unreachable.append(name)
                continue
            if body:
                try:
                    return adapt(body)
                except (KeyError, TypeError, IndexError):
                    continue

        if not reached_any:
            raise NetworkUnavailable("Semua API metadata tidak bisa dihubungi.")
        return None

    # -- pencarian berdasarkan judul --------------------------------------

    def search(self, title: str, author: str = "", year: int | None = None,
               rows: int = 5) -> list[Work]:
        works: list[Work] = []
        reached_any = False

        query = " ".join(x for x in (title, author) if x)
        cr = self._polite(
            "https://api.crossref.org/works?"
            + urllib.parse.urlencode({"query.bibliographic": query, "rows": rows})
        )
        try:
            body = self._get(cr)
            reached_any = True
            if body:
                works += [_crossref_to_work(i) for i in body["message"].get("items", [])]
        except (NetworkUnavailable, KeyError, TypeError):
            self.unreachable.append("crossref")

        oa_params = {"search": title, "per-page": rows}
        if year:
            oa_params["filter"] = f"publication_year:{year}"
        oa = self._polite("https://api.openalex.org/works?" + urllib.parse.urlencode(oa_params))
        try:
            body = self._get(oa)
            reached_any = True
            if body:
                works += [_openalex_to_work(i) for i in body.get("results", [])]
        except (NetworkUnavailable, KeyError, TypeError):
            self.unreachable.append("openalex")

        if not reached_any:
            raise NetworkUnavailable("Semua API metadata tidak bisa dihubungi.")
        return works

    # -- pencarian berfilter untuk penjelajahan literatur -------------------

    def search_openalex(
        self,
        query: str,
        since: int | None = None,
        until: int | None = None,
        oa_only: bool = False,
        min_citations: int = 0,
        work_type: str = "",
        limit: int = 20,
    ) -> list[Work]:
        """Pencarian OpenAlex dengan filter. Dipakai penjelajahan, bukan verifikasi.

        OpenAlex dipakai sebagai primer di sini karena filternya paling kaya
        (tahun, open access, jumlah sitasi, jenis karya) dan gratis tanpa kunci.
        """
        filters = []
        if since:
            filters.append(f"from_publication_date:{since}-01-01")
        if until:
            filters.append(f"to_publication_date:{until}-12-31")
        if oa_only:
            filters.append("is_oa:true")
        if min_citations:
            filters.append(f"cited_by_count:>{min_citations - 1}")
        if work_type:
            filters.append(f"type:{work_type}")

        params = {"search": query, "per-page": min(limit, 200)}
        if filters:
            params["filter"] = ",".join(filters)

        url = self._polite("https://api.openalex.org/works?" + urllib.parse.urlencode(params))
        try:
            body = self._get(url)
        except NetworkUnavailable:
            self.unreachable.append("openalex")
            raise
        if not body:
            return []
        return [_openalex_to_work(i) for i in body.get("results", [])]


def url_is_reachable(url: str, timeout: int = 10) -> bool | None:
    """Apakah URL non-DOI masih hidup? None bila tidak bisa disimpulkan.

    Dipakai untuk sumber institusi/artikel yang tidak diindeks basis data
    sitasi. Tautan mati adalah masalah nyata pada daftar pustaka skripsi.
    """
    if not url.lower().startswith(("http://", "https://")):
        return None
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": USER_AGENT_BASE})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 501):
            return None  # server menolak HEAD; bukan berarti tautannya mati
        return exc.code < 400
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None
