#!/usr/bin/env python3
"""
Normalize US-state-tradition rubric items to a common framing.

Each rubric in the state tradition (Opheim, Newmark2005/2017, CPI_HiredGuns,
OpenSecrets, Sunlight, CPI_2015) wraps the underlying concept in a different
syntactic frame:
  - HiredGuns: 'Is a lobbyist required to file X?'
  - Newmark2017: 'Disclosure required: X' / 'X necessitates registering'
  - OpenSecrets: 'Is there X?' / 'How easily can X?'
  - Newmark2005, Opheim: bare noun phrases (mostly)
  - CPI_2015, Sunlight: short category labels

After embedding the raw text, items cluster much more strongly within their
own rubric than with semantically-equivalent items in other rubrics. This
script strips the framing so equivalent items present a more uniform surface
to the embedding model.

Reads:  docs/active/compendium-source-extracts/results/cross_rubric_items_clustered.csv
Writes: docs/active/compendium-source-extracts/results/cross_rubric_items_state_normalized.csv

The output CSV has the same columns plus 'indicator_text_raw' (preserved
original) and 'indicator_text' (normalized). It is restricted to state-tradition
rubrics so the downstream embed run is scoped to ~134 items.
"""
import re
import sys
from pathlib import Path

import pandas as pd

STATE_RUBRICS = ['CPI_2015', 'HiredGuns', 'Newmark2005', 'Newmark2017',
                 'OpenSecrets', 'Opheim', 'Sunlight']

# Per-rubric (pattern, replacement) lists. Applied in order. Replacement of '' drops.
# Patterns are designed to strip the framing scaffold without losing the noun phrase.
RULES = {
    'HiredGuns': [
        # PDF text-encoding ligatures
        (r'ﬁ', 'fi'),
        (r'ﬂ', 'fl'),
        # Trailing question mark
        (r'\?\s*$', ''),
        # 'In addition to X, does the deﬁnition recognize Y?' -> 'definition recognizes Y in addition to X'
        (r'^In addition to (.+?), does the definition recognize (.+?)$',
         r'definition recognizes \2 in addition to \1'),
        # Long question prefixes (apply before the more general 'is required to' rule)
        (r'^How often during each two-year cycle is (.+?)$', r'frequency: \1'),
        (r'^How often is (.+?)$', r'frequency: \1'),
        (r'^How often are (.+?)$', r'frequency: \1'),
        (r'^How many days can (.+?) before (.+?)$', r'days before \2: \1'),
        (r'^How many days (.+?)$', r'days for \1'),
        (r'^Within how many days must (.+?) (.+?)$', r'days within which \1 \2'),
        (r'^How much does (.+?) have to (.+?) to (.+?)$', r'threshold to \3: \1 \2'),
        (r'^What is the statutory provision for (.+?)$', r'\1'),
        (r'^What spending must be (.+?)$', r'spending \1'),
        (r'^When was (.+?)$', r'\1'),
        (r'^Where (.+?)$', r'\1'),
        # Are/Is questions
        (r'^Are summaries \(totals\) of (.+?) classified by (.+?)$',
         r'summary totals of \1 classified by \2'),
        (r'^Are sample (.+?) available (.+?)$', r'sample \1 availability \2'),
        (r'^Is there a "cooling off" period required (.+?)$',
         r'cooling-off period \1'),
        (r'^Is there a statutory penalty for (.+?)$', r'statutory penalty for \1'),
        (r'^Is a lobbyist required to (.+?)$', r'lobbyist required to \1'),
        (r'^Is a lobbyist who has (.+?)$', r'lobbyist who has \1'),
        (r'^Is an employer or principal of a lobbyist required to (.+?)$',
         r'employer or principal of lobbyist required to \1'),
        (r'^Is the lobbyist employer/principal on whose behalf (.+?) required to be (.+?)$',
         r'lobbyist employer/principal on whose behalf \1 \2'),
        (r'^Is the recipient of (.+?) required to be (.+?)$', r'recipient of \1 \2'),
        (r'^Is the date of (.+?) required to be (.+?)$', r'date of \1 \2'),
        (r'^Is a description of (.+?) required to be (.+?)$', r'description of \1 \2'),
        (r'^Is subject matter or bill number to be addressed by a lobbyist required on (.+?)$',
         r'subject matter or bill number on \1'),
        (r'^Is compensation/salary required to be reported (.+?)$',
         r'compensation/salary reported \1'),
        (r'^Is spending on (.+?) required to be reported$', r'spending on \1'),
        (r'^Does the oversight agency provide (.+?)$', r'oversight agency provides \1'),
        (r'^Does the state agency provide (.+?)$', r'state agency provides \1'),
        (r'^Does the state agency conduct (.+?)$', r'state agency conducts \1'),
        (r'^Does the state publish (.+?)$', r'state publishes \1'),
        (r'^Does the state have (.+?)$', r'state has \1'),
        # Generic interrogative fallbacks (apply after specific patterns)
        (r'^Is (.+?) required to be (.+?)$', r'\1 \2'),
        (r'^Is (.+?) required\s*$', r'\1'),
        (r'^Is there (.+?)$', r'\1'),
        # Whitespace cleanup
        (r'\s+', ' '),
    ],
    'Newmark2017': [
        # 'Disclosure required: X' -> 'X (disclosure required)'
        (r'^Disclosure required:\s*(.+?)$', r'\1 (disclosure)'),
        # 'X necessitates registering as a lobbyist' -> 'X (registration trigger)'
        (r'^(.+?) necessitates registering as a lobbyist\s*$', r'\1 (registration trigger)'),
        # 'X are defined as lobbyists if engaged in lobbying-related behaviors'
        (r'^(.+?) are defined as lobbyists if engaged in lobbying-related behaviors\s*$',
         r'\1 (lobbyist definition)'),
        # 'X standard for lobbyist status (state defines persons as lobbyists if Y)'
        (r'^(.+?) standard for lobbyist status \(.*?\)\s*$', r'\1 (lobbyist threshold)'),
        # 'Lobbyists prohibited from X' -> 'X (prohibited)'
        (r'^Lobbyists prohibited from (.+?)$', r'\1 (prohibited)'),
        # 'X is prohibited' / 'X is prohibited (...)' -> 'X (prohibited)'
        (r'^(.+?) is prohibited(\s*\(.+?\))?\s*$', r'\1 (prohibited)'),
        # 'Revolving door restrictions (X)' -> 'revolving door restrictions'
        (r'^Revolving door restrictions \(.*?\)\s*$', r'revolving door restrictions'),
        # 'Contingent compensation is prohibited (X)' -> handled by 'is prohibited' above
    ],
    'OpenSecrets': [
        (r'\?\s*$', ''),
        (r'^Who is (.+?)$', r'\1'),
        (r'^How much are (.+?)$', r'\1'),
        (r'^How easily can the public access (.+?)$', r'public access to \1'),
        (r'^Is there (.+?)$', r'\1'),
    ],
    'Opheim': [
        # 'X as a criterion for definition' -> 'X (definition criterion)'
        (r'^(.+?) as a criterion for definition\s*$', r'\1 (definition criterion)'),
        # 'X designated as lobbyists' -> 'X (lobbyist designation)'
        (r'^(.+?) designated as lobbyists\s*$', r'\1 (lobbyist designation)'),
        # 'specific X standard to delineate lobbying activity' -> 'X (lobbyist threshold)'
        (r'^specific (.+?) standard to delineate lobbying activity\s*$',
         r'\1 (lobbyist threshold)'),
    ],
    # Pass-through rubrics: nothing to strip
    'Newmark2005': [],
    'CPI_2015': [],
    'Sunlight': [],
}


def normalize(text: str, rubric: str) -> str:
    """Apply rubric-specific framing rules to one item."""
    out = text
    for pat, repl in RULES.get(rubric, []):
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    return out.strip()


def main():
    root = Path('docs/active/compendium-source-extracts/results')
    src = root / 'cross_rubric_items_clustered.csv'
    dst = root / 'cross_rubric_items_state_normalized.csv'
    if not src.exists():
        sys.exit(f'ERROR: source CSV not found: {src}')

    df = pd.read_csv(src).fillna('')
    df = df[df['paper'].isin(STATE_RUBRICS)].copy()
    df['indicator_text_raw'] = df['indicator_text']
    df['indicator_text'] = [normalize(t, p)
                            for t, p in zip(df['indicator_text'], df['paper'])]

    df.to_csv(dst, index=False)
    print(f'Wrote {dst}  ({len(df)} state-tradition items)')

    # Diff dump for eyeball verification
    print('\n=== Per-rubric before/after samples ===')
    for paper in STATE_RUBRICS:
        sub = df[df.paper == paper]
        if sub.empty:
            continue
        changed = sub[sub['indicator_text'] != sub['indicator_text_raw']]
        print(f'\n--- {paper}  (n={len(sub)}, changed={len(changed)}) ---')
        for _, row in sub.head(8).iterrows():
            mark = '*' if row['indicator_text'] != row['indicator_text_raw'] else ' '
            print(f'  {mark} BEFORE: {row["indicator_text_raw"][:100]}')
            if mark == '*':
                print(f'    AFTER:  {row["indicator_text"][:100]}')


if __name__ == '__main__':
    main()
