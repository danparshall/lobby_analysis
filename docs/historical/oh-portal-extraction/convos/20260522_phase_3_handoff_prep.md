# OH (A') Phase 3 — VPN workaround + handoff

**Date:** 2026-05-22
**Branch:** oh-portal-extraction

## Summary

The long-running blocker on (A') execution has been **VPN reachability** to US state portals — `requests.get` against OLAC times out at the connect layer from outside the US. This session is the one where the workaround landed: browser-save the AER HTML with VPN on, mirror it into the canonical `data/oh_portal/raw/...` layout, and feed the local file to the extractor by importing the shipped modules directly (skipping the blocked fetch step). The HTML round-trip worked end-to-end.

Two other items closed out in the same session:
- **Validation results skeleton.** `results/20260507_oh_a_prime_validation.md` pre-filled with source-derived ground truth (4 bills, $20 Section II.D aggregate, expected null patterns, pre-flagged schema gaps). The actual validation step is now purely tag-filling.
- **Regime literal verification.** `git grep "regime=" origin/statute-extraction` confirmed `regime="legislative"` — matches `extraction_brief.py:14` exactly. No code change required.

The LLM extraction call itself surfaced a workspace API quota cap (resets 2026-06-01). Will be resolved on my side; assume it doesn't apply for whoever picks up the LLM run.

## Decisions made

- **Preserve canonical raw-artifact layout** for the browser-saved HTML — mirroring with a real `meta.json` (sha256 over the bytes, `fetch_method="browser-save-via-vpn-then-local-copy"`) means downstream tooling sees the same shape as a live fetch.
- **No unilateral schema bump for v1.4.** Pre-flagged gaps go in the validation doc + this convo; bump waits for team consensus.
- **Don't expand (A') scope to multiple filings.** One filing is correct for (A'); the volume work is (B'). HART 1459616 and LKQ 1405684 are already pre-vetted as (B') seeds.

## Open questions

- Still open from 2026-05-07: v1.4 schema-gap handling protocol (ad-hoc convo + Dan/Gowrav review, or formal RFC?). Concrete first-gap candidate now ready in the validation doc (Section II.D three-sub-row structure).
- Still open from 2026-05-07: Anthropic SDK vs subagent-dispatch alignment with Track A. Refactor cost ~1–2hr now, larger at (B') scale.

## What's left

1. Run the LLM extraction against the saved HTML (or live fetch from a US-network machine).
2. Fill in `results/20260507_oh_a_prime_validation.md` — Emitted Value + Tag columns; compute summary stats.
3. Append session entry to `RESEARCH_LOG.md`; one-liner to `STATUS.md` Recent Sessions; commit + push.

## Side notes

- Worktree venv editable install is duplicated 4×; tests and CLI work fine under `PYTHONPATH=src .venv/bin/python -m ...`. Long-term cleanup is a separate ticket — don't `uv sync --reinstall-package` per standing memory.
- The `regime` field on `FieldRequirement` (`state_master.py:151`) is `str | None`, not a constrained `Literal`. Convention is community-policed; worth flagging as low-priority schema hygiene.
