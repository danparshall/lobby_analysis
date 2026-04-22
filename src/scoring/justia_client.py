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

# Justia chrome that appears as whole lines inside #main-content and gets
# deleted. Tight literal matches — we want to strip navigation without touching
# statute text that might share a word.
_CHROME_LINE_FRAGMENTS: tuple[str, ...] = (
    "Justia",
    "U.S. Law",
    "U.S. Codes and Statutes",
    "There Is a Newer Version",
    "View All Versions",
    "View Our Newest Version Here",
    "Justia Free Databases",
    "Justia Legal Resources",
    "Find a Lawyer",
    "Ask a Lawyer",
    "Legal Forms",
    "Free Newsletters",
    "Have a Legal Question",
    "Log In",
    "Sign Up",
    "Get your case reviewed",
    "Disclaimer:",
    "Justia makes no guarantees",
    "Copyright \u00a9",
    "Marketing Solutions",
)


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

    Note: This parser is CA-specific (it only matches `.html`-suffixed title
    URLs). Other states use directory-style URLs or deeper hierarchies. Kept
    for Phase 1 audit compatibility; new code should use
    `lobbying_statute_urls.LOBBYING_STATUTE_URLS` instead.
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


_NAMESPACE_RE = re.compile(r"^(?:https?://law\.justia\.com)?(/codes/[a-z-]+/\d{4}/)")


def parse_statute_text(html: str) -> str:
    """Extract statute text from a Justia statute-leaf page.

    Works on any Justia leaf regardless of state URL convention — CA
    section-range leaves, TX full-chapter leaves, NY single-page acts, WY
    chapter-leaves. Returns the main-content text with navigation chrome
    (breadcrumbs, version banner, "Find a Lawyer" CTAs, footer) removed.
    """
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one("#main-content")
    if main is None:
        # Fallback: some legacy Justia layouts don't use #main-content. Use
        # <article> or <main>, then the whole body as last resort.
        main = soup.find("article") or soup.find("main") or soup.find("body")
    if main is None:
        return ""
    raw_text = main.get_text("\n", strip=True)
    # Line-level filter: drop any line that starts with a known chrome fragment
    # or is purely navigation text (short, no statute-like content). Statute
    # lines tend to be long and sentence-like; chrome lines are short labels.
    kept: list[str] = []
    for line in raw_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if any(s.startswith(frag) or s == frag for frag in _CHROME_LINE_FRAGMENTS):
            continue
        kept.append(s)
    return "\n".join(kept)


def parse_children_list(html: str, parent_url: str) -> list[str]:
    """Return child-page URLs linked from a Justia listing page.

    Used during curation (when identifying the lobby-statute leaves for a new
    state or vintage). Not used by scheduled retrieval — that pulls from
    `lobbying_statute_urls.LOBBYING_STATUTE_URLS`.

    Returns absolute URLs in the parent's (state, year) namespace, excluding
    the parent itself and accounts.justia.com sign-in links. Deduplicated,
    preserving first-seen order.

    Raises ValueError if parent_url is not in the `/codes/STATE/YEAR/`
    namespace.
    """
    m = _NAMESPACE_RE.match(parent_url)
    if not m:
        raise ValueError(
            f"parent_url not in /codes/STATE/YEAR/ namespace: {parent_url}"
        )
    parent_path = (
        parent_url[len(JUSTIA_BASE):]
        if parent_url.startswith(JUSTIA_BASE)
        else parent_url
    )
    # Stem = parent path with trailing `/` and `.html` stripped. Children extend
    # the stem either by adding `/…` (subdirectory) or `.…` (same-dir filename
    # variant, as in WI's `/13/13.html` → `/13/13.61.html`).
    parent_canon = parent_path.rstrip("/")
    stem = parent_canon.removesuffix(".html")

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    children: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            url = JUSTIA_BASE + href
            path = href
        elif href.startswith(JUSTIA_BASE):
            url = href
            path = href[len(JUSTIA_BASE):]
        else:
            continue
        if "accounts.justia.com" in url:
            continue
        if path.rstrip("/") == parent_canon:
            continue
        if not path.startswith(stem):
            continue
        tail = path[len(stem):]
        # Strictly-deeper check: next character after stem must be a separator
        # (`/` subdirectory, `.` same-dir filename extension). Prevents false
        # matches like stem `/gov` matching an unrelated `/government-office.html`.
        if not tail or tail[0] not in ("/", "."):
            continue
        if url in seen:
            continue
        seen.add(url)
        children.append(url)
    return children


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
