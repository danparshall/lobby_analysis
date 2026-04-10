# PAPER_INDEX

One-sentence summary of every paper in `papers/`. Use this as the entry point for literature lookup; once you've found the right paper, check `PAPER_SUMMARIES.md` for the key findings, and `papers/text/` for the full extracted text.

## Papers

- **Bacik_2025__lobbyview_network_dynamics** (2025) — Presents LobbyView, a relational database integrating 1.6M+ federal LDA reports ($87B+ expenditures) with entity disambiguation across clients, registrants, lobbyists, government entities, and legislators, linked to Compustat/Orbis/BoardEx/VoteView; this is the federal gold standard the state-level pipeline aims to replicate. File: `papers/Bacik_2025__lobbyview_network_dynamics.pdf`
- **Kim_2025__ai_bill_positions_lobbying** (2025) — Uses GPT-4 (with a graph neural network refinement layer) to classify interest group positions on federal bills from LDA report text, validated at 96.93% accuracy vs. human labels on 391 dually-annotated samples, producing 279k bill positions across 12k interest groups — 5× more groups and 7× more bills than MapLight. File: `papers/Kim_2025__ai_bill_positions_lobbying.pdf`

---

**Format for new entries:**

```
- **[short_name]** ([year]) — [one-sentence summary]. File: `papers/[filename].pdf`
```
