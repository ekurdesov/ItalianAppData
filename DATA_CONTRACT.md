# JSON Data Contract — ItalianDataA1 (bilingual merged format)

## File layout

```
index.json          master lesson index
library.json        generated single-word Italian library
lessons/{file}      one bilingual JSON per lesson (replaces en/ and ru/)
```

Load path: `lessons/{file}` where `file` comes from `index.json`.  
All locales are in a single file. Access translated fields with the locale key `"en"` or `"ru"`.

`library.json` is a generated helper file for phrase-building and vocabulary reuse. It aggregates reusable single-word Italian entries from lesson flashcards, single-word rule examples, and verb tables.

---

## index.json

```json
{
  "version": 6,
  "generated_at": "YYYY-MM-DD",
  "locale_data_path": "lessons/{file}",
  "notes": "string",
  "lessons": [ LessonIndex ]
}
```

### LessonIndex entry

```json
{
  "id":                   "A1-L3-6",
  "title":                "string",    // Italian unit title
  "level":                "A1",
  "objectives":           ["string"],  // Italian wording
  "file":                 "a3l6.json",
  "flashcard_count":      30,
  "language_rule_count":  5,
  "dialogue_count":       1,
  "verb_table_count":     6
}
```

---

## Lesson file (`lessons/*.json`)

```json
{
  "lesson_info":            LessonInfo,
  "language_rules":         [LanguageRule],
  "flashcards":             [Flashcard],
  "classroom_instructions": [ClassroomInstruction],
  "dialogues":              [Dialogue],
  "verb_tables":            [VerbTable]
}
```

### LessonInfo

```json
{
  "id":    "A1-L3-6",
  "title": "string",          // Italian — same for all locales
  "level": "A1",
  "objectives": {
    "it": ["string"],         // Italian (source wording)
    "en": ["string"],
    "ru": ["string"]
  }
}
```

### LanguageRule

```json
{
  "category":    { "en": "Grammar",  "ru": "Грамматика" },
  "rule":        { "en": "string",   "ru": "string" },
  "description": { "en": "string",   "ru": "string" },
  "conjugations": {                  // optional — only on verb rules
    "io": "string", "tu": "string", "lui/lei/Lei": "string",
    "noi": "string", "voi": "string", "loro": "string"
  },
  "examples": [
    {
      "it":      "string",           // always Italian
      "en":      "string",
      "ru":      "string",
      "context": "string"            // optional: "informal", "formal", etc.
    }
  ]
}
```

### Flashcard

```json
{
  "term": "string",                  // always Italian
  "en":   "string",
  "ru":   "string",
  "type": { "en": "verb", "ru": "глагол" }
}
```

### ClassroomInstruction

```json
{
  "it": "string",
  "en": "string",
  "ru": "string"
}
```

### Dialogue

```json
{
  "id":       "D-A1L3-6-01",
  "title":    "string",              // Italian title
  "register": "informal | formal | neutral",
  "context":  { "en": "string", "ru": "string" },
  "turns": [
    {
      "speaker": "A | B | name",
      "it":      "string",
      "en":      "string",
      "ru":      "string"
    }
  ],
  "practice_prompts": [              // optional
    {
      "cue":         { "en": "string", "ru": "string" },
      "expected_it": "string"
    }
  ]
}
```

### VerbTable

```json
{
  "infinitive":  "essere",
  "translation": { "en": "to be", "ru": "быть" },
  "forms": {
    "io":          "sono",
    "tu":          "sei",
    "lui/lei/Lei": "è",
    "noi":         "siamo",
    "voi":         "siete",
    "loro":        "sono"
  },
  "pronoun_labels": {
    "io":          { "en": "I",                   "ru": "я"         },
    "tu":          { "en": "you (sg.)",            "ru": "ты"        },
    "lui/lei/Lei": { "en": "he/she/you (formal)",  "ru": "он/она/Вы" },
    "noi":         { "en": "we",                   "ru": "мы"        },
    "voi":         { "en": "you (pl.)",            "ru": "вы"        },
    "loro":        { "en": "they",                 "ru": "они"       }
  }
}
```

---

## Optionality

| Field | Required |
|---|---|
| `language_rules[].conjugations` | only on verb-pattern rules |
| `language_rules[].examples[].context` | optional |
| `dialogues` | always present, may be `[]` |
| `dialogues[].practice_prompts` | optional |
| `verb_tables` | always present, may be `[]` |

---

## Client-side usage

**Lesson list** — read `index.json` only; use `*_count` fields for badges without loading lesson files.

**Flashcard mode**
```js
card.term          // Italian question
card[locale]       // answer in user's locale
card.type[locale]  // localised type label
```

**Verb practice mode**
```js
for (const vt of lesson.verb_tables) {
  display(vt.infinitive, vt.translation[locale])
  for (const pronoun of Object.keys(vt.forms)) {
    label  = vt.pronoun_labels[pronoun][locale]
    answer = vt.forms[pronoun]
  }
}
```

**Dialogue reader**
```js
turn.it            // Italian line
turn[locale]       // translation toggle
dialogue.context[locale]
```

**Switching locale** — no file reload needed; just change the locale key used to access translated fields.

---

## library.json

```json
{
  "version": 1,
  "generated_at": "YYYY-MM-DD",
  "source": "lessons/*.json",
  "notes": "string",
  "item_count": 123,
  "items": [LibraryItem]
}
```

### LibraryItem

```json
{
  "it": "caffè",
  "en": ["coffee", "espresso"],
  "ru": ["кофе", "эспрессо"],
  "types": [
    { "en": "drink", "ru": "напиток" }
  ],
  "forms": ["il caffè", "un caffè"],
  "lessons": ["A1-L1-1", "A1-L4-2"],
  "sources": [
    {
      "file": "a4l2.json",
      "lesson_id": "A1-L4-2",
      "kind": "flashcard",
      "it": "il caffè"
    }
  ]
}
```

`library.json` intentionally excludes multi-word phrases. Regenerate it with:

```bash
node build_library_json.js
```
