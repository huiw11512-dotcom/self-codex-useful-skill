---
name: literature-retrieval
description: Find, rank, verify, download, and organize scholarly literature metadata and authorized full text/PDFs from DOI lists, titles, citations, search queries, BibTeX/RIS, publisher pages, IEEE Xplore, CNKI, ACM, ScienceDirect, SpringerLink, Wiley, arXiv, PubMed/PMC, institutional proxies, and open repositories. Use for quality-first literature searches, authenticated/manual-login publisher workflows, bibliography export, and paper collection. Rank by relevance, venue quality, authority, citation influence, recency, and coverage of the user's technical problem; do not prefer open access over higher-quality authorized sources. If a selected target remains paywalled after user authorization, list DOI and citation/access status instead of replacing it automatically. Never use Sci-Hub, mirrors, credential scraping, paywall bypass, captcha circumvention, or automated mass downloading that violates site terms.
---

# Literature Retrieval

## Overview

Use this skill to locate high-quality papers, resolve metadata, rank candidates, and collect PDFs through authorized sources. Treat the user's subscriptions, institutional access, and browser login sessions as primary access routes, not as credentials to copy, store, or automate outside the active session.

## Access Rules

- Use lawful sources only: publisher pages available through the user's subscription, institutional proxy/link resolver, library discovery tools, open access, preprint servers, author repositories, PubMed Central, arXiv, or interlibrary loan.
- Do not use Sci-Hub, LibGen mirrors, leaked credentials, shared accounts, paywall bypasses, captcha workarounds, or cookie/token extraction.
- Do not ask the user to paste passwords, cookies, session tokens, or institutional secrets. If login is required, ask the user to sign in manually in the browser, then continue from the authenticated page.
- Avoid bulk downloading unless the platform terms and the user's license allow it. Use small batches, visible progress, and source logs.
- Do not make Computer Use/UI clicking the default retrieval path. Prefer official URLs opened in the user's already-authorized local browser, then monitor the download folder or extract already-loaded PDF responses from the local browser cache.
- Cache extraction is only for PDFs that the authorized local browser has already loaded from official pages. Do not extract cookies, tokens, signed URLs, passwords, or attempt to reconstruct access for unopened documents.
- If a high-quality target is blocked by authentication, stop and ask the user to complete login/authorization in the browser, then continue from the authenticated page. Do not immediately downgrade to an OA/preprint alternative unless the user asks for alternatives or authorization is unavailable.
- If a requested paper still requires payment or has no full-text entitlement after the user completes available authorization, do not automatically replace it with an easier paper. Add it to a "not downloaded" list with DOI, title, authors, venue, year, official URL, access status, and recommended next step.
- If a requested paper is not available through authorized routes after the user has had a chance to authorize access, report that clearly and offer alternatives: library request, author contact, DOI/publisher landing page, citation-only export, or OA/preprint search.

## Workflow

1. Normalize the request.
   - Extract DOI values, titles, citations, authors, year hints, venues, and requested output format.
   - If the user does not specify a destination, use a local `literature/` folder in the current workspace.
   - For lists, deduplicate by DOI first, then normalized title.

2. Resolve metadata and candidate access links.
   - Use `scripts/resolve_literature.py` for DOI/title/query batches before browsing.
   - Prefer DOI and publisher landing pages over search-engine snippets.
   - Record source, DOI, title, year, authors, venue, landing URL, OA URL/PDF URL, and retrieval status.

3. Rank candidates by quality before considering download convenience.
   - Prioritize direct relevance to the user's technical question, authoritative venues, known foundational papers/reviews/standards, citation influence, methodological fit, and recency when the field is changing.
   - Prefer version-of-record publisher PDFs for selected targets when the user has access.
   - Treat OA availability as a metadata/download convenience signal only. Do not substitute a lower-quality OA paper for a better paywalled/authenticated paper without the user's approval.

4. Choose the best authorized access route for the selected targets.
   - First: publisher page through the user's authenticated session or institutional proxy.
   - Second: library discovery/link resolver, document delivery, or interlibrary loan.
   - Third: publisher-hosted OA PDF or repository OA PDF from Unpaywall/OpenAlex/arXiv/PMC, when it is the same target work or when the user approves an alternative.
   - For Chinese literature, prefer CNKI, Wanfang, VIP, official journal sites, DOI/Crossref when present, or institution library discovery.
   - When authentication, captcha, QR login, SSO, or license confirmation blocks progress, pause and ask the user to complete it. Continue only after the page is authorized.
   - When the authenticated page still shows purchase-only, rent-only, or no-entitlement access, stop trying to download that target and record it in the not-downloaded list.

5. Download or collect the artifact.
   - Use official "PDF", "Download PDF", "Full Text PDF", or equivalent buttons on authorized pages.
   - Preferred non-UI method for local browser sessions:
     1. Open official DOI/article/PDF URLs in the user's already-authorized local browser with OS/browser launch commands.
     2. Check the user's download folder for new PDFs.
     3. If the browser displays the PDF without saving, run `scripts/extract_browser_pdf_cache.py` to recover the already-loaded PDF response from local Chrome/Edge cache.
     4. Verify extracted PDFs by file header, page count, and title text before treating them as downloaded.
   - Save files with stable names such as `firstauthor-year-short-title.pdf` or DOI-derived names.
   - Do not silently download many files from a platform. Keep the user informed when login, captcha, license limits, or manual download steps are encountered.

6. Verify and organize.
   - Open or inspect each PDF enough to confirm it matches the requested title/DOI.
   - Keep a `source_log.csv` or equivalent with: request item, title, DOI, source URL, PDF URL if available, access route, date, status, and notes. Use statuses such as `downloaded`, `authorization-needed`, `paywalled-after-authorization`, `no-entitlement`, and `metadata-only`.
   - For `paywalled-after-authorization`, `no-entitlement`, or `metadata-only`, include enough bibliographic detail for the user to request the item manually.
   - Export BibTeX/RIS/CSV/Markdown when requested.

## Helper Script

Run the resolver from the skill folder or by absolute path:

```bash
python C:/Users/Administrator/.codex/skills/literature-retrieval/scripts/resolve_literature.py --input papers.txt --out literature/results.csv --email user@example.com
python C:/Users/Administrator/.codex/skills/literature-retrieval/scripts/resolve_literature.py --doi 10.1109/5.771073 --query "sinuous antenna balun" --out results.json
```

- `--email` enables Unpaywall lookup and should be the user's public contact email, not a password. Use OA results for metadata and exact-target access hints, not as the default ranking criterion.
- Use `--out .csv`, `.json`, or `.md` depending on the requested deliverable.
- Read the script only when modifying it or diagnosing a failure.

Recover already-loaded local-browser PDFs without Computer Use:

```bash
python C:/Users/Administrator/.codex/skills/literature-retrieval/scripts/extract_browser_pdf_cache.py --out literature/cache-extracted --since-minutes 120 --manifest literature/cache-extracted/manifest.csv
python C:/Users/Administrator/.codex/skills/literature-retrieval/scripts/extract_browser_pdf_cache.py --out literature/cache-extracted --title "High-Power Microwaves" --dedupe
```

- Use this only after official pages/PDFs have been opened in the user's authorized local browser.
- The script reads local cache files only, extracts byte ranges beginning with `%PDF-`, trims to `%%EOF` when present, deduplicates by SHA-256, and optionally filters by extracted PDF text.
- Validate and rename outputs before final delivery.

## Platform Details

Read `references/platform-workflows.md` when working with named platforms such as IEEE Xplore, CNKI, ScienceDirect, SpringerLink, Wiley, ACM, arXiv, PubMed/PMC, or institutional proxy workflows.
