"""Phase 2 grain-collapse for the NY Open NY (Socrata) lobbying pipeline.

NY's datasets are denormalized ~1,300x: one filing emits hundreds-to-thousands
of rows (the cartesian of bills x subjects x parties-lobbied x ...), with the
filing-level compensation replicated on every row. Separately, an amendment is
a NEW submission (a new ``form_submission_id``) that supersedes the prior
submission for the same business key; re-amendment is common.

:func:`collapse_to_filing_grain` is the load-bearing dollar-conservation guard.
It runs two steps, in order:

1. **Supersede resolution.** Group by the business key and keep only the rows
   whose ``form_submission_id`` is the maximum for that key. Verified against
   live data: amendment ids are strictly greater than the superseded original's
   id, so ``max(form_submission_id)`` is the latest version. This drops
   superseded submissions entirely, so their (often different) compensation can
   never be summed in.

2. **Grain collapse.** Reduce the surviving row explosion to one row per
   ``(reporting_year, reporting_period, form_submission_id, principal_lobbyist,
   beneficial_client, bill_id)``. Compensation is filing-level and replicated,
   so it is carried (not summed) onto each surviving bill row; summing it over
   *distinct* filings then equals the true total.

The function operates on **canonical** column names (see :data:`BUSINESS_KEY`
and :data:`GRAIN`); per-dataset raw column names are normalized upstream by the
column map before this step.
"""

from __future__ import annotations

import pandas as pd

#: Identity of a single filing across submissions. An amendment shares this key
#: with the submission it supersedes but carries a higher ``form_submission_id``.
BUSINESS_KEY: tuple[str, ...] = (
    "reporting_year",
    "reporting_period",
    "principal_lobbyist",
    "beneficial_client",
    "contractual_client_name",
)

#: One output row per this tuple. ``bill_id`` is null for non-bill focus rows.
GRAIN: tuple[str, ...] = (
    "reporting_year",
    "reporting_period",
    "form_submission_id",
    "principal_lobbyist",
    "beneficial_client",
    "bill_id",
)

#: Identity of a single firm's filing (one firm's report-of-work for one client
#: in one period) — ``GRAIN`` minus ``bill_id``. This is NOT ``form_submission_id``
#: alone: a ``form_submission_id`` is the *client's* semi-annual report id, shared
#: across every firm the client retains (verified on live 2025 data — 26% of
#: submissions list >1 firm). Per-filing aggregates (e.g. ``n_bills_in_filing``)
#: must group by this key, or a co-retained firm's bills leak into another's.
FILING_KEY: tuple[str, ...] = GRAIN[:-1]

_CARRIED = ("contractual_client_name", "filing_compensation")
_REQUIRED = set(BUSINESS_KEY) | set(GRAIN) | {"filing_compensation"}


def resolve_superseded(
    df: pd.DataFrame,
    *,
    business_key: tuple[str, ...] = BUSINESS_KEY,
) -> pd.DataFrame:
    """Keep only the latest submission per business key (drop superseded ones).

    An amendment is a NEW ``form_submission_id`` superseding the prior submission
    for the same business key; verified against live data, amendment ids are
    strictly greater than the superseded original's, so ``max(form_submission_id)``
    per business key is the surviving version. ``dropna=False`` is load-bearing: a
    NaN in any business-key column would otherwise make ``groupby`` drop the group,
    ``transform("max")`` return NaN, and every row for that filing fall out of the
    ``== latest`` filter — silently losing the filing.

    Shared by :func:`collapse_to_filing_grain` (the dollar pipeline) and the
    ``parties_lobbied`` extraction, so both drop superseded submissions identically.
    """
    work = df.copy()
    work["__seq"] = pd.to_numeric(work["form_submission_id"], errors="raise")
    latest_seq = work.groupby(list(business_key), dropna=False)["__seq"].transform("max")
    return work.loc[work["__seq"] == latest_seq].drop(columns="__seq")


def collapse_to_filing_grain(
    df: pd.DataFrame,
    *,
    business_key: tuple[str, ...] = BUSINESS_KEY,
) -> pd.DataFrame:
    """Resolve superseded submissions and collapse the row explosion to grain.

    Returns one row per :data:`GRAIN` tuple, carrying ``contractual_client_name``,
    the filing-level ``filing_compensation`` (replicated, not summed), and
    ``n_bills_in_filing`` (the count of distinct real bills in the filing — the
    denominator a downstream even-split needs). Rows are deterministically
    sorted so re-runs diff cleanly.

    Expects the canonical ``bill_id`` column to already exist — it is derived by
    the **parser step**, which runs downstream of :func:`columns.normalize_columns`
    (rename) and upstream of this collapse. ``normalize_columns`` output alone is
    not directly consumable here; the parser must interpose to add ``bill_id``.

    Assumptions (true for the verified data shape): ``form_submission_id`` is the
    submission primary key (so the max id per business key is a single
    submission), and ``filing_compensation`` is replicated identically across a
    filing's rows (so de-duplicating to grain keeps the correct value).

    Raises :class:`KeyError` if a required canonical column is absent.
    """
    missing = _REQUIRED.difference(df.columns)
    if missing:
        raise KeyError(f"grain-collapse requires canonical columns; missing: {sorted(missing)}")

    # 1. Supersede resolution: keep only the latest submission per business key.
    survivors = resolve_superseded(df, business_key=business_key)

    # 2. Collapse the explosion to one row per (filing, bill).
    collapsed = survivors.drop_duplicates(subset=list(GRAIN))

    # Distinct real bills per surviving filing (null bill_id excluded). Keyed by
    # FILING_KEY, not form_submission_id alone — a shared client submission lists
    # multiple firms, each with its own bills; grouping by submission would give
    # every co-retained firm the union of all their bill counts.
    real_bills = survivors.loc[survivors["bill_id"].notna()]
    n_bills = real_bills.groupby(list(FILING_KEY))["bill_id"].nunique()

    out_cols = list(GRAIN) + [c for c in _CARRIED if c not in GRAIN]
    out = collapsed.loc[:, out_cols].copy()
    filing_keys = list(zip(*(out[col] for col in FILING_KEY)))
    out["n_bills_in_filing"] = [int(n_bills.get(key, 0)) for key in filing_keys]

    out = out.sort_values(by=list(GRAIN), na_position="last").reset_index(drop=True)
    return out
