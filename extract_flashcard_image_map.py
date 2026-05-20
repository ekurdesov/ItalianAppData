#!/usr/bin/env python3
"""Extract all flashcard terms from lessons into an image map for Nano Banana generation."""

import json
from pathlib import Path

LESSONS_DIR = Path(__file__).parent / "lessons"
OUTPUT_FILE = Path(__file__).parent / "flashcard_image_map.json"


def main():
    # Load existing map to preserve file/generated state
    existing = {}
    if OUTPUT_FILE.exists():
        existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))

    image_map = {}

    for lesson_file in sorted(LESSONS_DIR.glob("*.json")):
        data = json.loads(lesson_file.read_text(encoding="utf-8"))
        for card in data.get("flashcards", []):
            term = card["term"]
            if term not in image_map:
                prev = existing.get(term, {})
                image_map[term] = {
                    "description": prev.get("description", card["en"]),
                    "file": prev.get("file", ""),
                    "generated": prev.get("generated", False),
                }

    sorted_map = dict(sorted(image_map.items()))

    OUTPUT_FILE.write_text(
        json.dumps(sorted_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(sorted_map)} terms to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
