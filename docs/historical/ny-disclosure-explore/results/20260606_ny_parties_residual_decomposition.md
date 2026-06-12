<!-- Generated during: convos/20260606_ny_accent_fold_match_key.md -->

# NY `parties_lobbied` — what's in the residual after accent-folding

After accent-folding, **7,393 edge rows** (206 distinct raw values) carry a
legislator title (`Senator` / `Assembly member`) but stay **unresolved**. This
doc decomposes them to decide which lever is worth building next. Generated from
the regenerated 2025 release + the OS files in `data/bills/NY/2025/`.

## The "fuller OS people roster" lever is dead (0 recovery)

The handoff proposed a fuller OS people roster (beyond bill sponsorships) to catch
"leadership / non-sponsors." The data refutes it:

- The **sponsorship** roster already holds **219 distinct persons** — NY has 213
  seats, so it is already the whole legislature.
- `NY_2025-2026_vote_people.csv` (everyone who cast a vote) adds 152 more first+last
  keys but recovers **0** of the residual. (Id-consistency is fine: 66 keys appear
  in both sources, with **0** `ocd-person` disagreements — safe to merge if ever
  needed.)
- **Every residual surname is already in the roster.** The misses are name-FORM
  mismatches, not absences.

## The residual is 91% nicknames

| bucket | distinct | rows | meaning |
|---|---:|---:|---:|
| **nickname-like** (surname in roster, first name differs) | 58 | **6,705 (91%)** | formal↔informal first name |
| **absent** (surname not in roster) | 148 | 688 (9%) | mostly *former* members |

Recovering the nickname bucket would lift **state-legislator resolution from
92.6% to ~99.3%**.

### Nickname-like — note the bidirectional direction

The disclosure is sometimes formal vs an informal roster, sometimes the reverse:

| disclosure (unresolved) | rows | roster first-name for that surname |
|---|---:|---|
| Senator Elizabeth Krueger (+staff) | 1,318 | `liz` |
| Assembly member Jennifer Lunsford (+staff) | 855 | `jen` |
| Assembly member Ronald T. Kim (+staff) | 585 | `ron` |
| Assembly member Edward Gibbs (+staff) | 549 | `eddie` |
| Assembly member Phillip G. Steck (+staff) | 590 | `phil` |
| Assembly member **Chris** Eachus (+staff) | 446 | `christopher` ← reverse: disclosure informal |
| Senator Daniel G. Stec (+staff) | 233 | `dan` |
| Senator Bill Weber | 127 | `william` |
| Senator Jim Tedisco (+staff) | 206 | `james` |
| … Matt/Matthew Slater, Steve/Steven Rhoads, Rob/Robert Rolison, Mike/Michael Reilly, Joe/Joseph Sempolinski, Sam/Samuel Pirozzolo … | | |

All are standard, dictionary-covered nickname pairs.

### Three false-match traps in the same bucket (the reason to use a curated dictionary, not surname-matching)

- **`Keith Wright` (disclosure) vs roster `Jordan Wright`** — *different people,
  same surname & district*: Keith L.T. Wright is the former member; Jordan Wright
  (his son) holds the seat now. Surname-only matching would mis-attribute Keith's
  lobbying to Jordan. A nickname dictionary refuses (keith ≠ jordan).
- **`Paul Bologna` vs roster `Paula Bologna`** — Paul/Paula are not a nickname
  pair; a curated dictionary keeps them distinct, a prefix/stemming heuristic
  would not.
- **`Jarett Gandolfo` vs roster `Jerett`** — a one-character *spelling* variant, not
  a nickname. A dictionary won't catch it; it needs bounded edit-distance (gated).

### Absent — mostly correctly unresolved former members

The 148-value / 688-row tail is long and heterogeneous: Carmen De La Rosa (→ NYC
Council 2021), Tim Kennedy (→ US House 2024), Helene Weinstein (d. 2024), Kimberly
Jean-Pierre (resigned 2022), plus a few misspellings (`Patrick J. Carrol`). These
are **not** current state legislators, so leaving them unresolved is correct —
mapping them to a current `ocd-person` would be wrong. Not worth a systematic
lever.

## Conclusion

Build a **nickname matcher** (canonicalize first names via a standard nickname↔formal
dictionary, both sides, then match on (canonical-first, last) with a collision
guard). Drop the fuller-roster item. Hold any edit-distance second pass for the
`Jarett/Jerett`-style tail behind a measurement gate — only ~a few hundred rows
are even candidates, so confirm it's worth it before building.

## Reproduction

Scripts (scratch, in `/tmp` during the session): `ny_residual_decompose.py`
(fuller-roster test), `ny_residual_lastname.py` (nickname-vs-absent split). Both
read `releases/ny/NY_filing_parties_lobbied.tsv` + `data/bills/NY/2025/`.
