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
    out = FIXTURES_DIR / out_name
    out.write_text(body, encoding="utf-8")
    blocked = "Just a moment" in body or "Attention Required" in body
    print(f"  -> {out.name} ({len(body):,} bytes, HTTP {status}, title={title!r}, blocked={blocked})")
    time.sleep(5.0)  # courtesy rate-limit


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
        # One section leaf: a specific Political Reform Act section.
        (
            "https://law.justia.com/codes/california/2010/gov/title-9/chapter-6/article-1/section-86100/",
            "california_2010_gov_section_86100.html",
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
