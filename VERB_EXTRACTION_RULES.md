# Verb Extraction Rules

This document defines how to rebuild `verb_tables` in the current merged-schema repo.

Use it together with:
- [DATA_CONTRACT.md](/Users/annakurdzesau/Dev/MobileApps/ItalianDataA1/DATA_CONTRACT.md)
- [extract_verb_tables.py](/Users/annakurdzesau/Dev/MobileApps/ItalianDataA1/extract_verb_tables.py)

## Scope

This repo no longer uses separate `en/` and `ru/` lesson trees.

Verb extraction now targets:
- `lessons/*.json`
- `index.json`
- optionally `library.json` after regeneration

The extractor must write `verb_tables` in the merged lesson format:

```json
{
  "infinitive": "andare",
  "translation": {
    "en": "to go",
    "ru": "идти / ехать"
  },
  "forms": {
    "io": "vado",
    "tu": "vai",
    "lui/lei/Lei": "va",
    "noi": "andiamo",
    "voi": "andate",
    "loro": "vanno"
  },
  "pronoun_labels": {
    "io": { "en": "I", "ru": "я" },
    "tu": { "en": "you (sg.)", "ru": "ты" },
    "lui/lei/Lei": { "en": "he/she/you (formal)", "ru": "он/она/Вы" },
    "noi": { "en": "we", "ru": "мы" },
    "voi": { "en": "you (pl.)", "ru": "вы" },
    "loro": { "en": "they", "ru": "они" }
  }
}
```

## Source Of Truth

The source of truth is the PDF content in `IT/*.pdf`, not the current lesson JSON and not an old hardcoded mapping.

The mapping inside `extract_verb_tables.py` is only a materialized result of the latest PDF scan.
If the PDFs change, re-scan and update the mapping.

## What Counts As A Lesson Verb

Add a verb to `verb_tables` when at least one of these is true:

1. The PDF has a dedicated verb exercise page for that infinitive.
Examples:
- `VERBI IN -ARE`
- `VERBI IN -ERE`
- `VERBI IN -IRE`
- `VERBI IN -ISC`
- `VERBI IRREGOLARI`
- `Completate con il verbo ...`

2. The PDF shows the infinitive explicitly in exercise notation.
Examples:
- `(comprare) ____`
- `(io-finire) ____`
- `(tu-chiamarsi) ____`

3. The PDF lesson objective explicitly teaches that verb or verb group.
Examples:
- `grammatica verbo stare`
- `verbi irregolari andare/fare`

4. The lesson contains a high-signal repeated verb used as part of a verb drill or structured completion set, even if not shown as a standalone six-form table.

Do not add a verb just because it appears once in a reading or dialogue.

## Strong Signals To Scan For

When reading a PDF, inspect pages containing:
- `VERBO`
- `VERBI`
- `VERBI REGOLARI`
- `VERBI IRREGOLARI`
- `VERBI IN -ARE`
- `VERBI IN -ERE`
- `VERBI IN -IRE`
- `VERBI IN -ISC`
- `Completate`
- the pronoun sequence `io`, `tu`, `lui`, `noi`, `voi`, `loro`

These pages are the most likely to contain missing verbs.

## Extraction Heuristics

### High-confidence patterns

Treat these as reliable evidence:

- infinitive inside parentheses:
  - `(abitare)`
  - `(voi-capire)`
  - `(io-finire)`

- headings that name verbs directly:
  - `Essere, chiamarsi o studiare?`
  - `Completate con il verbo andare`

- irregular verb lesson headers:
  - `verbi irregolari andare/fare`

### Medium-confidence patterns

Treat these as candidates that still need human judgment:

- infinitives listed in objective slides
- repeated infinitives on multiple neighboring exercise pages
- verb game pages where the drill clearly targets finite forms

### Low-confidence patterns

Do not add automatically from these alone:

- a single occurrence in a reading passage
- a single occurrence in dialogue text
- nouns or false positives ending in `-are`, `-ere`, `-ire`

Examples of false positives seen in scans:
- `cameriere`
- `quartiere`
- OCR garbage like `mare`, `care`, `gare`

## Human Review Rules

The extractor should be conservative enough to avoid obvious garbage, but final inclusion still needs judgment.

Before adding a verb, check:

1. Is it really an infinitive and not an OCR artifact?
2. Is the lesson teaching or drilling it, rather than merely using it?
3. Does it fit A1 scope for this lesson?
4. Do we already have a correct paradigm and translation in `VERB_DATA`?

## Translation Rules

Each verb in `VERB_DATA` must have:
- natural English infinitive translation
- natural Russian infinitive translation

Prefer practical beginner wording.

Examples:
- `prendere`: `to take` / `брать / заказывать / садиться на транспорт`
- `fare`: `to do / to make` / `делать / совершать`
- `piacere`: `to like / to please` / `нравиться`

Avoid overly literal or narrow translations if the lesson uses the verb more broadly.

## Lesson-Level Rules

Do not force every detected verb into every nearby lesson.

The lesson should receive only verbs that are actually taught or drilled in that lesson's PDF.

Examples from the current corpus:
- `a3l4` should include `amare` because the PDF contains `Amo molto l'Italia.`
- `a4l3` should include `viaggiare`, `pulire`, `restare` because they appear in the `VERBI IN -ISC` drill
- `a3l3` should include many regular verbs because the lesson has multiple dedicated `VERBI IN -ARE/-ERE` pages

## After Updating Verb Tables

Whenever `verb_tables` change:

1. Rewrite the affected `lessons/*.json`
2. Update `index.json`
   - `verb_table_count` must equal `len(lesson.verb_tables)`
   - update `generated_at`
3. Regenerate `library.json`

Command:

```bash
python3 extract_verb_tables.py
node build_library_json.js
```

## Validation Checklist

Before finishing:

- all lesson JSON files parse
- `index.json` parses
- `library.json` parses after regeneration
- `verb_table_count` values in `index.json` match real counts
- no stale old-schema fields like `translation_en` or `translation_ru` remain in `verb_tables`
- newly added verbs appear in both lesson JSON and `library.json`

## Common Past Failure Modes

These caused misses before and must be avoided:

1. Using a stale hardcoded lesson-to-verb mapping without rechecking the PDFs
2. Assuming only the "main grammar verb" belongs in `verb_tables`
3. Ignoring later exercise pages labeled `VERBI`
4. Missing verbs that appear in completion syntax like `(amare)` or `(viaggiare)`
5. Reusing the old split-locale extractor logic in a merged-schema repo

## Current Practical Rule

If a PDF page has:
- at least one explicit infinitive in parentheses, or
- a `VERBI` heading plus multiple finite-form blanks, or
- a full six-person drill,

that page must be reviewed for `verb_tables`.
