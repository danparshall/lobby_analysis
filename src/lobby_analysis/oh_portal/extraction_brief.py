"""Builds the LLM extraction brief for OH legislative-agent A&E reports.

The brief is the prompt content passed to claude-opus-4-7 alongside the
fetched OLAC AER text. Keep it narrow to OH legislative regime — other
regimes (executive-agency, retirement-system) and other states get their
own briefs when (B') broadens.
"""

OH_LEGISLATIVE_BRIEF = """\
You are extracting one Ohio legislative-agent Activity & Expenditure Report (AER)
into a LobbyingFiling JSON record.

Source: Ohio Lobbying Activity Center (OLAC), public AER view.
Regime: legislative (governed by ORC §§101.70-101.79). Use regime="legislative".
Form type: Legislative Agent Activity & Expenditure Report — quarterly-tri-annual
filing covering one (agent, employer) engagement during one reporting window
(May 31 / Sep 30 / Jan 31 deadlines).

Target schema: LobbyingFiling (lobby_analysis.models.filings) with sub-entities
LobbyingPosition (one per disclosed bill/resolution) and LobbyingExpenditure
(one per expenditure line item).

Extraction rules:

1. Section I lists bills/resolutions with active advocacy this period. For each,
   emit one LobbyingPosition. The OH form does NOT collect a stance ("support"/
   "oppose"/etc.), so leave the position field null when not stated. Populate
   bill_reference with the bill identifier (e.g., "HB 96") and description with
   the bill title.

2. Section II.A-C are itemized expenditure tables (Gifts; Itemized Meals &
   Beverages; Dinner/Party/Function where all members invited). For each
   populated row, emit one LobbyingExpenditure with category set per the
   section (gift / entertainment / entertainment), amount as the dollar value,
   and recipient_name from the Recipient column.

3. Section II.D is a non-itemized aggregate of three sub-categories (Meals
   Under $50, Speaking Engagements, National Conference Meals). The current
   schema cannot represent the three-way breakdown. If Section D has a
   non-zero total, emit ONE LobbyingExpenditure with category="entertainment",
   amount=Total Aggregate D, recipient_name=null. Do NOT emit three rows.
   Do NOT invent recipients.

4. If a section is empty or shows "No expenditures", emit no expenditure rows
   for that section.

5. Leave fields null when not stated in the source. Do NOT guess. Hallucinated
   values pollute the validation log and break the (A') round-trip's signal.

6. Populate filing-level fields from the report header: agent name, employer
   name, reporting period dates, date filed, confirmation number (use as the
   external filing_id).
"""


def build_oh_legislative_brief() -> str:
    """Return the OH legislative-agent extraction brief.

    No parameters at (A') — the brief is fixed for this single regime and form
    type. Parameterization (e.g., regime, form_type, year) becomes a (B')
    concern when we generalize.
    """
    return OH_LEGISLATIVE_BRIEF
