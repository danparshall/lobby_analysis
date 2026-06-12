<!-- Generated during: convos/20260610_ny_bi_semi_reconciliation.md -->

# Empirical reconciliation: `client_semiannual` vs `lobbyist_bimonthly` compensation

**Date:** 2026-06-10
**Branch:** `ny-disclosure-explore`
**Probe:** [`scripts/ny_probe_bi_semi_reconciliation.py`](../../../../scripts/ny_probe_bi_semi_reconciliation.py)
**Raw evidence:** [`20260610_ny_bi_full_pull.json`](20260610_ny_bi_full_pull.json) (35 distinct bimonthly filing tuples for 5 firms in 2025)
**Issue:** [#37](https://github.com/danparshall/lobby_analysis/issues/37)
**Local pulls used:** `data/raw/ny/2025/client_semiannual.csv` (full 11,200,080-row 2025 pull) + a targeted Socrata `$group` query against `t9kf-dqbc` for the 5 sample firms (no full bimonthly pull on disk).

## TL;DR

**The bimonthly and semiannual datasets report the exact same compensation dollars on two different cadences.** For every `(principal_lobbyist, beneficial_client, half-year)` cell tested:

> `SUM(canonical bimonthly compensation for periods in H)` **`= canonical semiannual compensation for H`** to the cent.

Empirically verified on **11/11 cells** (5 firms × up to 2 half-years × 1 client each, plus one second-client case for STOP). Zero delta in every cell. Including a load-bearing case where the semiannual amendment corrected $47,000 → $45,823 and the bimonthly side independently reports $45,823 — the two regulated filer-sides are reconciled by amendment.

**Operational consequence (binds future builds that materialize both datasets):** naively concatenating the materialized `filing_compensation` columns from both datasets would **exactly 2× double-count** the retained-lobbyist universe — not a precaution, a literal multiplicative error. Caveat 11 of `releases/ny/README.md` updated with the empirically-verified rule.

## Method

The 2026-06-07 bimonthly party-grain probe ([`results/20260607_ny_bimonthly_party_grain.md`](20260607_ny_bimonthly_party_grain.md)) captured one bimonthly period per firm — necessary but insufficient to test the SUM-across-3-bi-periods rule.

This probe extends the sample by hitting Socrata for all distinct `(form_submission_id, year, period, firm, b_client, c_client, compensation)` tuples for the 5 firms in 2025 (`$group` query, 35 rows in 25s), then comparing against the local 2025 semiannual CSV. Both sides apply the amendment-supersede rule (keep `max(form_submission_id)` per business key — same rule [`io/ny/grain.py`](../../../../src/lobby_analysis/io/ny/grain.py) uses on the semi side, applied here to the bi side too).

**Why the 5 firms?** They're the mid-size dense filings selected by the 2026-06-07 probe — small enough that one Socrata `$group` returns all their distinct tuples in one request, large enough to include both single-client filers (CSEA, Planned Parenthood, NYSEDC, Clean and Healthy NY) and a multi-client retained-lobbyist firm (STOP, which retains two clients: itself and the Future of Life Institute). Coverage spans 3 retainer shapes:

| Shape | Example | What it tests |
|---|---|---|
| Constant per-period retainer | NYSEDC ($9,015 × 6 periods = $27,045 × 2 semi) | Trivial linear case |
| Variable per-period billing | CSEA (Jan/Feb $3,569; Mar/Apr $16,527; May/June $5,448 → semi $25,544) | Non-uniform sum still reconciles |
| Amendment-corrected total | STOP/Future of Life H2: bi periods sum to $45,823; semi original $47,000 → amended $45,823 | Supersede picks the amendment on both sides; they agree |

## Reconciliation table

| Firm | Beneficial client | Half | `SUM(bi)` | `semi` | Δ | Bi periods present |
|---|---|---|---:|---:|---:|---|
| CSEA, INC. | CSEA, INC. | H1 | $25,544.00 | $25,544.00 | $0.00 | Jan/Feb · Mar/Apr · May/June |
| CSEA, INC. | CSEA, INC. | H2 | $10,707.00 | $10,707.00 | $0.00 | July/Aug · Sep/Oct · Nov/Dec |
| Clean and Healthy NY | Clean and Healthy NY | H1 | $4,954.00 | $4,954.00 | $0.00 | Jan/Feb · Mar/Apr · May/June |
| Clean and Healthy NY | Clean and Healthy NY | H2 | $1,636.00 | $1,636.00 | $0.00 | July/Aug · Sep/Oct · Nov/Dec |
| NYSEDC | NYSEDC | H1 | $27,045.00 | $27,045.00 | $0.00 | Jan/Feb · Mar/Apr · May/June |
| NYSEDC | NYSEDC | H2 | $27,045.00 | $27,045.00 | $0.00 | July/Aug · Sep/Oct · Nov/Dec |
| Planned Parenthood | Planned Parenthood | H1 | $11,580.00 | $11,580.00 | $0.00 | Jan/Feb · Mar/Apr · May/June |
| Planned Parenthood | Planned Parenthood | H2 | $2,535.00 | $2,535.00 | $0.00 | July/Aug · Sep/Oct · Nov/Dec |
| STOP, INC. | STOP, INC. | H1 | $15,681.00 | $15,681.00 | $0.00 | Mar/Apr · May/June (no Jan/Feb bi filing exists) |
| STOP, INC. | STOP, INC. | H2 | $8,624.00 | $8,624.00 | $0.00 | July/Aug · Sep/Oct · Nov/Dec |
| STOP, INC. | Future of Life Institute | H2 | $45,823.00 | $45,823.00 | $0.00 | Sep/Oct · Nov/Dec (no July/Aug bi filing exists) |

**11 cells matched, 0 mismatched.** STOP/STOP H1 and STOP/Future of Life H2 each have only 2 of 3 expected bimonthly periods present — and the semiannual exactly equals the sum of the periods that *do* exist, confirming the rule survives missing-period gaps (the semi reports the half-year total of what was actually billed, and so does the bimonthly).

## Load-bearing details

### Amendments must be superseded on BOTH sides

For STOP/Future of Life Jul/Dec, the semi side has TWO filings (`776168` = $47,000 original, `782245` = $45,823 amendment); the bi side has TWO filings for Sep/Oct (`766186` = $3,267 + a later amendment) and similar story for Nov/Dec. With the max-`form_submission_id` rule applied to **both** sides, semi = $45,823 and SUM(bi) = $45,823. Without supersede, semi = $47,000 ≠ SUM(raw bi) — so the rule depends on applying the amendment chain consistently.

### The CSEA Mar/Apr surprise vs. the "1/3 each period" reading

A naive "each bimonthly = 1/3 of the semi" reading would predict CSEA's Jan/Feb 2025 bi = $25,544 / 3 ≈ $8,515 — instead the actual Jan/Feb bi is **$3,569**, with Mar/Apr **$16,527** carrying the bulk. The semi still reconciles ($3,569 + $16,527 + $5,448 = $25,544), but the per-period values reflect **actual billing**, not even-thirds. The reconciliation rule is summation, not division.

### Business key on both sides — the cross-dataset join

The bimonthly and semiannual datasets are **filed by different parties**: the semi is filed by the **client**, the bi is filed by the **firm**. Their `form_submission_id` sequences are independent (semi sub_ids and bi sub_ids overlap in numeric range but mean different things — they're not joinable). The cross-dataset handle is the **business key**:

```
(reporting_year, principal_lobbyist, beneficial_client[, contractual_client_name])
```

within which a half-year `H` defines the comparison interval (semi period ∈ {`Jan/June`, `July/Dec`}; bi periods covering `H1` = {`Jan/Feb`, `Mar/Apr`, `May/June`}, `H2` = {`July/Aug`, `Sep/Oct`, `Nov/Dec`}).

`contractual_client_name` is the lever for the multi-client retained-firm case (STOP retains both itself and the Future of Life Institute; the bi filings carry distinct `beneficial_client_name` to separate them, and the semi side does too). Including it in the key prevents collapsing two distinct retainers to one summed cell.

## Operational rule (for the implementer of a future build that materializes both)

1. **`client_semiannual` is the canonical compensation source** for the 2025 release. The 2025 totals in `releases/ny/` ($345.8M) are sourced exclusively from it.
2. **`lobbyist_bimonthly` is the source of individual-lobbyist-person resolution + itemized expenses + finer time grain — NOT a source of additional compensation dollars.** When folded in, pull those columns; **drop `filing_compensation`** before any join.
3. **If both materialized outputs must be joined**, dedupe by `(reporting_year, principal_lobbyist, beneficial_client, contractual_client_name)` + half-year and keep `client_semiannual`'s `filing_compensation` — exactly equivalent to `SUM(bi periods)` for that half-year (verified $0 delta on 11/11 cells), and cheaper to read at semiannual grain.
4. **Naive concatenation of the two materialized outputs' `filing_compensation` columns = exact 2× double-count.** The rule is structurally tight — not a "best-practice precaution," a hard correctness invariant.

## Scope + open follow-ups

- **Sample is 5 firms × 11 cells.** Large enough to make the binary verdict ("they overlap → don't sum") unambiguous, and to confirm the precise SUM equality on three distinct retainer shapes. NOT large enough to claim the rule holds for *every* of 1,333 firms × 4,373 clients in 2025 — a full-sample sanity check (run after the first bi pull lands) is recommended before the first cross-dataset build ships.
- **Public-corporation universe untested.** This probe only touches the retained-lobbyist universe (`client_semiannual` ↔ `lobbyist_bimonthly`). The public-corp datasets (`public_corp_registration` + `public_corp_bimonthly`) carry their own `compensation` column for in-house lobbyists; they don't overlap with the retained-lobbyist datasets but DO have their own internal reconciliation question (their registration is anticipated comp vs the bimonthly actual). Out of scope for #37.
- **`current_period_compensation` vs `compensation` semantics.** The semi field name and the bi field name differ but both project to the canonical `filing_compensation` via [`io/ny/columns.py`](../../../../src/lobby_analysis/io/ny/columns.py). This probe verifies the equality of the **summed totals**, which is what the operational rule needs. The two raw fields may have non-numeric semantics differences (e.g. anticipated vs actual) that don't surface at the totals level.
