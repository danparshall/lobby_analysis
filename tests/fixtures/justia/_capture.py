"""One-off fixture-capture helper. Fetches a handful of Justia pages via Playwright
and saves them as static HTML fixtures for the TDD cycle in tests/.

Usage:
    uv run python tests/fixtures/justia/_capture.py

Re-run only when we need to refresh fixtures (e.g. Justia changes markup).
"""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

FIXTURES_DIR = Path(__file__).parent

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def capture(url: str, out_name: str, page) -> None:
    out = FIXTURES_DIR / out_name
    if out.exists():
        print(f"skip (exists): {out.name}")
        return
    print(f"fetching {url} ...")
    resp = page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    status = resp.status if resp else 0
    # Wait for Cloudflare challenge (if any) to clear: poll title for up to 30s.
    for i in range(60):  # 60 * 500ms = 30s
        title = page.title()
        if "Just a moment" not in title and "Attention Required" not in title:
            break
        page.wait_for_timeout(500)
    else:
        print(f"  !! challenge did not clear for {url}")
    title = page.title()
    body = page.content()
    out.write_text(body, encoding="utf-8")
    blocked = "Just a moment" in body or "Attention Required" in body
    print(f"  -> {out.name} ({len(body):,} bytes, HTTP {status}, title={title!r}, blocked={blocked})")
    time.sleep(2.0)  # courtesy rate-limit


def main() -> None:
    urls = [
        # Year index for CA: list of all years Justia hosts for California.
        ("https://law.justia.com/codes/california/", "california_index.html"),
        # Year index for CO: Justia's earliest CO year is 2016, so no 2010.
        ("https://law.justia.com/codes/colorado/", "colorado_index.html"),
        # CA 2010 title index: list of all titles available for CA in 2010.
        ("https://law.justia.com/codes/california/2010/", "california_2010_index.html"),
        # One title leaf. Target: CA Government Code, which contains the Political
        # Reform Act (Ch. 6, §§ 86100+) — the lobbying-disclosure chapter.
        # Pick a top-level title index that lists chapters.
        (
            "https://law.justia.com/codes/california/2010/gov.html",
            "california_2010_gov_title.html",
        ),
        # One section-range leaf (Political Reform Act §§ 86100-86118 = definitions
        # in the lobbying-disclosure article). Justia's actual leaf format is range-pages,
        # not individual-section pages.
        (
            "https://law.justia.com/codes/california/2010/gov/86100-86118.html",
            "california_2010_gov_sections_86100_86118.html",
        ),
        # --- TX bootstrap: year-index + 2009 title-index, to learn slug structure
        # before fetching the Government Code Ch. 305 pages.
        # TX has biennial Justia coverage (2005, 2009, 2011, 2013, ...); 2010 is not
        # hosted. Phase 1 audit correctly picked 2009 as the nearest within ±2 tolerance.
        # Note: TX uses directory-style title URLs (`/codes/texas/2009/government-code/`)
        # rather than CA's `.html`-suffixed form — parser must handle both.
        ("https://law.justia.com/codes/texas/", "texas_index.html"),
        ("https://law.justia.com/codes/texas/2009/", "texas_2009_index.html"),
        # TX Government Code title page. Chapter 305 = Registration of Lobbyists
        # (TX's counterpart to CA Political Reform Act Ch. 6).
        (
            "https://law.justia.com/codes/texas/2009/government-code/",
            "texas_2009_government_code_title.html",
        ),
        # TX Gov Code Title 5 (Open Government; Ethics) — kept for reference; it holds
        # the Texas Ethics Commission (Ch. 571) + related ethics/disclosure chapters,
        # but NOT Ch. 305 (Lobbyists). Ch. 305 lives under Title 3.
        (
            "https://law.justia.com/codes/texas/2009/government-code/title-5-open-government-ethics/",
            "texas_2009_gov_title5.html",
        ),
        # TX Gov Code Title 3 (Legislative Branch) — houses Ch. 305 (Registration of
        # Lobbyists). Subtitle A covers the legislature; Ch. 305 is the lobby-disclosure
        # statute equivalent to CA Political Reform Act.
        (
            "https://law.justia.com/codes/texas/2009/government-code/title-3-legislative-branch/",
            "texas_2009_gov_title3.html",
        ),
        # TX Gov Code Ch. 305 (Registration of Lobbyists) — the core lobby-disclosure
        # statute leaf. May list sections (deeper navigation) or contain statute text.
        (
            "https://law.justia.com/codes/texas/2009/government-code/title-3-legislative-branch/chapter-305-registration-of-lobbyists/",
            "texas_2009_gov_title3_chapter305.html",
        ),
        # --- WY / NY / WI year-index pages for curation of the lobbying_statute_urls
        # config. Fixtures kept for reference; parser tests don't strictly require
        # them but they document the URL hierarchy we navigated.
        ("https://law.justia.com/codes/wyoming/2010/", "wyoming_2010_index.html"),
        ("https://law.justia.com/codes/new-york/2010/", "new_york_2010_index.html"),
        ("https://law.justia.com/codes/wisconsin/2010/", "wisconsin_2010_index.html"),
        # NY "Regulation of Lobbying Act 1040/81" — standalone code slug (not under
        # Legislative Law). Likely the single-URL statute body for NY lobby law.
        (
            "https://law.justia.com/codes/new-york/2010/rla/",
            "new_york_2010_rla.html",
        ),
        # WI Ch. 13 (Legislative Branch) — contains Subch. III Lobbying Regulation
        # (§§13.61-13.795). Fetching the chapter page to see sub-structure.
        (
            "https://law.justia.com/codes/wisconsin/2010/13/13.html",
            "wisconsin_2010_chapter13.html",
        ),
        # WY Title 28 (Legislature) — contains Ch. 7 Lobbying (§§28-7-101 et seq.).
        (
            "https://law.justia.com/codes/wyoming/2010/Title28/Title28.html",
            "wyoming_2010_title28.html",
        ),
        # WY Title 28 Ch. 7 (Lobbyists) — statute leaf.
        (
            "https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html",
            "wyoming_2010_title28_chapter7.html",
        ),
    ]

    with sync_playwright() as p:
        for url, name in urls:
            # Fresh browser per request: Cloudflare fingerprints the session after the
            # first request, so a long-lived context gets progressively challenged.
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(user_agent=UA)
            page = ctx.new_page()
            try:
                capture(url, name, page)
            except Exception as e:
                print(f"  !! failed {url}: {e}")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
