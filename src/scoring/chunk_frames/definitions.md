## Chunk frame: `definitions`

You are identifying **what makes someone count as a lobbyist** under this state's law. The 7 compendium rows in this chunk decompose that question along three orthogonal axes. Read each row's `description` to identify which axis it asks about — the row name alone is sometimes ambiguous on direction.

### Axis 1 — Activity / TARGET axis

What kinds of *communication or activity* trigger inclusion in the lobbyist definition? Specifically: does lobbying *directed at* administrative or executive-branch agencies count, or is the regime legislative-only?

- `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` — target-axis. About lobbying *with administrative agencies as the recipients of contact*. NOT about agencies *as actors* (which lives in the registration domain).

### Axis 2 — Person / ACTOR axis

Does the definition include or exclude particular *categories of people* based on their role, independent of who they're contacting?

- `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` — actor-axis. About elected officials engaging in lobbying behavior themselves.
- `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` — actor-axis. About individual public employees (state-agency staff, civil servants) engaging in lobbying behavior themselves.

The actor-axis question about *agencies as institutional actors* (e.g., FDA staff lobbying Congress on behalf of FDA) is **not in this chunk** — it lives in the `registration` chunk's PRI A-series (`REG_GOVT_LOBBYING_GOVT`, `REG_EXECUTIVE_AGENCY`, etc.). This chunk's actor axis is limited to *individual* roles.

### Axis 3 — THRESHOLD axis

Does inclusion depend on a measurable gate the activity must clear?

- **Quantitative** thresholds (numeric):
  - `DEF_COMPENSATION_STANDARD` — paid > $X per period.
  - `DEF_EXPENDITURE_STANDARD` — spends > $X on lobbying.
  - `DEF_TIME_STANDARD` — > X% of compensated time on lobbying.
- **Qualitative** threshold (non-numeric materiality test):
  - `THRESHOLD_LOBBYING_MATERIALITY_GATE` — "main purposes" / "primary purpose" / "on a regular and substantial basis" / similar language.

Inclusion-framed ("a person IS a lobbyist if X") and exemption-framed ("a person is NOT subject to disclosure if X") phrasings can both populate these rows; the row description names which framing applies. Some rows have an exemption-framed counterpart in the `definitions` domain itself (e.g., `DEF_EXPENDITURE_STANDARD` ↔ `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT`); a statute can populate one, the other, or both — they are independent statutory mechanisms.

### Disambiguation cue

When you read each row, the **prepositions and verbs** in the description pin the axis:

- "**contact with** X" / "**directed at** X" / "lobbying *of* X" → TARGET axis.
- "X **engages in**" / "**treats** X **as**" / "X **is defined as** a lobbyist" → ACTOR axis.
- "**threshold**" / "exceeds $X" / "more than X% of time" → THRESHOLD axis.

If a row's description seems to apply to multiple axes simultaneously, surface it in `notes` and pick the axis the cited framework_reference items most strongly anchor on. Do **not** silently average.

### Statute-level scope reminder

OH (and several other priority states) has multiple parallel lobbying regimes (legislative, executive, retirement-system, pay-to-play, etc.). Each axis above can take a different value per regime. Apply the regime-emission rule from the locked scorer prompt — emit one record per `(compendium_row_id, regime, registrant_role)` tuple where the answer differs across regimes; emit a single record with `regime=null, registrant_role=null` where the answer is uniform.
