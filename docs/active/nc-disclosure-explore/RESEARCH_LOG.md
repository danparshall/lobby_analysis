# Research Log — nc-disclosure-explore

Branch goal (per kickoff): **catalog NC's publication shape for the compendium practical-availability axis.** First state being characterized after the 2026-05-24 gather-first pivot. NOT an ingestion-pipeline branch — pure characterization.

Newest entries first.

---

## Session: 2026-05-25 — [20260525_nc_disclosure_initial_look](convos/20260525_nc_disclosure_initial_look.md)

### Topics Explored
- Profiled `NC_2026.xlsx` (NC SoS term-based registration export, 2,964 rows of lobbyist↔principal pairs for Term=2025)
- Recovered source URL ([NC SoS Lobbying Download](https://www.sosnc.gov/online_services/lobbying/download))
- Web-fetched the SoS download page; web-searched whether other NC agencies publish lobbying data
- Inspected 4 additional `daily_*.xls` files the user had downloaded — turned out to be NC's "real-time Directory" exports (a different bulk-download surface)
- Consolidated all 5 NC files into `~/data/lobby_analysis/disclosures/NC/` with type-meaningful names

### Provisional Findings
- **NC publishes only registration-side data as free bulk download.** No expenditure, contact log, gift, or bills-lobbied data in any free bulk file. Quarterly expense reports exist legally and are filed with SoS but require per-record web search (no scripted access) or paid SoS Data Subscription Services for bulk.
- **Two distinct free bulk surfaces exist:** (1) term-based export at `/download` page = `NC_2026.xlsx` (no email, term-keyed, 2,964 pairs); (2) real-time Directory export = 4 separate files for lobbyists / principals / state-agency-liaisons / local-govt-liaisons (with email, ~6,366 rows combined). These have different schemas, different row counts, and different content emphasis.
- **Liaison registries (state agency + local govt) are a category the term export omits entirely.** 100 state-agency liaisons + 6 local-govt liaisons. This is the "covered-officials" side of the lobbying graph — useful for future activity-data joins if those reports ever become accessible.
- **Schema-vs-reality finding for the compendium:** NC concretely demonstrates that the `practical_availability` axis likely needs more than yes/no — at minimum tiered to capture (a) free + bulk + scriptable, (b) free + per-record manual, (c) paid bulk. Worth surfacing for v2.2 design.
- **Data-quality observations on the term export:** 53 dup-pair groups (45 byte-identical, 8 meaningful); `PrinTitle` 100% null; `SqlLogUserIp` is the literal `'False'` everywhere; heavy-tailed lobbyist→principal distribution (top: 63 principals).

### Results
- [results/20260525_nc_file_inventory.md](results/20260525_nc_file_inventory.md) — file inventory, full schemas, entity counts, top-lobbyist tail

### Next Steps
- **Profile the 4 directory files** with the same depth as `NC_2026.xlsx` (counts, uniques, nulls, dups, email coverage)
- **Reconcile the row-count discrepancy** between `NC_directory_lobbyists.xlsx` (3,198 pairs) and `NC_2026.xlsx` (2,964 pairs) — different snapshot date, different inclusion criteria, or different denormalization?
- **Walk the 181 compendium rows for NC** with the bulk-download surface as the answer set — produces a concrete column for the practical-availability matrix
- **Decide whether the tiered practical-availability finding is a v2.2 design item.** Don't act unilaterally; raise it in the next v2.2 conversation
- **Optional:** investigate SoS Data Subscription Services price / terms (project-strategic); pull "all previous terms" download if multi-vintage characterization is wanted
