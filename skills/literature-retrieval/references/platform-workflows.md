# Platform Workflows

Use this reference for named publisher, database, and library workflows. Keep access lawful and visible to the user. Select papers by quality first; use access workflows to retrieve the selected targets.

## General Browser Workflow

1. Start from a DOI, publisher URL, library link resolver, or official database result.
2. If the page requires authentication, ask the user to sign in manually. Continue only after the authenticated page is visible.
3. Avoid Computer Use/UI clicking unless the user explicitly asks for it or no non-UI route exists. Prefer opening official URLs in the local authorized browser, then checking downloads/cache.
4. Use official download controls or official PDF URLs only. Do not extract cookies, tokens, hidden API URLs, or signed PDF links for reuse.
5. If the browser renders a full PDF but does not save it, recover the already-loaded local cache response with `scripts/extract_browser_pdf_cache.py`, then validate title/page count.
6. Save the PDF and log the landing URL, source platform, access route, date, and status.
7. Verify the title, DOI, authors, and publication year against the request.
8. Do not replace a selected high-quality target with an easier OA/preprint result unless it is the same work or the user approves the substitution.
9. If the authorized page still requires purchase or shows no entitlement, record DOI, citation, official URL, access status, and next step; do not keep attempting unauthorized download paths.

## IEEE Xplore

- Prefer DOI URLs or `https://ieeexplore.ieee.org/document/<article-number>` pages.
- Use the official `PDF` button after the user is authenticated or the paper is open access.
- For authorized local Chrome/Edge sessions, opening `https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=<article-number>` may load the IEEE Full-Text PDF in the browser. If it renders but does not save, use cache extraction and validate the PDF.
- If access is denied, ask the user to complete IEEE/institution authorization in the browser first. After authorization is unavailable or denied, check the user's library resolver, document delivery, author accepted manuscript, arXiv, or conference/journal homepage.
- Record IEEE article number when available.

## CNKI, Wanfang, VIP, and Chinese Journal Sites

- Prefer exact title, author, year, journal, and fund/project identifiers because Chinese databases often have duplicate or near-duplicate records.
- Use the user's manual login or institutional IP/proxy access. Pause for the user when captcha, SMS, QR-code login, SSO, or download confirmation appears. Do not automate captcha, SMS, QR-code login, or account sharing.
- Save both PDF/CAJ when the user explicitly wants both and the platform license allows it. Otherwise prefer PDF.
- For CNKI records, log title, authors, source journal/conference, year, issue, DOI if present, database URL, and download status.

## ScienceDirect, SpringerLink, Wiley, Taylor & Francis, ACM, APS, OSA/Optica

- Start from DOI landing pages or the platform's official article page.
- Use institutional access banners or authenticated PDF buttons for selected targets. Use open access labels when they point to the same selected work, not as a reason to choose a lower-quality substitute.
- If only HTML is available through access, ask whether HTML capture, citation export, or library request is acceptable.
- For accepted manuscripts, prefer institutional repositories and author pages surfaced by OpenAlex/Unpaywall.

## arXiv, PubMed, and PubMed Central

- arXiv PDFs are authorized when available. Record arXiv ID and version.
- PubMed is metadata-focused; PubMed Central provides authorized full text when a PMCID exists.
- Distinguish preprints from version-of-record articles in the source log.

## Google Scholar and Search Engines

- Use search engines for discovery only when DOI/title databases fail or the user asks for broad discovery.
- Do not scrape search results at scale. Prefer official APIs and publisher/repository pages once candidates are found.

## When Full Text Is Unavailable

Report the status only after the user has had a chance to complete authorization. Include a table with DOI, title, authors, venue, year, official URL, access status, and best next step. Provide the best authorized next step:

- DOI/publisher landing page
- Library link resolver or interlibrary loan request
- Author contact or institutional repository search
- Open-access/preprint alternatives checked when authorized access is unavailable or the user wants substitutes
- Citation-only export
