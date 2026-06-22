#!/usr/bin/env python3
"""Extract already-loaded PDF responses from local browser cache.

This is for authorized local browser sessions where an official publisher page
has rendered a PDF but did not save it to Downloads. It does not read cookies,
tokens, passwords, or reconstruct access for unopened documents.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import time
from pathlib import Path


def default_cache_roots() -> list[Path]:
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    home = Path.home()
    roots = [
        local / "Google/Chrome/User Data/Default/Cache/Cache_Data",
        local / "Google/Chrome/User Data/Profile 1/Cache/Cache_Data",
        local / "Microsoft/Edge/User Data/Default/Cache/Cache_Data",
        local / "Microsoft/Edge/User Data/Profile 1/Cache/Cache_Data",
        home / ".cache/google-chrome/Default/Cache/Cache_Data",
        home / ".cache/microsoft-edge/Default/Cache/Cache_Data",
    ]
    return [root for root in roots if root.exists()]


def extract_pdf_bytes(data: bytes) -> bytes | None:
    start = data.find(b"%PDF-")
    if start < 0:
        return None
    pdf = data[start:]
    eof = pdf.rfind(b"%%EOF")
    if eof >= 0:
        pdf = pdf[: eof + 5] + b"\n"
    return pdf


def pdf_text(path: Path, max_pages: int = 2) -> str:
    try:
        try:
            from pypdf import PdfReader
        except Exception:
            from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        chunks: list[str] = []
        for page in reader.pages[:max_pages]:
            chunks.append(page.extract_text() or "")
        return " ".join(" ".join(chunks).split())
    except Exception:
        return ""


def iter_cache_files(roots: list[Path], since_seconds: float, min_size: int):
    cutoff = time.time() - since_seconds if since_seconds > 0 else 0
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            if stat.st_size < min_size or stat.st_mtime < cutoff:
                continue
            yield path, stat


def write_manifest(rows: list[dict[str, str]], manifest: Path) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "output",
        "bytes",
        "sha256",
        "pages_or_text_status",
        "source_cache_file",
        "source_mtime",
        "text_preview",
    ]
    with manifest.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Directory for extracted PDF files.")
    parser.add_argument("--cache-root", action="append", help="Browser cache root. May be repeated.")
    parser.add_argument("--since-minutes", type=float, default=180.0, help="Only scan files modified within this window. Use 0 for all.")
    parser.add_argument("--min-size", type=int, default=100_000, help="Minimum cache file size in bytes.")
    parser.add_argument("--title", action="append", help="Case-insensitive text filter applied to extracted PDF text.")
    parser.add_argument("--dedupe", action="store_true", help="Write only one file per SHA-256 digest.")
    parser.add_argument("--manifest", help="CSV manifest path.")
    args = parser.parse_args()

    roots = [Path(p) for p in args.cache_root] if args.cache_root else default_cache_roots()
    roots = [root for root in roots if root.exists()]
    if not roots:
        print("No browser cache roots found.", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    rows: list[dict[str, str]] = []
    filters = [item.casefold() for item in (args.title or [])]

    for source, stat in iter_cache_files(roots, args.since_minutes * 60.0, args.min_size):
        try:
            data = source.read_bytes()
        except OSError:
            continue
        pdf = extract_pdf_bytes(data)
        if not pdf:
            continue
        digest = hashlib.sha256(pdf).hexdigest().upper()
        if args.dedupe and digest in seen:
            continue
        seen.add(digest)
        output = out_dir / f"{source.name}_{len(pdf)}.pdf"
        output.write_bytes(pdf)
        text = pdf_text(output)
        if filters and not all(item in text.casefold() for item in filters):
            output.unlink(missing_ok=True)
            continue
        pages_status = "text-ok" if text else "text-unavailable"
        rows.append(
            {
                "output": str(output),
                "bytes": str(len(pdf)),
                "sha256": digest,
                "pages_or_text_status": pages_status,
                "source_cache_file": str(source),
                "source_mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                "text_preview": text[:500],
            }
        )

    if args.manifest:
        write_manifest(rows, Path(args.manifest))
    else:
        for row in rows:
            print(f"{row['output']}\t{row['bytes']}\t{row['sha256']}\t{row['text_preview'][:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
