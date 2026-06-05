# Influence-Chain Closure Analysis

**Goal:** assemble the chain **company → lobbyist → lawmaker → bill**, with money on the edges, per state.
**Compiled:** 2026-06-05 · **Scope:** state-level, verified states only (unknowns excluded, not scored as negatives)
**Companion files:** `lobbying-disclosure-sample.md` (6-state deep schema), `lobbying-disclosure-50state-tracker.md` (official sources), plus the two research reports (official 50-state; third-party pipelines).

---

## The reframe: this is a connectivity problem, not a coverage problem

"4 of 6 categories present" is the wrong test. What matters is whether the **join path closes** — whether shared keys let you traverse from a company to the bills it influenced and the lawmakers attached to those bills, with spending on the edges. A state with six disconnected tables is useless; a state with four *joinable* tables is gold.

### The chain decomposes into edges, and the two halves live in different datasets

| Edge | Source | Availability |
|---|---|---|
| **company → lobbyist** (hired-by) | lobbying registration | **Near-universal** — rarely the problem |
| **company/lobbyist → $** (paid/spent) | lobbying expenditure reports | ~19 "spending states" (OpenSecrets list); grain varies (co→firm vs co→lobbyist) |
| **company/lobbyist → bill** (lobbied-on) | lobbying activity/linkage | Present where bills tracked; **degrades to subject-matter in many states** |
| **lawmaker → bill** (sponsor/committee/vote) | **legislative data (Open States/Plural)** — NOT lobbying data | **All 50 states**, clean, bill-keyed |
| **→ lawmaker** (who was lobbied) | lobbying contact disclosure | **Broken almost everywhere** in bulk form |

### The single most important consequence
**Your chain has two halves that join on the bill.** The lobbying half (company → lobbyist → bill + $) comes from disclosure data. The legislative half (lawmaker → bill) comes from **Open States/Plural**, which covers all 50 states with real bill IDs. They meet at the bill key.

**Therefore the empty "lawmaker" column in lobbying data matters far less than it first appears — *provided the bill key is a real bill number.*** If a state gives you company → lobbyist → **bill** + $, you pivot through the bill into Open States and recover sponsors, committee members, and votes for free. You never needed lobbying data to identify the lawmakers.

**This makes bill-number granularity the linchpin of the entire project.** Subject-matter coding ("Taxation," "Health") does NOT join to Open States; an actual bill number (SB 1047, A1749) does. So a state's subject-matter-only coding isn't "missing one category" — it *severs the bridge between your two data halves.*

---

## Chain-closure scorecard (verified states)

Edges scored: **Co→Lob** (registration link) · **→$** (spending) · **→Bill** (bill-level linkage vs. subject-matter only) · **Lawmaker via Open States** (always available if bill key is real). "Position/linkage" is treated as the lobbyist→bill linkage per your instruction (not directional stance).

| State | Co→Lob | →$ (spending) | →Bill | Lawmaker (via Open States on bill key) | **Chain status** |
|---|---|---|---|---|---|
| **New York** | ✅ open-data | ✅ open-data (transactional) | ✅ **bill-level** (lobbyist→bill→client) | ✅ (bill key real) | **CLOSES** — strongest in US |
| **Colorado** | ✅ download | ✅ transactional | ✅ **bill-level** (+ stance support/oppose) | ✅ | **CLOSES** — and uniquely has stance |
| **Wisconsin** | ✅ download (directory) | ⚠️ aggregate download / itemized search-only | ✅ **bill/matter-level** | ✅ | **CLOSES w/ caveat** — spending grain needs targeted query for itemized |
| **California** | ✅ download (raw bulk) | ✅ transactional | ❌ **subject-matter only** | ✖ bridge broken at bill | **BREAKS at bill** — needs topic→bill resolution |
| **Texas** | ✅ download (Excel/CSV) | ✅ transactional (banded $) | ❌ **subject-matter only** | ✖ | **BREAKS at bill** — + spending is in bands, not exact |
| **Illinois** | ✅ open-data (daily) | ⚠️ exp via records request | ❌ **subject + agency intent, no bill #** | ✖ | **BREAKS at bill** |
| **Washington** | ✅ open-data | ✅ transactional | ❌ subject/agency only | ✖ | **BREAKS at bill** (+ no-commercial-use, moot for you) |
| **Florida** | ✅ download | ✅ transactional (compensation) | ❌ none/subject | ✖ | **BREAKS at bill** |
| **North Carolina** | ✅ download (free + paid) | ✅ transactional | ❌ subject-area | ✖ | **BREAKS at bill** |
| **Ohio** | ✅ download (CSV) | ⚠️ search-only (transactional) | ❌ none | ✖ | **BREAKS at bill + spending search-only** |
| **Maryland** | ✅ search→export | ✅ transactional (search→export) | ❌ none | ✖ | **BREAKS at bill** |
| **Michigan** | ✅ search-only | ✅ search-only (transactional) | ❌ **none-collected (confirmed)** | ✖ | **BREAKS at bill; scraping banned → targeted records request only** |
| **Connecticut** | ✅ open-data + Excel | ✅ transactional (PDF reports) | ⚠️ "issues" tracked; bill-level unconfirmed | ? | **LIKELY breaks at bill — verify** |
| **Massachusetts** | ✅ search-only | ✅ search-only | ⚠️ bills on forms, bulk-export unconfirmed | ? | **VERIFY — bill data may exist, not bulk** |
| **New Jersey** | ✅ search-only | ⚠️ aggregate | ❌ none | ✖ | **BREAKS at bill + spending aggregate** |
| **Virginia** | ✅ search-only | ✅ search-only | ⚠️ subject; **NAMES officials lobbied (Sched A/B)** | partial — has lawmaker side directly! | **UNUSUAL — see note** |

### Two states that don't fit the pattern

**Colorado** is the only state that closes the chain *and* carries directional stance (support/oppose/amend/monitor per client per bill). For any analysis where the *direction* of influence matters, CO is the reference implementation.

**Virginia** is the inverse of everyone else: its lobbying data actually *names the officials lobbied* (Schedule A/B), so it has the normally-broken "→lawmaker" edge directly in the lobbying corpus — but it's CAPTCHA-gated and search-only, and the bill side is subject-matter. VA is the one place to study the lobbyist→lawmaker edge as *disclosed* (vs. imputed via bill sponsorship), if you can get past the CAPTCHA with targeted queries.

---

## What this means for strategy

### Tier 1 — chain closes from bulk data alone (build here first)
**New York, Colorado, Wisconsin.** Pull the lobbying bulk (company → lobbyist → bill + $), join to Open States on bill number for the lawmaker side. WI needs one targeted-query step to get itemized (not just aggregate) spending. These three give you the complete observed chain with no imputation.

### Tier 2 — chain breaks only at the bill join (the big, valuable states)
**California, Texas, Illinois, Washington, Florida, NC, Maryland.** You get company → lobbyist → **subject-matter** → $, fully from bulk. The break is that subject-matter won't join to Open States. Two ways to close it, in your stated order of preference:
- **Targeted queries:** once the bulk skeleton is built, resolve specific subject-matter entries to bills via targeted lookups (per-filing detail pages often name bills even when the bulk export only carries the subject code). This is a few hundred targeted requests per state, not wholesale scraping — legally and operationally the right tool.
- **Imputation (your fallback):** assign probable bills/lawmakers by matching (subject-matter × session × client industry) against Open States bills in that subject area. Lossy but reasonable for aggregate analysis; you flagged you have methods for this.

### Tier 3 — access-constrained, use targeted records requests
**Michigan** (scraping explicitly banned; bill data not collected at all — confirmed negative — so the chain *cannot* close to bill level here regardless of effort; treat lawmaker-linkage as unavailable and rely on spending + registration only). **Virginia** (CAPTCHA; but uniquely has the lawmaker edge — worth targeted effort).

### The standing architectural decision
**Source the lawmaker → bill edge from Open States/Plural for all 50 states, not from lobbying data.** Build it once as a bill-keyed spine. Then every state's lobbying data just needs to reach a *real bill number* to light up the full chain. This converts the per-state problem into a single question: **"can I get this state's lobbying activity to bill-number granularity — via bulk, or via targeted query if not?"**

---

## Open questions before scaling
1. **Spending grain consistency:** states variously report company→firm vs company→lobbyist vs banded ranges (TX). For "W company spends X via Y lobbyist," TX's banded compensation and WI's aggregate download are the known degradations — both fixable with targeted queries but flag the grain per state.
2. **The subject→bill resolution rate** in Tier 2 states is unmeasured. Worth a small pilot (one state, one session) to see what fraction of subject-matter filings can be resolved to specific bills via targeted detail-page queries before committing to the approach across all of Tier 2.
3. **~28 unverified states** still need the deep pass; this scorecard only covers verified states. Several (Iowa, Rhode Island) are flagged as likely bill-level and would land in Tier 1 if confirmed.
