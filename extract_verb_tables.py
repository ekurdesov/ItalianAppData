"""
Rebuild `verb_tables` in the merged `lessons/*.json` files.

The mapping below is based on a fresh PDF scan of `IT/*.pdf` on 2026-05-15.
Priority is given to verb-drill slides and pages explicitly labeled `VERBI` or
`verbo`, plus a small number of high-signal lesson verbs visible in the lesson
texts (for example `amare` in L3-4).
"""

from __future__ import annotations

import json
import os
from collections import OrderedDict


VERB_DATA = {
    "abitare": {
        "en": "to live / to reside",
        "ru": "жить / проживать",
        "forms": {"io": "abito", "tu": "abiti", "lui/lei/Lei": "abita", "noi": "abitiamo", "voi": "abitate", "loro": "abitano"},
    },
    "amare": {
        "en": "to love",
        "ru": "любить",
        "forms": {"io": "amo", "tu": "ami", "lui/lei/Lei": "ama", "noi": "amiamo", "voi": "amate", "loro": "amano"},
    },
    "andare": {
        "en": "to go",
        "ru": "идти / ехать",
        "forms": {"io": "vado", "tu": "vai", "lui/lei/Lei": "va", "noi": "andiamo", "voi": "andate", "loro": "vanno"},
    },
    "aprire": {
        "en": "to open",
        "ru": "открывать",
        "forms": {"io": "apro", "tu": "apri", "lui/lei/Lei": "apre", "noi": "apriamo", "voi": "aprite", "loro": "aprono"},
    },
    "arrivare": {
        "en": "to arrive",
        "ru": "приходить / приезжать",
        "forms": {"io": "arrivo", "tu": "arrivi", "lui/lei/Lei": "arriva", "noi": "arriviamo", "voi": "arrivate", "loro": "arrivano"},
    },
    "avere": {
        "en": "to have",
        "ru": "иметь",
        "forms": {"io": "ho", "tu": "hai", "lui/lei/Lei": "ha", "noi": "abbiamo", "voi": "avete", "loro": "hanno"},
    },
    "bere": {
        "en": "to drink",
        "ru": "пить",
        "forms": {"io": "bevo", "tu": "bevi", "lui/lei/Lei": "beve", "noi": "beviamo", "voi": "bevete", "loro": "bevono"},
    },
    "cambiare": {
        "en": "to change",
        "ru": "менять / изменять",
        "forms": {"io": "cambio", "tu": "cambi", "lui/lei/Lei": "cambia", "noi": "cambiamo", "voi": "cambiate", "loro": "cambiano"},
    },
    "capire": {
        "en": "to understand",
        "ru": "понимать",
        "forms": {"io": "capisco", "tu": "capisci", "lui/lei/Lei": "capisce", "noi": "capiamo", "voi": "capite", "loro": "capiscono"},
    },
    "chiamarsi": {
        "en": "to be called",
        "ru": "называться / зваться",
        "forms": {"io": "mi chiamo", "tu": "ti chiami", "lui/lei/Lei": "si chiama", "noi": "ci chiamiamo", "voi": "vi chiamate", "loro": "si chiamano"},
    },
    "chiedere": {
        "en": "to ask",
        "ru": "спрашивать",
        "forms": {"io": "chiedo", "tu": "chiedi", "lui/lei/Lei": "chiede", "noi": "chiediamo", "voi": "chiedete", "loro": "chiedono"},
    },
    "chiudere": {
        "en": "to close",
        "ru": "закрывать",
        "forms": {"io": "chiudo", "tu": "chiudi", "lui/lei/Lei": "chiude", "noi": "chiudiamo", "voi": "chiudete", "loro": "chiudono"},
    },
    "comprare": {
        "en": "to buy",
        "ru": "покупать",
        "forms": {"io": "compro", "tu": "compri", "lui/lei/Lei": "compra", "noi": "compriamo", "voi": "comprate", "loro": "comprano"},
    },
    "correre": {
        "en": "to run",
        "ru": "бежать / бегать",
        "forms": {"io": "corro", "tu": "corri", "lui/lei/Lei": "corre", "noi": "corriamo", "voi": "correte", "loro": "corrono"},
    },
    "credere": {
        "en": "to believe",
        "ru": "верить / считать",
        "forms": {"io": "credo", "tu": "credi", "lui/lei/Lei": "crede", "noi": "crediamo", "voi": "credete", "loro": "credono"},
    },
    "dormire": {
        "en": "to sleep",
        "ru": "спать",
        "forms": {"io": "dormo", "tu": "dormi", "lui/lei/Lei": "dorme", "noi": "dormiamo", "voi": "dormite", "loro": "dormono"},
    },
    "essere": {
        "en": "to be",
        "ru": "быть",
        "forms": {"io": "sono", "tu": "sei", "lui/lei/Lei": "è", "noi": "siamo", "voi": "siete", "loro": "sono"},
    },
    "fare": {
        "en": "to do / to make",
        "ru": "делать / совершать",
        "forms": {"io": "faccio", "tu": "fai", "lui/lei/Lei": "fa", "noi": "facciamo", "voi": "fate", "loro": "fanno"},
    },
    "finire": {
        "en": "to finish",
        "ru": "заканчивать",
        "forms": {"io": "finisco", "tu": "finisci", "lui/lei/Lei": "finisce", "noi": "finiamo", "voi": "finite", "loro": "finiscono"},
    },
    "guardare": {
        "en": "to look / to watch",
        "ru": "смотреть",
        "forms": {"io": "guardo", "tu": "guardi", "lui/lei/Lei": "guarda", "noi": "guardiamo", "voi": "guardate", "loro": "guardano"},
    },
    "guidare": {
        "en": "to drive",
        "ru": "водить машину",
        "forms": {"io": "guido", "tu": "guidi", "lui/lei/Lei": "guida", "noi": "guidiamo", "voi": "guidate", "loro": "guidano"},
    },
    "imparare": {
        "en": "to learn",
        "ru": "учить / осваивать",
        "forms": {"io": "imparo", "tu": "impari", "lui/lei/Lei": "impara", "noi": "impariamo", "voi": "imparate", "loro": "imparano"},
    },
    "indicare": {
        "en": "to indicate / to show",
        "ru": "указывать / показывать",
        "forms": {"io": "indico", "tu": "indichi", "lui/lei/Lei": "indica", "noi": "indichiamo", "voi": "indicate", "loro": "indicano"},
    },
    "lavorare": {
        "en": "to work",
        "ru": "работать",
        "forms": {"io": "lavoro", "tu": "lavori", "lui/lei/Lei": "lavora", "noi": "lavoriamo", "voi": "lavorate", "loro": "lavorano"},
    },
    "leggere": {
        "en": "to read",
        "ru": "читать",
        "forms": {"io": "leggo", "tu": "leggi", "lui/lei/Lei": "legge", "noi": "leggiamo", "voi": "leggete", "loro": "leggono"},
    },
    "litigare": {
        "en": "to argue / to quarrel",
        "ru": "ссориться",
        "forms": {"io": "litigo", "tu": "litighi", "lui/lei/Lei": "litiga", "noi": "litighiamo", "voi": "litigate", "loro": "litigano"},
    },
    "mangiare": {
        "en": "to eat",
        "ru": "есть / кушать",
        "forms": {"io": "mangio", "tu": "mangi", "lui/lei/Lei": "mangia", "noi": "mangiamo", "voi": "mangiate", "loro": "mangiano"},
    },
    "mettere": {
        "en": "to put",
        "ru": "класть / ставить",
        "forms": {"io": "metto", "tu": "metti", "lui/lei/Lei": "mette", "noi": "mettiamo", "voi": "mettete", "loro": "mettono"},
    },
    "parlare": {
        "en": "to speak",
        "ru": "говорить",
        "forms": {"io": "parlo", "tu": "parli", "lui/lei/Lei": "parla", "noi": "parliamo", "voi": "parlate", "loro": "parlano"},
    },
    "partire": {
        "en": "to leave / to depart",
        "ru": "уезжать / отправляться",
        "forms": {"io": "parto", "tu": "parti", "lui/lei/Lei": "parte", "noi": "partiamo", "voi": "partite", "loro": "partono"},
    },
    "passare": {
        "en": "to spend / to pass",
        "ru": "проводить / проходить",
        "forms": {"io": "passo", "tu": "passi", "lui/lei/Lei": "passa", "noi": "passiamo", "voi": "passate", "loro": "passano"},
    },
    "perdere": {
        "en": "to lose",
        "ru": "терять",
        "forms": {"io": "perdo", "tu": "perdi", "lui/lei/Lei": "perde", "noi": "perdiamo", "voi": "perdete", "loro": "perdono"},
    },
    "piacere": {
        "en": "to like / to please",
        "ru": "нравиться",
        "forms": {"io": "piaccio", "tu": "piaci", "lui/lei/Lei": "piace", "noi": "piacciamo", "voi": "piacete", "loro": "piacciono"},
    },
    "portare": {
        "en": "to bring / to carry",
        "ru": "приносить / носить",
        "forms": {"io": "porto", "tu": "porti", "lui/lei/Lei": "porta", "noi": "portiamo", "voi": "portate", "loro": "portano"},
    },
    "potere": {
        "en": "to be able to / can",
        "ru": "мочь",
        "forms": {"io": "posso", "tu": "puoi", "lui/lei/Lei": "può", "noi": "possiamo", "voi": "potete", "loro": "possono"},
    },
    "preferire": {
        "en": "to prefer",
        "ru": "предпочитать",
        "forms": {"io": "preferisco", "tu": "preferisci", "lui/lei/Lei": "preferisce", "noi": "preferiamo", "voi": "preferite", "loro": "preferiscono"},
    },
    "prendere": {
        "en": "to take",
        "ru": "брать / заказывать / садиться на транспорт",
        "forms": {"io": "prendo", "tu": "prendi", "lui/lei/Lei": "prende", "noi": "prendiamo", "voi": "prendete", "loro": "prendono"},
    },
    "preparare": {
        "en": "to prepare",
        "ru": "готовить / подготавливать",
        "forms": {"io": "preparo", "tu": "prepari", "lui/lei/Lei": "prepara", "noi": "prepariamo", "voi": "preparate", "loro": "preparano"},
    },
    "presentare": {
        "en": "to introduce / to present",
        "ru": "представлять",
        "forms": {"io": "presento", "tu": "presenti", "lui/lei/Lei": "presenta", "noi": "presentiamo", "voi": "presentate", "loro": "presentano"},
    },
    "pulire": {
        "en": "to clean",
        "ru": "чистить / убирать",
        "forms": {"io": "pulisco", "tu": "pulisci", "lui/lei/Lei": "pulisce", "noi": "puliamo", "voi": "pulite", "loro": "puliscono"},
    },
    "regalare": {
        "en": "to give as a gift",
        "ru": "дарить",
        "forms": {"io": "regalo", "tu": "regali", "lui/lei/Lei": "regala", "noi": "regaliamo", "voi": "regalate", "loro": "regalano"},
    },
    "restare": {
        "en": "to stay / to remain",
        "ru": "оставаться",
        "forms": {"io": "resto", "tu": "resti", "lui/lei/Lei": "resta", "noi": "restiamo", "voi": "restate", "loro": "restano"},
    },
    "ricevere": {
        "en": "to receive",
        "ru": "получать",
        "forms": {"io": "ricevo", "tu": "ricevi", "lui/lei/Lei": "riceve", "noi": "riceviamo", "voi": "ricevete", "loro": "ricevono"},
    },
    "rispondere": {
        "en": "to answer",
        "ru": "отвечать",
        "forms": {"io": "rispondo", "tu": "rispondi", "lui/lei/Lei": "risponde", "noi": "rispondiamo", "voi": "rispondete", "loro": "rispondono"},
    },
    "salutare": {
        "en": "to greet / to say hello to",
        "ru": "приветствовать / здороваться с",
        "forms": {"io": "saluto", "tu": "saluti", "lui/lei/Lei": "saluta", "noi": "salutiamo", "voi": "salutate", "loro": "salutano"},
    },
    "sapere": {
        "en": "to know",
        "ru": "знать / уметь",
        "forms": {"io": "so", "tu": "sai", "lui/lei/Lei": "sa", "noi": "sappiamo", "voi": "sapete", "loro": "sanno"},
    },
    "scrivere": {
        "en": "to write",
        "ru": "писать",
        "forms": {"io": "scrivo", "tu": "scrivi", "lui/lei/Lei": "scrive", "noi": "scriviamo", "voi": "scrivete", "loro": "scrivono"},
    },
    "sentire": {
        "en": "to hear / to feel",
        "ru": "слышать / чувствовать",
        "forms": {"io": "sento", "tu": "senti", "lui/lei/Lei": "sente", "noi": "sentiamo", "voi": "sentite", "loro": "sentono"},
    },
    "stare": {
        "en": "to stay / to be (health)",
        "ru": "находиться / чувствовать себя",
        "forms": {"io": "sto", "tu": "stai", "lui/lei/Lei": "sta", "noi": "stiamo", "voi": "state", "loro": "stanno"},
    },
    "stirare": {
        "en": "to iron",
        "ru": "гладить",
        "forms": {"io": "stiro", "tu": "stiri", "lui/lei/Lei": "stira", "noi": "stiriamo", "voi": "stirate", "loro": "stirano"},
    },
    "studiare": {
        "en": "to study",
        "ru": "учиться / изучать",
        "forms": {"io": "studio", "tu": "studi", "lui/lei/Lei": "studia", "noi": "studiamo", "voi": "studiate", "loro": "studiano"},
    },
    "tornare": {
        "en": "to return",
        "ru": "возвращаться",
        "forms": {"io": "torno", "tu": "torni", "lui/lei/Lei": "torna", "noi": "torniamo", "voi": "tornate", "loro": "tornano"},
    },
    "usare": {
        "en": "to use",
        "ru": "использовать",
        "forms": {"io": "uso", "tu": "usi", "lui/lei/Lei": "usa", "noi": "usiamo", "voi": "usate", "loro": "usano"},
    },
    "vendere": {
        "en": "to sell",
        "ru": "продавать",
        "forms": {"io": "vendo", "tu": "vendi", "lui/lei/Lei": "vende", "noi": "vendiamo", "voi": "vendete", "loro": "vendono"},
    },
    "venire": {
        "en": "to come",
        "ru": "приходить / приезжать",
        "forms": {"io": "vengo", "tu": "vieni", "lui/lei/Lei": "viene", "noi": "veniamo", "voi": "venite", "loro": "vengono"},
    },
    "viaggiare": {
        "en": "to travel",
        "ru": "путешествовать",
        "forms": {"io": "viaggio", "tu": "viaggi", "lui/lei/Lei": "viaggia", "noi": "viaggiamo", "voi": "viaggiate", "loro": "viaggiano"},
    },
    "vivere": {
        "en": "to live",
        "ru": "жить",
        "forms": {"io": "vivo", "tu": "vivi", "lui/lei/Lei": "vive", "noi": "viviamo", "voi": "vivete", "loro": "vivono"},
    },
    "volere": {
        "en": "to want",
        "ru": "хотеть",
        "forms": {"io": "voglio", "tu": "vuoi", "lui/lei/Lei": "vuole", "noi": "vogliamo", "voi": "volete", "loro": "vogliono"},
    },
}


LESSON_VERBS = OrderedDict(
    [
        ("a1l1", ["essere", "chiamarsi"]),
        ("a1l2", ["essere", "chiamarsi", "stare"]),
        ("a1l3", ["essere", "chiamarsi"]),
        ("a1l4", ["essere", "chiamarsi"]),
        ("a1l5", ["essere", "avere", "chiamarsi"]),
        ("a1l6", ["essere", "avere", "chiamarsi"]),
        ("a1l7", ["essere", "avere"]),
        ("a2l1", ["essere", "chiamarsi", "parlare"]),
        ("a2l2", ["essere", "chiamarsi", "parlare"]),
        ("a2l3", ["essere", "chiamarsi", "stare"]),
        ("a2l4", ["essere", "avere", "stare"]),
        ("a2l5", ["essere", "avere", "stare"]),
        ("a2l6", ["essere", "avere", "stare"]),
        ("a2l7", ["essere", "avere", "stare"]),
        ("a3l1", ["essere", "avere", "abitare", "chiamarsi", "studiare"]),
        ("a3l2", ["essere", "avere", "abitare"]),
        (
            "a3l3",
            [
                "essere",
                "abitare",
                "chiamarsi",
                "scrivere",
                "leggere",
                "prendere",
                "partire",
                "sentire",
                "dormire",
                "aprire",
                "preferire",
                "vivere",
                "vendere",
                "mettere",
                "chiedere",
                "perdere",
                "ricevere",
                "arrivare",
                "comprare",
                "indicare",
                "portare",
                "preparare",
                "presentare",
                "regalare",
                "stirare",
                "cambiare",
                "guardare",
                "guidare",
                "imparare",
                "lavorare",
                "passare",
                "chiudere",
                "correre",
                "rispondere",
            ],
        ),
        ("a3l4", ["essere", "avere", "abitare", "parlare", "studiare", "lavorare", "chiamarsi", "amare"]),
        ("a3l5", ["essere", "avere", "abitare", "parlare", "studiare", "lavorare"]),
        ("a3l6", ["essere", "avere", "abitare", "parlare", "studiare", "lavorare"]),
        ("a3l7", ["essere", "avere", "abitare", "parlare", "studiare", "lavorare", "stare"]),
        ("a3l8", ["essere", "avere", "stare", "chiamarsi", "abitare", "andare"]),
        ("a3l9", ["essere", "avere", "stare", "parlare", "chiamarsi", "abitare", "andare"]),
        (
            "a4l1",
            [
                "essere",
                "avere",
                "andare",
                "fare",
                "prendere",
                "lavorare",
                "arrivare",
                "chiudere",
                "tornare",
                "usare",
                "guardare",
                "litigare",
                "mangiare",
                "ricevere",
                "salutare",
                "bere",
                "chiedere",
                "credere",
                "mettere",
                "comprare",
            ],
        ),
        ("a4l2", ["essere", "avere", "andare", "fare", "bere", "prendere"]),
        (
            "a4l3",
            [
                "essere",
                "avere",
                "andare",
                "fare",
                "bere",
                "prendere",
                "venire",
                "preferire",
                "capire",
                "finire",
                "mangiare",
                "pulire",
                "restare",
                "viaggiare",
            ],
        ),
        ("a4l4", ["essere", "avere", "andare", "fare", "bere", "venire", "potere", "volere", "preferire", "capire"]),
    ]
)


PRONOUN_LABELS = {
    "io": {"en": "I", "ru": "я"},
    "tu": {"en": "you (sg.)", "ru": "ты"},
    "lui/lei/Lei": {"en": "he/she/you (formal)", "ru": "он/она/Вы"},
    "noi": {"en": "we", "ru": "мы"},
    "voi": {"en": "you (pl.)", "ru": "вы"},
    "loro": {"en": "they", "ru": "они"},
}


def make_verb_table(infinitive: str) -> dict:
    data = VERB_DATA[infinitive]
    return {
        "infinitive": infinitive,
        "translation": {"en": data["en"], "ru": data["ru"]},
        "forms": data["forms"],
        "pronoun_labels": PRONOUN_LABELS,
    }


def patch_lesson(lesson_path: str) -> int:
    lesson_key = os.path.splitext(os.path.basename(lesson_path))[0]
    desired = [make_verb_table(v) for v in LESSON_VERBS.get(lesson_key, [])]

    with open(lesson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    if data.get("verb_tables") != desired:
        data["verb_tables"] = desired
        changed = 1

    with open(lesson_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return changed


def patch_index(index_path: str) -> int:
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    changed = 0
    for lesson in index.get("lessons", []):
        lesson_path = os.path.join("lessons", lesson["file"])
        with open(lesson_path, "r", encoding="utf-8") as f:
            lesson_json = json.load(f)
        count = len(lesson_json.get("verb_tables", []))
        if lesson.get("verb_table_count") != count:
            lesson["verb_table_count"] = count
            changed = 1

    if index.get("generated_at") != "2026-05-15":
        index["generated_at"] = "2026-05-15"
        changed = 1

    if changed:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return changed


def main() -> None:
    changed_lessons = 0
    for lesson_key in LESSON_VERBS:
        path = os.path.join("lessons", f"{lesson_key}.json")
        if os.path.exists(path):
            changed_lessons += patch_lesson(path)
    changed_index = patch_index("index.json")
    print(f"Updated {changed_lessons} lesson files.")
    print(f"Index changed: {bool(changed_index)}")


if __name__ == "__main__":
    main()
