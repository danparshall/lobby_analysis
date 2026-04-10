---
name: maintaining-decision-docs
description: Use after creating or modifying decision documents in docs/ to keep DOCS_INDEX.md and DOCS_SUMMARY.md consistent. Also use as a standalone audit to find coverage gaps, broken links, and ADR format issues. Works across any repo with a docs/ directory. Run alongside updating-noridocs when finishing a branch that includes decision docs.
---

<required>
CRITICAL: Add the following steps to your Todo list using TodoWrite:

1. Discover docs directory and index files
2. Run coverage audit (find gaps)
3. Check ADR format compliance on recent/new docs
4. Check for broken Related: links
5. Update DOCS_INDEX.md with missing entries
6. Generate missing DOCS_SUMMARY.md entries
7. Report results to user
</required>

# Maintaining Decision Docs

Maintains the multi-level documentation index for project decision documents. Ensures DOCS_INDEX.md (one-line scan), DOCS_SUMMARY.md (paragraph summaries), and the individual docs stay consistent.

Announce at start: "I'm using the Maintaining Decision Docs skill to audit and update the docs index."

## The Process

### Step 1: Discover Docs Directory and Index Files

Locate the docs infrastructure in the current repo:

- [ ] Find the docs/ directory relative to repo root
- [ ] Check for docs/DOCS_INDEX.md — if missing, note for creation
- [ ] Check for docs/DOCS_SUMMARY.md — if missing, note for creation
- [ ] List all docs/2*.md files (decision docs use YYYYMMDD prefix)

If neither index file exists, ask the user if they want to initialize the framework.

If a bundled audit script exists, run it first to get the full picture:

```
python3 SKILLS_DIR/maintaining-decision-docs/audit_decision_docs.py REPO_ROOT
```

### Step 2: Run Coverage Audit

Compare docs on disk against index files:

- [ ] Find docs missing from DOCS_INDEX.md
- [ ] Find docs missing from DOCS_SUMMARY.md
- [ ] Find orphaned references (entries pointing to deleted docs)

### Step 3: Check ADR Format Compliance

For recently created or modified docs, check for: Date field, Status field, Context section, Decision section, Rationale section.

Only flag format issues on docs created after framework adoption. Mention non-compliant older docs in the report but don't block on them.

### Step 4: Check for Broken Related: Links

For each doc with Related: references, verify referenced documents exist on disk. Flag broken links and suggest possible matches.

Note: the audit script strips code blocks before checking links, but some example filenames in non-code-block sections may still appear as false positives. Use judgment.

### Step 5: Update DOCS_INDEX.md

For each missing doc, read it and add a one-line entry:

```
- `YYYYMMDD_name.md` — One-sentence description
```

If DOCS_INDEX.md doesn't exist, create it with a header linking to DOCS_SUMMARY.md, then add all docs.

### Step 6: Generate Missing DOCS_SUMMARY.md Entries

For each missing doc, read the full document and write a summary entry:

- Category, Status, Tags on the first line
- 2-4 sentence summary emphasizing "why" not just "what"
- Key decisions as bullets
- Related document links

Always read the complete document before writing a summary.

### Step 7: Report Results

Present a summary: coverage stats, format compliance, broken links, actions taken, and recommendations for docs that should be reformatted or reviewed.

## Integration

This skill handles docs/ decision documents. updating-noridocs handles docs.md code documentation. They are complementary — run both when finishing a branch with code changes and decision documents.

## Common Mistakes

- Writing summaries without reading the full doc first — leads to missed decisions and rationale
- Over-formatting old docs — only reformat when actively working with them
- Summarizing "what" instead of "why" — lead with the problem and rationale, not a table of contents

## Red Flags

Never skip reading a doc before summarizing it. Never delete docs from disk because they seem outdated — mark as Deprecated. Never rewrite the original doc's content in a summary — summarize, don't editorialize.

Always preserve the original doc's intent. Always use consistent tags. Always link related documents bidirectionally when possible.
