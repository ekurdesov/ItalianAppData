const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const LESSONS_DIR = path.join(ROOT, "lessons");
const OUTPUT = path.join(ROOT, "library.json");
const GENERATED_AT = "2026-05-15";

const ARTICLE_PREFIXES = [
  "il ",
  "lo ",
  "la ",
  "l'",
  "i ",
  "gli ",
  "le ",
  "un ",
  "uno ",
  "una ",
  "un'"
];

const ENTRY_SPLIT_RE = /\s*\/\s*/;
const SIMPLE_WORD_RE = /^[a-zàèéìíîòóùú][a-zàèéìíîòóùú'’-]*$/i;

function expandInflectionShorthand(value) {
  const match = value
    .trim()
    .match(/^([a-zàèéìíîòóùú'’-]+)\/([a-zàèéìíîòóùú'’-]+)([.?!])?$/i);
  if (!match) return null;

  const [, left, right] = match;
  if (right.length > 3 || left.length <= 1) return null;

  const base = left.slice(0, -1);
  return [left, `${base}${right}`];
}

function stripPrefix(term) {
  const lower = term.toLowerCase();
  for (const prefix of ARTICLE_PREFIXES) {
    if (lower.startsWith(prefix)) {
      return term.slice(prefix.length).trim();
    }
  }
  return term.trim();
}

function normalizeWord(term) {
  return term
    .trim()
    .replace(/[.,!?;:()[\]"]/g, "")
    .replace(/^«|»$/g, "")
    .trim();
}

function isSingleWord(term) {
  return SIMPLE_WORD_RE.test(term);
}

function parseVariants(it, en, ru) {
  const shorthand = expandInflectionShorthand(it);
  let itParts;
  if (shorthand) {
    itParts = shorthand;
  } else {
    const splitParts = it.split(ENTRY_SPLIT_RE).map((s) => s.trim()).filter(Boolean);
    const canSplitVariants =
      splitParts.length > 1 &&
      splitParts.every((part) => isSingleWord(normalizeWord(stripPrefix(part))));
    itParts = canSplitVariants ? splitParts : [it.trim()];
  }
  const enParts = en.split(ENTRY_SPLIT_RE).map((s) => s.trim()).filter(Boolean);
  const ruParts = ru.split(ENTRY_SPLIT_RE).map((s) => s.trim()).filter(Boolean);

  return itParts.map((part, index) => ({
    it: part,
    en: enParts.length === itParts.length ? enParts[index] : en,
    ru: ruParts.length === itParts.length ? ruParts[index] : ru
  }));
}

function ensureEntry(map, payload) {
  const key = payload.it.toLowerCase();
  if (!map.has(key)) {
    map.set(key, {
      it: payload.it,
      en: [],
      ru: [],
      types: [],
      forms: [],
      lessons: [],
      sources: []
    });
  }

  const entry = map.get(key);
  if (payload.en && !entry.en.includes(payload.en)) entry.en.push(payload.en);
  if (payload.ru && !entry.ru.includes(payload.ru)) entry.ru.push(payload.ru);
  if (payload.type && !entry.types.find((t) => t.en === payload.type.en && t.ru === payload.type.ru)) {
    entry.types.push(payload.type);
  }
  if (payload.form && !entry.forms.includes(payload.form)) entry.forms.push(payload.form);
  if (payload.lesson && !entry.lessons.includes(payload.lesson)) entry.lessons.push(payload.lesson);
  entry.sources.push(payload.source);
}

function addLexicalEntry(map, lessonId, file, kind, it, en, ru, type) {
  for (const variant of parseVariants(it, en, ru)) {
    const candidate = normalizeWord(stripPrefix(variant.it));
    if (!isSingleWord(candidate)) continue;
    ensureEntry(map, {
      it: candidate,
      en: variant.en,
      ru: variant.ru,
      type,
      form: variant.it,
      lesson: lessonId,
      source: {
        file,
        lesson_id: lessonId,
        kind,
        it: variant.it
      }
    });
  }
}

function addVerbTable(map, lessonId, file, table) {
  ensureEntry(map, {
    it: table.infinitive,
    en: table.translation.en,
    ru: table.translation.ru,
    type: { en: "verb infinitive", ru: "инфинитив" },
    form: table.infinitive,
    lesson: lessonId,
    source: {
      file,
      lesson_id: lessonId,
      kind: "verb_table_infinitive",
      it: table.infinitive
    }
  });

  for (const [person, form] of Object.entries(table.forms || {})) {
    const candidate = normalizeWord(form);
    if (!isSingleWord(candidate)) continue;
    ensureEntry(map, {
      it: candidate,
      en: table.translation.en,
      ru: table.translation.ru,
      type: {
        en: `verb form (${person})`,
        ru: `форма глагола (${person})`
      },
      form,
      lesson: lessonId,
      source: {
        file,
        lesson_id: lessonId,
        kind: "verb_form",
        person,
        infinitive: table.infinitive,
        it: form
      }
    });
  }
}

const entries = new Map();

for (const file of fs.readdirSync(LESSONS_DIR).sort()) {
  const fullPath = path.join(LESSONS_DIR, file);
  const lesson = JSON.parse(fs.readFileSync(fullPath, "utf8"));
  const lessonId = lesson.lesson_info.id;

  for (const flashcard of lesson.flashcards || []) {
    addLexicalEntry(
      entries,
      lessonId,
      file,
      "flashcard",
      flashcard.term,
      flashcard.en,
      flashcard.ru,
      flashcard.type
    );
  }

  for (const rule of lesson.language_rules || []) {
    for (const example of rule.examples || []) {
      addLexicalEntry(
        entries,
        lessonId,
        file,
        "language_rule_example",
        example.it,
        example.en,
        example.ru,
        {
          en: rule.category.en.toLowerCase(),
          ru: rule.category.ru.toLowerCase()
        }
      );
    }
  }

  for (const table of lesson.verb_tables || []) {
    addVerbTable(entries, lessonId, file, table);
  }
}

const output = {
  version: 1,
  generated_at: GENERATED_AT,
  source: "lessons/*.json",
  notes: "Reusable single-word Italian library derived from lesson flashcards, single-word rule examples, and verb tables. Multi-word phrases are intentionally excluded.",
  item_count: entries.size,
  items: [...entries.values()]
    .sort((a, b) => a.it.localeCompare(b.it, "it"))
    .map((entry) => ({
      it: entry.it,
      en: entry.en,
      ru: entry.ru,
      types: entry.types,
      forms: entry.forms.sort((a, b) => a.localeCompare(b, "it")),
      lessons: entry.lessons.sort(),
      sources: entry.sources
    }))
};

fs.writeFileSync(OUTPUT, JSON.stringify(output, null, 2) + "\n");
console.log(`Wrote ${OUTPUT} with ${output.item_count} items.`);
