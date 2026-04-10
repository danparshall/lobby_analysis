---
name: Add-Paper
description: Add a paper to the research collection — download PDF, extract text, add to PAPER_INDEX.md and PAPER_SUMMARIES.md. Ensures every paper is fully integrated with text extraction and indexed summaries.
---

<required>
*CRITICAL* Add the following steps to your Todo list using TodoWrite:

1. Obtain the PDF
2. Extract text
3. Add entry to PAPER_INDEX.md
4. Read the paper and add entry to PAPER_SUMMARIES.md
5. Stage all new files
</required>

# Adding a Paper

Announce at start: "I'm using the Add Paper skill to integrate this paper into the collection."

## Step 1: Obtain the PDF

- If the user provides a URL: download to `papers/` using `curl -L -o papers/<filename>.pdf <url>`
- If the user provides a local file path: copy to `papers/`
- If the user just names a paper: search for it and confirm the URL before downloading

**Filename convention:** `AuthorLast_Year__short_description.pdf`
- Double underscore separates author/year from description
- Use snake_case for the description
- Examples: `Acemoglu_2024__simple_macroeconomics_AI.pdf`, `Eloundou_2023__gpts_are_gpts.pdf`

If the paper already exists in `papers/`, skip to Step 2.

## Step 2: Extract text

Extract the PDF text to `papers/text/` with the same base filename and `.txt` extension:

```bash
# Using pdftotext if available
pdftotext papers/<filename>.pdf papers/text/<filename>.txt

# If pdftotext is not available, use Python
python3 -c "
import subprocess
result = subprocess.run(['python3', '-m', 'pymupdf', 'convert', '-output', 'papers/text/<filename>.txt', 'papers/<filename>.pdf'])
"
```

If neither tool works, read the PDF directly using the Read tool and write the extracted content to `papers/text/<filename>.txt`. This is the fallback — it works but may lose some formatting.

Verify the extraction is reasonable: check the first ~20 lines to confirm it's not garbled.

## Step 3: Add to PAPER_INDEX.md

Add a one-line entry in the appropriate section (or create a section if needed):

```markdown
| Author (Year) | One-sentence description of what the paper contributes | `filename.pdf` |
```

Keep entries sorted by author within each section. If PAPER_INDEX.md doesn't exist yet, create it:

```markdown
# Paper Index

| Paper | Description | File |
|-------|-------------|------|
| Author (Year) | One-sentence description | `filename.pdf` |
```

## Step 4: Add to PAPER_SUMMARIES.md

Read the paper (use the extracted text from `papers/text/`). Write a summary entry:

```markdown
### Paper Title

- Authors: Names (Affiliations)
- Date: Month Year
- File: `filename.pdf`
- Source: [URL or DOI if available]

Summary: [2-3 sentences on core contribution and approach]

Key findings:
- [Finding with numerical result and context — not raw numbers, always include what was measured and the baseline]
- [Finding with range estimate if available]
- [Comparison to baseline/prior work]

Relevance: [1-2 sentences on why this paper matters for this research collection]
```

**Important:**
- Read the actual results tables and figures, not just the abstract. Key findings are often buried in the results.
- Always include numerical results with context (e.g., "67% accuracy on X, compared to 52% baseline" not just "67%")
- If the paper is long, focus on the sections most relevant to the research collection's focus

## Step 5: Stage files

```bash
git add papers/<filename>.pdf papers/text/<filename>.txt PAPER_INDEX.md PAPER_SUMMARIES.md
```

Do NOT commit — the user may be adding multiple papers or may want to review first.

# Adding Multiple Papers

If the user asks to add several papers at once:
- Process each paper through all 5 steps before moving to the next
- This ensures each paper is fully integrated before context moves on
- For bulk additions (5+), consider using subagents in parallel for text extraction and summary writing

# Common Mistakes

**Skipping text extraction**
- Problem: Future sessions can't search or discuss the paper's details without re-parsing the PDF
- Fix: Always extract, even if the current task doesn't need the text

**Writing summaries from the abstract only**
- Problem: Abstracts omit key numerical findings, edge cases, and limitations
- Fix: Read the results/discussion sections; check tables and figures

**Adding numbers without context**
- Problem: "The model achieved 0.73" means nothing without knowing what was measured, on what data, and what the baseline was
- Fix: Always include metric name, dataset, and comparison point

**Forgetting to update PAPER_INDEX when updating PAPER_SUMMARIES**
- Problem: Index and summaries get out of sync
- Fix: Always update both in the same operation
