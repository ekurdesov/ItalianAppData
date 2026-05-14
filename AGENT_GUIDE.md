# Agent Guide — ItalianDataA1 PDF Processing

This document tells any AI agent exactly how to process new lesson PDFs and produce the correct output files.

---

## Project layout

```
ItalianDataA1/
  process/        ← drop new PDFs here before processing
  IT/             ← move each PDF here after processing
  en/             ← English lesson JSONs  (e.g. a3l6.json)
  ru/             ← Russian lesson JSONs  (e.g. a3l6.json)
  index.json      ← master lesson index, must be updated after each batch
  PROCESSING_RULES.txt  ← canonical rules (read this too)
```

---

## Step-by-step workflow

### 1. Identify what needs processing

List files in `process/` that are not yet in `index.json`.  
Example: `A1 Online L3-6.pdf` → lesson id `A1-L3-6` → files `en/a3l6.json` + `ru/a3l6.json`.

**Filename → id mapping**
- `A1 Online L3-6.pdf` → id `A1-L3-6`, file key `a3l6`
- Pattern: `A<level> Online L<unit>-<lesson>.pdf` → `A<level>-L<unit>-<lesson>` / `a<level>l<lesson>.json`
- Level number: `A1` → `a1`, `A2` → `a2`, etc.  Unit 3 lesson 6 → `a3l6`.

### 2. Extract content from the PDF

These are presentation slide exports (not clean text). Use `pdfplumber` (already installed):

```python
import pdfplumber

with pdfplumber.open("process/A1 Online L3-6.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            print(text)
```

**What to look for across slides:**
- Lesson title and unit name (usually on the first slide)
- Objectives list (often a bullet slide near the start)
- Grammar focus: verb conjugations, article rules, preposition patterns, etc.
- Vocabulary: themed word lists, flashcard-style items
- Classroom instructions: imperative phrases like "Ascoltate", "Completate", "Ripetete"
- Dialogue fragments: any exchange between two speakers (A/B or named characters)
- Reading/listening topic title

Many slides render with garbled or sparse text due to PDF export quirks. Read enough pages to identify all of the above. Do not transcribe every slide verbatim.

### 3. Build the English JSON (`en/a<X>l<Y>.json`)

Follow this exact schema (two-space indentation, valid JSON):

```json
{
  "lesson_info": {
    "id": "A1-L3-6",
    "title": "<Italian unit title>",
    "level": "A1",
    "objectives": ["<Italian wording from deck>", "..."]
  },
  "language_rules": [
    {
      "category": "Grammar | Vocabulary | Pragmatics | Phonetics",
      "rule": "<short rule name>",
      "description": "<plain English explanation, beginner-friendly>",
      "conjugations": { "io": "...", "tu": "...", "lui/lei/Lei": "...", "noi": "...", "voi": "...", "loro": "..." },
      "examples": [
        { "it": "<Italian sentence>", "translation": "<English translation>" }
      ]
    }
  ],
  "flashcards": [
    { "term": "<Italian word/phrase>", "definition": "<English>", "type": "<noun|verb|adjective|phrase|...>" }
  ],
  "classroom_instructions": [
    { "it": "<Italian imperative>", "translation": "<English>" }
  ],
  "dialogues": [
    {
      "id": "D-A1L3-6-01",
      "title": "<dialogue title>",
      "register": "informal | formal | neutral",
      "context": "<one sentence describing the situation>",
      "turns": [
        { "speaker": "A", "it": "...", "translation": "..." }
      ],
      "practice_prompts": [
        { "cue": "<English cue>", "expected_it": "<Italian starter>" }
      ]
    }
  ]
}
```

**Rules:**
- `conjugations` only when the rule is a verb pattern.
- `dialogues` is optional — include only when the lesson has usable exchanges.
- `practice_prompts` inside dialogues is optional.
- Objectives: keep Italian wording from the deck.
- 4–6 `language_rules`, distilled and practical.
- Flashcards: lesson vocabulary only, not random extras.
- Match tone/density of `en/a3l1.json` and `en/a3l2.json`.

### 4. Build the Russian JSON (`ru/a<X>l<Y>.json`)

Same structure and same Italian content (`it` fields stay Italian everywhere).  
Localize:
- `lesson_info.objectives` → translate to Russian, keep lesson title in Italian
- `language_rules[].category` → Russian (e.g. "Грамматика", "Лексика", "Прагматика", "Фонетика")
- `language_rules[].rule` → Russian
- `language_rules[].description` → Russian
- `examples[].translation` → Russian
- `flashcards[].definition` → Russian
- `flashcards[].type` → Russian (e.g. "глагол", "существительное", "прилагательное")
- `classroom_instructions[].translation` → Russian
- `dialogues[].context` → Russian
- `dialogues[].turns[].translation` → Russian
- `dialogues[].practice_prompts[].cue` → Russian

### 5. Update `index.json`

Add an entry to the `lessons` array:

```json
{
  "id": "A1-L3-6",
  "title": "<Italian unit title>",
  "level": "A1",
  "objectives": ["<same as lesson_info.objectives in EN file>"],
  "file": "a3l6.json",
  "flashcard_count": <exact count>,
  "language_rule_count": <exact count>,
  "dialogue_count": <exact count>
}
```

Also:
- Increment `version` by 1.
- Update `generated_at` to today's date (`YYYY-MM-DD`).
- Counts must exactly match the created JSON.

### 6. Move the PDF

After both JSON files are written and `index.json` is updated, move the source PDF:

```
process/A1 Online L3-6.pdf  →  IT/A1 Online L3-6.pdf
```

---

## Translation capability

I (Kiro/Claude) can produce Russian translations directly from Italian without calling any external API. The previous workflow used OpenAI Codex for translations, but that is not required — I can translate Italian → Russian and Italian → English natively as part of JSON generation.

If translation quality needs to be verified or a specific term is uncertain, flag it with a comment in the session but do not leave placeholder text in the JSON.

---

## Quality checklist before finishing

- [ ] JSON is valid (no trailing commas, correct nesting)
- [ ] Two-space indentation throughout
- [ ] All `it` fields contain Italian
- [ ] `en/` translations are English, `ru/` translations are Russian
- [ ] `flashcard_count`, `language_rule_count`, `dialogue_count` in `index.json` match actual array lengths
- [ ] `version` bumped, `generated_at` updated
- [ ] PDF moved from `process/` to `IT/`
- [ ] Lesson title stays Italian in both locale files

---

## Current state (as of 2026-05-14)

Processed lessons (in `IT/` + JSON exists): A1-L1-1 through A1-L3-5  
Pending in `process/`: L3-6, L3-7, L3-8, L3-9, L4-1, L4-2, L4-3, L4-4  
Next expected ids: A1-L3-6, A1-L3-7, A1-L3-8, A1-L3-9, A1-L4-1, A1-L4-2, A1-L4-3, A1-L4-4  
Current `index.json` version: 5  
