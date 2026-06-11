"""Tests for the OH-portal fetch layer's network identity.

The HTTP boundary itself is validated live, not unit-tested (see fetch.py's
module docstring). The User-Agent, however, is a pure constant carrying a
policy contract: when we crawl a state ethics server we identify ourselves
honestly rather than impersonating a browser. That contract is worth guarding.
"""

from lobby_analysis.oh_portal.fetch import USER_AGENT


def test_user_agent_identifies_honestly() -> None:
    # Must not masquerade as a mainstream browser.
    assert "Mozilla/" not in USER_AGENT
    assert "Chrome/" not in USER_AGENT
    assert "Safari/" not in USER_AGENT
    # Must carry a reachable contact handle (URL or email) so a server admin
    # can identify and reach the crawler's operator.
    assert ("+http" in USER_AGENT) or ("@" in USER_AGENT)
