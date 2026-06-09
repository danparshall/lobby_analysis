"""Builds the LLM extraction brief for OH legislative-agent A&E reports.

The brief is the prompt content passed to the model (see MODEL_ID) alongside
the fetched OLAC AER text. Keep it narrow to OH legislative regime — other
regimes (executive-agency, retirement-system) and other states get their
own briefs when (B') broadens.
"""

OH_LEGISLATIVE_BRIEF = """\
You are extracting one Ohio legislative-agent Activity & Expenditure Report (AER)
into a LobbyingFiling JSON record.

Source: Ohio Lobbying Activity Center (OLAC), public AER view.
Regime: legislative (governed by ORC §§101.70-101.79).
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

5. Leave fields null when not stated in the source. Do NOT guess or hallucinate.

6. Populate filing-level fields from the report header. The agent name is the
   filer — set filer_person. Also set the reporting period dates, date filed,
   and confirmation number (use the confirmation number as the external
   filing_id). The "Employer" on the OH form is the principal the agent lobbies
   for — it is NOT the filer. Put it in the `employer` field, NOT in
   filer_organization (employer ≠ organizational-filer). In the OH legislative
   regime the filer is always a natural-person agent, so filer_organization
   stays null — the OH form has no organizational-filer field separate from
   the agent and the employer. (Schema-wide, filer_person and
   filer_organization are independent and other states' regimes may populate
   both; this brief is OH-legislative-only.)

7. The "Reporting Period" field uses OH's standard semesterly shorthand. The
   OH legislative AER has exactly three reporting periods per year (per ORC
   §101.72), and the form's UI compresses them:
     - "Jan-Apr<YY>"  means January 1, 20YY  through April 30, 20YY
     - "May-Aug<YY>"  means May 1, 20YY      through August 31, 20YY
     - "Sep-Dec<YY>"  means September 1, 20YY through December 31, 20YY
   Always emit reporting_period_start and reporting_period_end as 4-digit-year
   ISO dates (YYYY-MM-DD) by expanding the 2-digit year YY to 20YY. Example:
   source "May-Aug25" yields reporting_period_start=2025-05-01 and
   reporting_period_end=2025-08-31. Do NOT emit the literal source string as
   the year; "May-Aug25" is shorthand, not a date.

8. If the source contains information that does not fit any schema field, do NOT
   silently drop it and do NOT force it into an ill-fitting field. Add a short,
   specific note to extraction_warnings describing what you saw and why it did
   not fit (e.g., "Section II.D splits into Meals/Speaking/National Conference
   sub-amounts; schema has one entertainment row, sub-breakdown lost"). This is
   how you flag schema gaps for human review.
"""


def build_oh_legislative_brief() -> str:
    """Return the OH legislative-agent extraction brief.

    No parameters at (A') — the brief is fixed for this single regime and form
    type. Parameterization (e.g., regime, form_type, year) becomes a (B')
    concern when we generalize.
    """
    return OH_LEGISLATIVE_BRIEF
