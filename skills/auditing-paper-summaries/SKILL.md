---
name: Audit-Papers
description: Check papers/ structure for completeness and accuracy — every PDF has text extraction, every paper is indexed in PAPER_INDEX.md and summarized in PAPER_SUMMARIES.md, summaries are factually accurate. Prompts the user for discrepancies.
---

<required>
CRITICAL: Add the following steps to your Todo list using TodoWrite:

1. Check papers/ structure: every PDF has a text extraction, every paper is indexed
2. Run format audit script to identify summary gaps
3. Determine scope (full audit, recent additions, or specific entries)
4. For each entry in scope, read the paper and verify the summary
5. Fix factual errors, add missing numerical findings
6. Fix formatting issues flagged by the script
7. Report results and prompt user for any structural fixes
</required>

# Auditing Papers

Checks the papers/ structure for completeness, then verifies that summaries accurately represent their source papers.

Announce at start: "I'm using the Audit Papers skill to check the papers structure and verify summary accuracy."

## The Process

### Step 0: Check Papers Structure

Before auditing content, check structural completeness:

- [ ] Every PDF in `papers/` has a corresponding `.txt` in `papers/text/`
- [ ] Every paper in `papers/` has a one-line entry in `PAPER_INDEX.md`
- [ ] Every paper in `PAPER_INDEX.md` has a full entry in `PAPER_SUMMARIES.md`
- [ ] No phantom entries (indexed in PAPER_INDEX but PDF missing)

**Report structural issues first and prompt the user:**
```
Found 3 structural issues:
- papers/Smith_2025_deployment.pdf has no text extraction in papers/text/
- papers/Jones_2024_scaling.pdf is not in PAPER_INDEX.md
- PAPER_INDEX.md lists "Chen 2025" but no PDF exists

Want me to fix these? (I can extract text and add index entries, but missing PDFs need to be downloaded.)
```

Fix only what the user approves. Then proceed to content audit.

### Step 1: Run Format Audit Script

Run the bundled script to get the full picture:

```
python3 SKILLS_DIR/auditing-paper-summaries/audit_paper_summaries.py REPO_ROOT
```

This identifies: missing metadata fields, entries without numerical findings, missing Key findings sections, missing PDFs or text extractions, and reference-only entries.

### Step 2: Determine Scope

Ask the user which scope to use:

- Recent additions: entries added since last audit (check git log for PAPER_SUMMARIES.md)
- Specific section: a category like "Agent Evaluation" or specific papers by name
- Priority list: entries flagged by the script as lacking numerical findings
- Full audit: every entry (expensive — 100+ papers)

For full audits, use parallel subagents to verify multiple papers simultaneously.

### Step 3: Verify Each Entry Against Source Paper

For each entry in scope:

- [ ] Read the extracted text from papers/text/ARXIV_ID.txt
- [ ] If no text extraction exists, read the PDF directly
- [ ] Compare the summary against the paper, checking:

Factual accuracy:
- Do cited numbers match the paper? (percentages, counts, ratios)
- Are benchmark names and results correct?
- Are author attributions and affiliations accurate?
- Are method names and architectural claims correct?
- Are date and arXiv ID correct?

Completeness of core findings:
- Are the paper's main quantitative results included?
- Are range estimates provided where the paper gives them?
- Are key comparisons to baselines captured?
- Is the central contribution accurately described?

### Step 4: Fix Errors

For each issue found:

- Factual errors: correct the claim to match the paper, noting the source section
- Missing numerical findings: extract key numbers with context (not raw numbers in isolation — always include what was measured, the baseline, and the result)
- Formatting: ensure consistent structure (arXiv, Authors, Date, File, Summary, Key findings, Relevance)

Reference-only entries (no local PDF) should be flagged but not audited for factual accuracy unless the user specifically requests it.

### Step 5: Report Results

Present findings per entry: what was verified, what was corrected, what was added. Flag any entries where the summary substantially misrepresents the paper.

## Required Format for Each Entry

```
### Paper Title

- arXiv: [ID](URL)
- Authors: Names (Affiliations)
- Date: Month Year
- File: `filename.pdf`

Summary: [Core contribution and approach]

Key findings:
- [Finding with numerical result and context]
- [Finding with range estimate if available]
- [Comparison to baseline/prior work]

Relevance: [Why this paper matters for this research collection]
```

## Scoping Guidance

- A single entry takes 2-5 minutes to verify thoroughly
- For full audits of 100+ papers, use parallel subagents (batch of 5-10 papers each)
- Prioritize entries flagged as "no numerical findings" — these are most likely to be incomplete
- Reference-only entries (imported from other repos without local PDFs) are lower priority

## Common Mistakes

- Correcting numbers without checking the original table/figure in the paper
- Adding numbers out of context (e.g., "67%" without saying what was measured or what the baseline was)
- Trusting the abstract alone — key findings are often in results tables, not the abstract
