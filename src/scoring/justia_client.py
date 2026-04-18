"""Justia HTTP client + HTML parsers.

Pure HTML parsing functions operate on strings — testable without the network.
Live-fetch path uses Playwright (fresh browser context per request) to clear
Cloudflare's JS challenge. Both paths satisfy a common `Client` protocol so
tests can substitute a FakeClient.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urljoin

from bs4 import BeautifulSoup

JUSTIA_BASE = "https://law.justia.com"


@dataclass(frozen=True)
class YearEntry:
    year: int
    url: str


@dataclass(frozen=True)
class TitleEntry:
    name: str
    slug: str
    url: str


class Client(Protocol):
    """Fetches an HTML page. Implementations: PlaywrightClient, FakeClient (tests)."""

    def fetch_page(self, url: str) -> str: ...


# ---------- parsers ----------


_YEAR_HREF_RE = re.compile(r"/codes/[a-z-]+/(\d{4})/?$")
_TITLE_HREF_RE = re.compile(r"/codes/[a-z-]+/\d{4}/([a-z0-9_-]+)\.html$")


def parse_state_year_index(html: str) -> list[int]:
    """Return the list of years Justia hosts for a state.

    Input: HTML of `https://law.justia.com/codes/<state>/`.
    Extracts years from `<a>` hrefs matching `/codes/<state>/<YYYY>/`.
    """
    soup = BeautifulSoup(html, "html.parser")
    years: set[int] = set()
    for a in soup.find_all("a", href=True):
        m = _YEAR_HREF_RE.search(a["href"])
        if not m:
            continue
        years.add(int(m.group(1)))
    return sorted(years)


def parse_year_title_index(html: str) -> list[TitleEntry]:
    """Return the list of code titles for a state in a given year.

    Input: HTML of `https://law.justia.com/codes/<state>/<year>/`.
    Extracts `<a href=".../state/year/slug.html"> Title Name </a>` entries.
    """
    soup = BeautifulSoup(html, "html.parser")
    seen_urls: set[str] = set()
    titles: list[TitleEntry] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = _TITLE_HREF_RE.search(href)
        if not m:
            continue
        url = href if href.startswith("http") else urljoin(JUSTIA_BASE, href)
        if url in seen_urls:
            continue
        name = a.get_text(strip=True)
        if not name:
            continue
        seen_urls.add(url)
        titles.append(TitleEntry(name=name, slug=m.group(1), url=url))
    return titles


# ---------- live client ----------

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class PlaywrightClient:
    """Live Justia client. Uses a fresh browser context per request to avoid
    Cloudflare's within-session fingerprinting (which re-challenges a persistent
    session after the first request and never clears).
    """

    def __init__(
        self,
        *,
        rate_limit_seconds: float = 5.0,
        challenge_timeout_seconds: float = 30.0,
    ) -> None:
        self._rate_limit_seconds = rate_limit_seconds
        self._challenge_timeout_seconds = challenge_timeout_seconds

    def fetch_page(self, url: str) -> str:
        import time

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(user_agent=_BROWSER_UA)
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                # Wait for Cloudflare JS challenge to clear, if present.
                deadline_polls = int(self._challenge_timeout_seconds * 2)
                for _ in range(deadline_polls):
                    title = page.title()
                    if "Just a moment" not in title and "Attention Required" not in title:
                        break
                    page.wait_for_timeout(500)
                body = page.content()
            finally:
                browser.close()
        time.sleep(self._rate_limit_seconds)
        return body
