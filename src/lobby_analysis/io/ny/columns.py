"""Per-dataset column map for the NY Open NY (Socrata) lobbying pipeline.

Phase 0 found the 6 NY datasets name the same concept differently:

  * bill-focus discriminator: ``type_of_lobbying_focus`` (client_semiannual,
    public_corp) vs ``lobbying_focus_type`` (lobbyist_bimonthly, registration);
  * client: ``beneficial_client`` (client_semiannual) vs
    ``beneficial_client_name`` (others); ``principal_lobbyist`` vs
    ``principal_lobbyist_name``;
  * compensation: ``current_period_compensation`` vs ``compensation``;
  * individual people: ``individual_lobbyist_name`` / ``individual_lobbyist_s``
    / ``individual_lobbyists``.

:func:`normalize_columns` renames a raw dataset frame to ONE canonical schema so
the grain-collapse and parser steps are dataset-agnostic.

Scope: this map currently covers the two datasets the 2025 build uses —
``client_semiannual`` (chain spine) and ``lobbyist_bimonthly`` (itemized
expenses + individual-person resolution). The remaining four
(``lobbyist_registration``, ``disbursement_public_monies``,
``public_corp_registration``, ``public_corp_bimonthly``) are a later add-on:
their raw columns are recorded in ``tests/fixtures/ny/sample_schema_4datasets.json``,
and the public-corporation universe has a structurally different shape (no
contractual/beneficial-client triad) that needs its own modeling decision
before it can be folded into this canonical schema.

Reconciliation: both ``client_semiannual`` and ``lobbyist_bimonthly`` carry
compensation for the same retained-lobbyist universe at different grains
(semi-annual vs bi-monthly), and the column map projects *both* into the
canonical ``filing_compensation``. **Never sum compensation across the two
datasets** — see ``releases/ny/README.md`` Caveat 11 for the discipline. The
materializer is single-dataset per CLI invocation, so the current build
cannot double-count by construction; the rule binds future builds that fold
in ``lobbyist_bimonthly`` (#37).

NOTE: deriving the canonical ``bill_id`` (from ``focus_type`` +
``focus_identifying_number``) is intentionally NOT done here — it belongs to the
parser step, where the "State Bill focus vs. level_of_government" scoping
question is resolved. The committed Phase-0 fixture shows a ``State Bill`` row
(``S550-A``) at ``level_of_government = 'Both (State and Municipal)'``, which the
Phase-0 findings' ``starts_with(level, 'State')`` filter would wrongly exclude —
flagged for resolution at the parser step.
"""

from __future__ import annotations

import pandas as pd

#: raw column name -> canonical column name, per dataset. Columns already in
#: canonical form (``form_submission_id``, ``filing_type``, ``reporting_year``,
#: ``reporting_period``, ``contractual_client_name``, ``focus_identifying_number``,
#: ``level_of_government``) are left untouched and so are omitted here.
COLUMN_MAPS: dict[str, dict[str, str]] = {
    "client_semiannual": {
        "current_period_compensation": "filing_compensation",
        "type_of_lobbying_focus": "focus_type",
    },
    "lobbyist_bimonthly": {
        "principal_lobbyist_name": "principal_lobbyist",
        "beneficial_client_name": "beneficial_client",
        "compensation": "filing_compensation",
        "lobbying_focus_type": "focus_type",
        "individual_lobbyist_name": "individual_lobbyists",
    },
}


def normalize_columns(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Return ``df`` with ``dataset``'s raw columns renamed to canonical names.

    Raises :class:`KeyError` if ``dataset`` has no column map — an unrecognized
    dataset must fail loudly rather than flow downstream with raw column names.
    """
    if dataset not in COLUMN_MAPS:
        raise KeyError(
            f"no column map for dataset {dataset!r}; known: {sorted(COLUMN_MAPS)}"
        )
    return df.rename(columns=COLUMN_MAPS[dataset])
