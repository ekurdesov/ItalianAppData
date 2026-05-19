# UPDATE_SPEC — Lesson Rerun Additions

When reprocessing or regenerating lesson JSON files, apply these additional steps after the base lesson content is built.

---

## 1. Dialogues

### Source

Expanded dialogue outlines live in `dialogue-outlines-it-expanded.md`.

### Rules

- Each dialogue targets a primary lesson based on its "Source lessons" field (first listed lesson).
- Use the DATA_CONTRACT `Dialogue` schema: `id`, `title`, `register`, `context`, `turns`.
- Dialogue IDs follow the pattern `D-A1L{unit}-{lesson}-{seq}` where `seq` is zero-padded and increments from the last existing dialogue in that file.
- All turns must include `it`, `en`, `ru` fields.
- `register` is one of: `informal`, `formal`, `neutral`.
- `practice_prompts` are optional — include them only when the dialogue clearly drills a specific structure.

### Current Mapping (20 dialogues)

| # | Title | Target file | Dialogue ID |
|---|---|---|---|
| 1 | Primo giorno nel corso di italiano | a1l1.json | D-A1L1-1-02 |
| 17 | Lezione, aula e materiali | a1l1.json | D-A1L1-1-03 |
| 2 | Presentazione formale con la professoressa | a1l2.json | D-A1L1-2-05 |
| 14 | Compagni di gruppo | a1l5.json | D-A1L1-5-03 |
| 3 | Numero di telefono e compito | a1l7.json | D-A1L1-7-03 |
| 11 | In giro per Roma | a1l7.json | D-A1L1-7-04 |
| 4 | Di dove sei e che lingue parli? | a2l1.json | D-A1L2-1-03 |
| 5 | Come stai? Sensazioni e bisogni | a2l4.json | D-A1L2-4-04 |
| 18 | Intervista doppia | a2l5.json | D-A1L2-5-05 |
| 6 | Dove abiti? | a3l1.json | D-A1L3-1-03 |
| 10 | Alla festa di Chiara | a3l1.json | D-A1L3-1-04 |
| 15 | Una strana coppia di vicini | a3l2.json | D-A1L3-2-03 |
| 7 | Email, lettura e compiti | a3l3.json | D-A1L3-3-03 |
| 19 | Perché vai in biblioteca? | a3l3.json | D-A1L3-3-04 |
| 8 | Che lingue parli? | a3l4.json | D-A1L3-4-02 |
| 9 | Indovina chi | a3l6.json | D-A1L3-6-02 |
| 16 | Nomi e cognomi italiani | a3l8.json | D-A1L3-8-02 |
| 20 | Ripasso prima dell'esame | a3l9.json | D-A1L3-9-01 |
| 12 | Al bar | a4l1.json | D-A1L4-1-02 |
| 13 | Offro io | a4l4.json | D-A1L4-4-03 |

### On Rerun

1. After building base lesson content, check if the lesson file appears in the mapping above.
2. If yes, append the corresponding dialogue(s) to the `dialogues` array.
3. Do not duplicate — check by `id` before inserting.
4. Update `dialogue_count` in `index.json`.

---

## 2. Verb Tables

### Rules

- After building base lesson content, run `python3 extract_verb_tables.py` to rebuild verb tables from the PDF source of truth.
- If a lesson's PDF teaches or drills a verb (see `VERB_EXTRACTION_RULES.md`), that verb must appear in `verb_tables`.
- Cross-check: if a dialogue uses a verb that the lesson also teaches, ensure it's in `verb_tables`.
- Update `verb_table_count` in `index.json` after any changes.

### Common Missing Verbs to Watch For

These verbs are frequently used in dialogues and may be missing from lessons that drill them:

| Verb | Lessons that likely need it |
|---|---|
| andare | a4l1, a3l9 |
| fare | a4l1, a3l9 |
| prendere | a4l1, a4l2, a4l3, a4l4 |
| bere | a4l4 |
| volere | a4l4 |
| preferire | a4l4 |
| abitare | a3l1, a3l2 |
| leggere | a3l3 |
| scrivere | a3l3 |
| parlare | a3l4 |

### On Rerun

1. Run `python3 extract_verb_tables.py`.
2. Manually verify any lesson that gained new dialogues — the dialogue vocabulary may reveal verbs the lesson should include.
3. Update `index.json` counts.

---

## 3. Post-Update Checklist

After any rerun:

- [ ] All `lessons/*.json` files parse as valid JSON
- [ ] `index.json` parses and all `*_count` fields match actual arrays
- [ ] `generated_at` in `index.json` reflects the update date
- [ ] No duplicate dialogue IDs within a lesson file
- [ ] No stale `translation_en`/`translation_ru` fields in verb_tables
- [ ] `extra/verbs.json` unchanged unless standalone paradigms were added
