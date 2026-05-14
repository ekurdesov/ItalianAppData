"""
Extract verb conjugation tables from IT PDFs and patch existing en/ + ru/ JSONs.
Also used as a library by the new-lesson processing script.

verb_tables schema added to each JSON:
[
  {
    "infinitive": "essere",
    "translation_en": "to be",
    "translation_ru": "быть",
    "forms": {
      "io": "sono",
      "tu": "sei",
      "lui/lei/Lei": "è",
      "noi": "siamo",
      "voi": "siete",
      "loro": "sono"
    }
  },
  ...
]
"""

import json, re, glob, os
import pdfplumber

# ── Known verb paradigms (ground truth for all A1 verbs) ──────────────────────
VERB_DATA = {
    "essere": {
        "translation_en": "to be",
        "translation_ru": "быть",
        "forms": {"io":"sono","tu":"sei","lui/lei/Lei":"è","noi":"siamo","voi":"siete","loro":"sono"}
    },
    "avere": {
        "translation_en": "to have",
        "translation_ru": "иметь",
        "forms": {"io":"ho","tu":"hai","lui/lei/Lei":"ha","noi":"abbiamo","voi":"avete","loro":"hanno"}
    },
    "chiamarsi": {
        "translation_en": "to be called",
        "translation_ru": "называться / зваться",
        "forms": {"io":"mi chiamo","tu":"ti chiami","lui/lei/Lei":"si chiama","noi":"ci chiamiamo","voi":"vi chiamate","loro":"si chiamano"}
    },
    "stare": {
        "translation_en": "to stay / to be (health)",
        "translation_ru": "находиться / чувствовать себя",
        "forms": {"io":"sto","tu":"stai","lui/lei/Lei":"sta","noi":"stiamo","voi":"state","loro":"stanno"}
    },
    "abitare": {
        "translation_en": "to live / to reside",
        "translation_ru": "жить / проживать",
        "forms": {"io":"abito","tu":"abiti","lui/lei/Lei":"abita","noi":"abitiamo","voi":"abitate","loro":"abitano"}
    },
    "parlare": {
        "translation_en": "to speak",
        "translation_ru": "говорить",
        "forms": {"io":"parlo","tu":"parli","lui/lei/Lei":"parla","noi":"parliamo","voi":"parlate","loro":"parlano"}
    },
    "lavorare": {
        "translation_en": "to work",
        "translation_ru": "работать",
        "forms": {"io":"lavoro","tu":"lavori","lui/lei/Lei":"lavora","noi":"lavoriamo","voi":"lavorate","loro":"lavorano"}
    },
    "studiare": {
        "translation_en": "to study",
        "translation_ru": "учиться / изучать",
        "forms": {"io":"studio","tu":"studi","lui/lei/Lei":"studia","noi":"studiamo","voi":"studiate","loro":"studiano"}
    },
    "scrivere": {
        "translation_en": "to write",
        "translation_ru": "писать",
        "forms": {"io":"scrivo","tu":"scrivi","lui/lei/Lei":"scrive","noi":"scriviamo","voi":"scrivete","loro":"scrivono"}
    },
    "leggere": {
        "translation_en": "to read",
        "translation_ru": "читать",
        "forms": {"io":"leggo","tu":"leggi","lui/lei/Lei":"legge","noi":"leggiamo","voi":"leggete","loro":"leggono"}
    },
    "prendere": {
        "translation_en": "to take",
        "translation_ru": "брать; садиться на транспорт",
        "forms": {"io":"prendo","tu":"prendi","lui/lei/Lei":"prende","noi":"prendiamo","voi":"prendete","loro":"prendono"}
    },
    "vivere": {
        "translation_en": "to live",
        "translation_ru": "жить",
        "forms": {"io":"vivo","tu":"vivi","lui/lei/Lei":"vive","noi":"viviamo","voi":"vivete","loro":"vivono"}
    },
    "vendere": {
        "translation_en": "to sell",
        "translation_ru": "продавать",
        "forms": {"io":"vendo","tu":"vendi","lui/lei/Lei":"vende","noi":"vendiamo","voi":"vendete","loro":"vendono"}
    },
    "mettere": {
        "translation_en": "to put",
        "translation_ru": "класть / ставить",
        "forms": {"io":"metto","tu":"metti","lui/lei/Lei":"mette","noi":"mettiamo","voi":"mettete","loro":"mettono"}
    },
    "chiedere": {
        "translation_en": "to ask",
        "translation_ru": "спрашивать",
        "forms": {"io":"chiedo","tu":"chiedi","lui/lei/Lei":"chiede","noi":"chiediamo","voi":"chiedete","loro":"chiedono"}
    },
    "rispondere": {
        "translation_en": "to answer",
        "translation_ru": "отвечать",
        "forms": {"io":"rispondo","tu":"rispondi","lui/lei/Lei":"risponde","noi":"rispondiamo","voi":"rispondete","loro":"rispondono"}
    },
    "partire": {
        "translation_en": "to leave / to depart",
        "translation_ru": "уезжать / отправляться",
        "forms": {"io":"parto","tu":"parti","lui/lei/Lei":"parte","noi":"partiamo","voi":"partite","loro":"partono"}
    },
    "sentire": {
        "translation_en": "to hear / to feel",
        "translation_ru": "слышать / чувствовать",
        "forms": {"io":"sento","tu":"senti","lui/lei/Lei":"sente","noi":"sentiamo","voi":"sentite","loro":"sentono"}
    },
    "dormire": {
        "translation_en": "to sleep",
        "translation_ru": "спать",
        "forms": {"io":"dormo","tu":"dormi","lui/lei/Lei":"dorme","noi":"dormiamo","voi":"dormite","loro":"dormono"}
    },
    "aprire": {
        "translation_en": "to open",
        "translation_ru": "открывать",
        "forms": {"io":"apro","tu":"apri","lui/lei/Lei":"apre","noi":"apriamo","voi":"aprite","loro":"aprono"}
    },
    "preferire": {
        "translation_en": "to prefer",
        "translation_ru": "предпочитать",
        "forms": {"io":"preferisco","tu":"preferisci","lui/lei/Lei":"preferisce","noi":"preferiamo","voi":"preferite","loro":"preferiscono"}
    },
    "capire": {
        "translation_en": "to understand",
        "translation_ru": "понимать",
        "forms": {"io":"capisco","tu":"capisci","lui/lei/Lei":"capisce","noi":"capiamo","voi":"capite","loro":"capiscono"}
    },
    "finire": {
        "translation_en": "to finish",
        "translation_ru": "заканчивать",
        "forms": {"io":"finisco","tu":"finisci","lui/lei/Lei":"finisce","noi":"finiamo","voi":"finite","loro":"finiscono"}
    },
    "andare": {
        "translation_en": "to go",
        "translation_ru": "идти / ехать",
        "forms": {"io":"vado","tu":"vai","lui/lei/Lei":"va","noi":"andiamo","voi":"andate","loro":"vanno"}
    },
    "fare": {
        "translation_en": "to do / to make",
        "translation_ru": "делать",
        "forms": {"io":"faccio","tu":"fai","lui/lei/Lei":"fa","noi":"facciamo","voi":"fate","loro":"fanno"}
    },
    "bere": {
        "translation_en": "to drink",
        "translation_ru": "пить",
        "forms": {"io":"bevo","tu":"bevi","lui/lei/Lei":"beve","noi":"beviamo","voi":"bevete","loro":"bevono"}
    },
    "venire": {
        "translation_en": "to come",
        "translation_ru": "приходить / приезжать",
        "forms": {"io":"vengo","tu":"vieni","lui/lei/Lei":"viene","noi":"veniamo","voi":"venite","loro":"vengono"}
    },
    "potere": {
        "translation_en": "to be able to / can",
        "translation_ru": "мочь",
        "forms": {"io":"posso","tu":"puoi","lui/lei/Lei":"può","noi":"possiamo","voi":"potete","loro":"possono"}
    },
    "volere": {
        "translation_en": "to want",
        "translation_ru": "хотеть",
        "forms": {"io":"voglio","tu":"vuoi","lui/lei/Lei":"vuole","noi":"vogliamo","voi":"volete","loro":"vogliono"}
    },
    "dovere": {
        "translation_en": "to have to / must",
        "translation_ru": "должен",
        "forms": {"io":"devo","tu":"devi","lui/lei/Lei":"deve","noi":"dobbiamo","voi":"dovete","loro":"devono"}
    },
    "sapere": {
        "translation_en": "to know",
        "translation_ru": "знать (уметь)",
        "forms": {"io":"so","tu":"sai","lui/lei/Lei":"sa","noi":"sappiamo","voi":"sapete","loro":"sanno"}
    },
    "mangiare": {
        "translation_en": "to eat",
        "translation_ru": "есть / кушать",
        "forms": {"io":"mangio","tu":"mangi","lui/lei/Lei":"mangia","noi":"mangiamo","voi":"mangiate","loro":"mangiano"}
    },
    "tornare": {
        "translation_en": "to return",
        "translation_ru": "возвращаться",
        "forms": {"io":"torno","tu":"torni","lui/lei/Lei":"torna","noi":"torniamo","voi":"tornate","loro":"tornano"}
    },
    "arrivare": {
        "translation_en": "to arrive",
        "translation_ru": "приезжать / прибывать",
        "forms": {"io":"arrivo","tu":"arrivi","lui/lei/Lei":"arriva","noi":"arriviamo","voi":"arrivate","loro":"arrivano"}
    },
    "usare": {
        "translation_en": "to use",
        "translation_ru": "использовать",
        "forms": {"io":"uso","tu":"usi","lui/lei/Lei":"usa","noi":"usiamo","voi":"usate","loro":"usano"}
    },
    "chiudere": {
        "translation_en": "to close",
        "translation_ru": "закрывать",
        "forms": {"io":"chiudo","tu":"chiudi","lui/lei/Lei":"chiude","noi":"chiudiamo","voi":"chiudete","loro":"chiudono"}
    },
    "correre": {
        "translation_en": "to run",
        "translation_ru": "бежать / бегать",
        "forms": {"io":"corro","tu":"corri","lui/lei/Lei":"corre","noi":"corriamo","voi":"correte","loro":"corrono"}
    },
    "perdere": {
        "translation_en": "to lose",
        "translation_ru": "терять",
        "forms": {"io":"perdo","tu":"perdi","lui/lei/Lei":"perde","noi":"perdiamo","voi":"perdete","loro":"perdono"}
    },
    "ricevere": {
        "translation_en": "to receive",
        "translation_ru": "получать",
        "forms": {"io":"ricevo","tu":"ricevi","lui/lei/Lei":"riceve","noi":"riceviamo","voi":"ricevete","loro":"ricevono"}
    },
    "vedere": {
        "translation_en": "to see",
        "translation_ru": "видеть",
        "forms": {"io":"vedo","tu":"vedi","lui/lei/Lei":"vede","noi":"vediamo","voi":"vedete","loro":"vedono"}
    },
    "piacere": {
        "translation_en": "to like / to please",
        "translation_ru": "нравиться",
        "forms": {"io":"piaccio","tu":"piaci","lui/lei/Lei":"piace","noi":"piacciamo","voi":"piacete","loro":"piacciono"}
    },
}

# ── Lesson → verbs mapping (derived from PDF content analysis) ────────────────
LESSON_VERBS = {
    "a1l1": ["essere","chiamarsi"],
    "a1l2": ["essere","chiamarsi","stare"],
    "a1l3": ["essere","chiamarsi"],
    "a1l4": ["essere","chiamarsi"],
    "a1l5": ["essere","avere"],
    "a1l6": ["essere","avere"],
    "a1l7": ["essere","avere"],
    "a2l1": ["essere","chiamarsi","parlare"],
    "a2l2": ["essere","chiamarsi","parlare"],
    "a2l3": ["essere","chiamarsi","stare"],
    "a2l4": ["essere","avere"],
    "a2l5": ["essere","avere","stare"],
    "a2l6": ["essere","avere","stare"],
    "a2l7": ["essere","avere"],
    "a3l1": ["essere","abitare"],
    "a3l2": ["essere","abitare"],
    "a3l3": ["essere","abitare","scrivere","leggere","prendere","partire","sentire","dormire","aprire","preferire"],
    "a3l4": ["essere","avere","abitare","parlare","studiare","lavorare"],
    "a3l5": ["essere","avere","abitare","parlare","studiare","lavorare"],
    # new lessons
    "a3l6": ["essere","avere","abitare","parlare","studiare","lavorare"],
    "a3l7": ["essere","avere","abitare","parlare","studiare","lavorare","stare"],
    "a3l8": ["essere","avere","stare"],
    "a3l9": ["essere","avere","stare","parlare"],
    "a4l1": ["essere","avere","andare","fare","prendere","lavorare"],
    "a4l2": ["essere","avere","andare","fare","bere","prendere"],
    "a4l3": ["essere","avere","andare","fare","bere","prendere","venire"],
    "a4l4": ["essere","avere","andare","fare","bere","venire","potere","volere"],
}


def make_verb_table(infinitive):
    """Return a verb_tables entry dict for the given infinitive."""
    d = VERB_DATA[infinitive]
    return {
        "infinitive": infinitive,
        "translation_en": d["translation_en"],
        "translation_ru": d["translation_ru"],
        "forms": d["forms"]
    }


def verb_tables_for_lesson(lesson_key):
    """Return the verb_tables list for a lesson key like 'a3l3'."""
    verbs = LESSON_VERBS.get(lesson_key, [])
    return [make_verb_table(v) for v in verbs if v in VERB_DATA]


def patch_json_file(path, lesson_key):
    """Add/replace verb_tables in a JSON file. Returns True if changed."""
    with open(path) as f:
        data = json.load(f)
    tables = verb_tables_for_lesson(lesson_key)
    if data.get("verb_tables") == tables:
        return False
    data["verb_tables"] = tables
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    changed = 0
    for locale in ("en", "ru"):
        for path in sorted(glob.glob(os.path.join(base, locale, "*.json"))):
            key = os.path.splitext(os.path.basename(path))[0]  # e.g. "a3l3"
            if key not in LESSON_VERBS:
                print(f"  SKIP {path} (no mapping)")
                continue
            if patch_json_file(path, key):
                print(f"  PATCHED {path}")
                changed += 1
            else:
                print(f"  OK     {path}")
    print(f"\nDone. {changed} files updated.")
