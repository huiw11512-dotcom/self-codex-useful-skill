#!/usr/bin/env python3
"""Resolve scholarly literature metadata and authorized OA links.

Uses public metadata/open-access APIs only. It does not download paywalled PDFs,
handle credentials, or bypass publisher access controls.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


USER_AGENT = "literature-retrieval-skill/1.0 (mailto:research@example.com)"
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
FIELDS = [
    "input",
    "match_rank",
    "source",
    "title",
    "doi",
    "year",
    "authors",
    "venue",
    "publisher",
    "landing_url",
    "pdf_url",
    "oa_status",
    "notes",
]


def request_json(url: str, timeout: int = 12, retries: int = 1) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code != 429 or attempt == retries:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 2.0 * (attempt + 1)
            delay = min(delay, 5.0)
            time.sleep(delay)
    raise RuntimeError("unreachable retry state")


def normalize_doi(value: str) -> str | None:
    value = value.strip().strip("<>()[]{}.,;")
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:\s*", "", value, flags=re.IGNORECASE)
    match = DOI_RE.search(value)
    if not match:
        return None
    doi = match.group(0).rstrip(".,;)")
    return doi.lower()


def first(values: list[Any] | None) -> Any:
    return values[0] if values else None


def join_authors(authors: list[str], limit: int = 8) -> str:
    if len(authors) <= limit:
        return "; ".join(authors)
    return "; ".join(authors[:limit]) + f"; et al. ({len(authors)} total)"


def crossref_record_from_message(data: dict[str, Any], original: str, rank: int = 1) -> dict[str, str]:
    authors = []
    for author in data.get("author", []) or []:
        name = " ".join(part for part in [author.get("given"), author.get("family")] if part)
        if name:
            authors.append(name)
    pdf_url = ""
    for link in data.get("link", []) or []:
        if "pdf" in (link.get("content-type") or "").lower():
            pdf_url = link.get("URL", "")
            break
    year = ""
    for key in ("published-print", "published-online", "issued"):
        parts = ((data.get(key) or {}).get("date-parts") or [])
        if parts and parts[0]:
            year = str(parts[0][0])
            break
    return {
        "input": original,
        "match_rank": str(rank),
        "source": "Crossref",
        "title": first(data.get("title")) or "",
        "doi": (data.get("DOI") or "").lower(),
        "year": year,
        "authors": join_authors(authors),
        "venue": first(data.get("container-title")) or "",
        "publisher": data.get("publisher") or "",
        "landing_url": data.get("URL") or (f"https://doi.org/{data.get('DOI')}" if data.get("DOI") else ""),
        "pdf_url": pdf_url,
        "oa_status": "",
        "notes": "metadata",
    }


def crossref_record(doi: str, original: str) -> dict[str, str] | None:
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    data = request_json(url).get("message", {})
    row = crossref_record_from_message(data, original)
    if not row["doi"]:
        row["doi"] = doi
    if not row["landing_url"]:
        row["landing_url"] = f"https://doi.org/{doi}"
    return row


def crossref_search(query: str, limit: int) -> list[dict[str, str]]:
    params = urlencode({"query.bibliographic": query, "rows": max(1, min(limit, 25))})
    url = f"https://api.crossref.org/works?{params}"
    items = request_json(url).get("message", {}).get("items", []) or []
    return [crossref_record_from_message(item, query, index) for index, item in enumerate(items, start=1)]


def authors_from_openalex(work: dict[str, Any]) -> str:
    names = []
    for item in work.get("authorships", []) or []:
        author = item.get("author") or {}
        name = author.get("display_name")
        if name:
            names.append(name)
    return join_authors(names)


def openalex_record_from_work(work: dict[str, Any], original: str, rank: int = 1) -> dict[str, str]:
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    oa = work.get("open_access") or {}
    doi = work.get("doi") or ""
    if doi.lower().startswith("https://doi.org/"):
        doi = doi[16:]
    landing_url = primary.get("landing_page_url") or oa.get("oa_url") or work.get("id") or ""
    pdf_url = primary.get("pdf_url") or ""
    if not pdf_url and oa.get("oa_url", "").lower().endswith(".pdf"):
        pdf_url = oa.get("oa_url") or ""
    return {
        "input": original,
        "match_rank": str(rank),
        "source": "OpenAlex",
        "title": work.get("title") or "",
        "doi": doi.lower(),
        "year": str(work.get("publication_year") or ""),
        "authors": authors_from_openalex(work),
        "venue": source.get("display_name") or "",
        "publisher": source.get("host_organization_name") or "",
        "landing_url": landing_url,
        "pdf_url": pdf_url,
        "oa_status": oa.get("oa_status") or "",
        "notes": "open_access" if oa.get("is_oa") else "metadata",
    }


def openalex_by_doi(doi: str, original: str, email: str | None = None) -> dict[str, str] | None:
    url = f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='/')}"
    if email:
        url += "?" + urlencode({"mailto": email})
    data = request_json(url)
    return openalex_record_from_work(data, original)


def openalex_search(query: str, limit: int, email: str | None = None) -> list[dict[str, str]]:
    params_data = {"search": query, "per-page": max(1, min(limit, 25))}
    if email:
        params_data["mailto"] = email
    params = urlencode(params_data)
    url = f"https://api.openalex.org/works?{params}"
    data = request_json(url)
    rows = []
    for index, work in enumerate(data.get("results", []) or [], start=1):
        rows.append(openalex_record_from_work(work, query, index))
    return rows


def unpaywall_record(doi: str, original: str, email: str) -> dict[str, str] | None:
    params = urlencode({"email": email})
    url = f"https://api.unpaywall.org/v2/{quote(doi, safe='')}?{params}"
    data = request_json(url)
    loc = data.get("best_oa_location") or {}
    return {
        "input": original,
        "match_rank": "1",
        "source": "Unpaywall",
        "title": data.get("title") or "",
        "doi": (data.get("doi") or doi).lower(),
        "year": str(data.get("year") or ""),
        "authors": "",
        "venue": data.get("journal_name") or "",
        "publisher": data.get("publisher") or "",
        "landing_url": loc.get("url") or data.get("doi_url") or f"https://doi.org/{doi}",
        "pdf_url": loc.get("url_for_pdf") or "",
        "oa_status": data.get("oa_status") or "",
        "notes": f"host_type={loc.get('host_type') or ''}".strip("="),
    }


def read_inputs(args: argparse.Namespace) -> list[str]:
    items: list[str] = []
    if args.input:
        for path in args.input:
            text = Path(path).read_text(encoding="utf-8")
            items.extend(line.strip() for line in text.splitlines() if line.strip())
    items.extend(args.doi or [])
    items.extend(args.query or [])
    if not items and not sys.stdin.isatty():
        items.extend(line.strip() for line in sys.stdin.read().splitlines() if line.strip())
    return items


def resolve_item(item: str, email: str | None, limit: int, sleep: float) -> list[dict[str, str]]:
    doi = normalize_doi(item)
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    if doi:
        for source_name, resolver in (
            ("Crossref", lambda: crossref_record(doi, item)),
            ("OpenAlex", lambda: openalex_by_doi(doi, item, email)),
        ):
            try:
                row = resolver()
                if row:
                    rows.append(row)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                errors.append(f"{source_name}: {exc}")
            time.sleep(sleep)
        if email:
            try:
                row = unpaywall_record(doi, item, email)
                if row:
                    rows.append(row)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                errors.append(f"Unpaywall: {exc}")
    else:
        for source_name, resolver in (
            ("OpenAlex search", lambda: openalex_search(item, limit, email)),
            ("Crossref search", lambda: crossref_search(item, limit)),
        ):
            try:
                rows.extend(resolver())
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                errors.append(f"{source_name}: {exc}")
            time.sleep(sleep)
    if not rows:
        rows.append({field: "" for field in FIELDS})
        rows[0].update({"input": item, "source": "", "notes": "not resolved; " + "; ".join(errors)})
    elif errors:
        rows[0]["notes"] = (rows[0].get("notes", "") + "; " + "; ".join(errors)).strip("; ")
    return rows


def write_json(rows: list[dict[str, str]], path: Path) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, str]]) -> str:
    cols = ["match_rank", "source", "title", "doi", "year", "landing_url", "pdf_url", "oa_status", "notes"]
    lines = [
        "|" + "|".join(cols) + "|",
        "|" + "|".join("---" for _ in cols) + "|",
    ]
    for row in rows:
        vals = []
        for col in cols:
            value = (row.get(col) or "").replace("|", "\\|").replace("\n", " ")
            vals.append(value[:300])
        lines.append("|" + "|".join(vals) + "|")
    return "\n".join(lines) + "\n"


def write_output(rows: list[dict[str, str]], out: str | None) -> None:
    if not out:
        sys.stdout.write(markdown_table(rows))
        return
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".json":
        write_json(rows, path)
    elif suffix == ".csv":
        write_csv(rows, path)
    else:
        path.write_text(markdown_table(rows), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", help="Text file with one DOI, title, or query per line.")
    parser.add_argument("--doi", action="append", help="DOI to resolve. May be repeated.")
    parser.add_argument("--query", action="append", help="Title or search query. May be repeated.")
    parser.add_argument("--out", help="Output path: .csv, .json, or Markdown for other extensions.")
    parser.add_argument("--email", help="Public contact email for Unpaywall API lookup.")
    parser.add_argument("--limit", type=int, default=3, help="OpenAlex results per title/query, max 25.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between API requests in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    items = read_inputs(args)
    if not items:
        print("No input provided. Use --doi, --query, --input, or stdin.", file=sys.stderr)
        return 2
    rows: list[dict[str, str]] = []
    for item in items:
        rows.extend(resolve_item(item, args.email, args.limit, args.sleep))
    write_output(rows, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
