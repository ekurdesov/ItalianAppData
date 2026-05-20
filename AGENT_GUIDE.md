# Agent Guide — ItalianDataA1

This repo uses a merged lesson format.

There are no separate `en/` and `ru/` lesson trees.
Each lesson lives in one file under `lessons/` and contains `it`, `en`, and `ru` data together.

## Project layout

```text
ItalianDataA1/
  process/                 drop new PDFs here before processing
  IT/                      processed source PDFs
  lessons/                 merged lesson JSON files
  index.json               master lesson index
  extra/verbs.json         standalone extra verb paradigms
  DATA_CONTRACT.md         canonical schema
  PROCESSING_RULES.txt     condensed workflow rules
  VERB_EXTRACTION_RULES.md verb-table extraction rules
  extract_verb_tables.py   rebuilds verb tables in lessons/*.json
  extract_flashcard_image_map.py  generates flashcard_image_map.json for Nano Banana
```

## Current lesson file model

Each lesson file contains:
- `lesson_info`
- `language_rules`
- `flashcards`
- `classroom_instructions`
- `dialogues`
- `verb_tables`

All locale-aware fields use nested `en` and `ru` keys.
Italian source text remains in `it` fields or Italian-only fields like `title`.

See [DATA_CONTRACT.md](/Users/annakurdzesau/Dev/MobileApps/ItalianDataA1/DATA_CONTRACT.md) for the exact schema.

## Processing a new PDF

### 1. Identify lesson key

Example:
- `A1 Online L3-6.pdf`
- lesson id: `A1-L3-6`
- lesson file: `lessons/a3l6.json`

### 2. Read the PDF

Use `pdfplumber` and inspect enough slides to identify:
- title
- objectives
- grammar focus
- vocabulary focus
- classroom instructions
- dialogue fragments
- verb drill pages

Do not transcribe the whole deck.
These JSONs are structured lesson summaries, not full slide dumps.

### 3. Build or update one merged lesson file

Write one file in `lessons/`, not two locale files.

Rules:
- keep lesson title in Italian
- keep source Italian in all `it` examples and dialogue turns
- store English and Russian translations in sibling `en` and `ru` fields
- keep objectives under:

```json
"objectives": {
  "it": [...],
  "en": [...],
  "ru": [...]
}
```

### 4. Rebuild derived data when needed

If verb coverage changes:

```bash
python3 extract_verb_tables.py
```

After any flashcard changes:

```bash
python3 extract_flashcard_image_map.py
```

### 5. Update index.json

`index.json` must reference:
- the lesson `file`
- `flashcard_count`
- `language_rule_count`
- `dialogue_count`
- `verb_table_count`
- `extra_verbs_data_path`

`generated_at` should reflect the latest processing date.

## Verb extraction

Do not guess lesson verbs from memory.

Use [VERB_EXTRACTION_RULES.md](/Users/annakurdzesau/Dev/MobileApps/ItalianDataA1/VERB_EXTRACTION_RULES.md).

Important:
- scan pages labeled `VERBI`, `VERBO`, `VERBI IN -ARE/-ERE/-IRE/-ISC`, `VERBI IRREGOLARI`
- treat `(infinitive) ____` patterns as high-confidence evidence
- avoid OCR false positives
- only include verbs the lesson actually teaches or drills

## Flashcard images

Flashcards support an optional `image` field containing a filename (e.g. `"caffè.webp"`).
Images are generated externally via Nano Banana and stored in the app's asset bundle.

### Image map format (`flashcard_image_map.json`)

```json
{
  "caffè": { "description": "a cup of espresso coffee", "file": "caffè.webp", "generated": true },
  "libro": { "description": "a book", "file": "", "generated": false }
}
```

- `description` — English prompt for Nano Banana image generation.
- `file` — filename of the generated image (empty until generated).
- `generated` — `true` once the image has been created.

### When to regenerate

Run after processing any PDF (new flashcards get added automatically):

```bash
python3 extract_flashcard_image_map.py
```

The script preserves existing `file` and `generated` values — only new terms are appended with defaults.

### Rules

- Descriptions should be concrete, visual, and unambiguous — suitable for image generation.
- Abstract terms (grammar words, pronouns, conjunctions) may be skipped or given a symbolic description.
- The `image` field in lesson JSON is optional; not every flashcard needs one.

## Quality checklist

- JSON parses
- merged schema is preserved
- no stale `translation_en` / `translation_ru` fields in `verb_tables`
- no stale references to `en/` or `ru/` lesson trees
- `index.json` counts match the real lesson file
- `extra/verbs.json` stays aligned with the standalone verb inventory

## Practical rule

If you are about to create or update lesson content and you find yourself planning separate locale files, stop.
The correct output is one merged file in `lessons/`.
