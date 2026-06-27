"""
Thin Python loader for shared knowledgebase.json.

Source of truth: forgeai-studio/shared/knowledgebase.ts
Regenerate JSON: npm run kb:export (from forgeai-studio/)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_JSON_PATH = Path(__file__).resolve().parents[2] / "shared" / "knowledgebase.json"


def _load() -> dict[str, Any]:
    with open(_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


_data = _load()

SPACE_KEYWORDS: list[str] = _data["spaceKeywords"]
EARTH_KEYWORDS: list[str] = _data["earthKeywords"]
ADVANCED_SCIENCE_KEYWORDS: list[str] = _data["advancedScienceKeywords"]
POLITICAL_KEYWORDS: list[str] = _data["politicalKeywords"]
PROTECTED_ENGLISH_WORDS: list[str] = _data["protectedEnglishWords"]
HIGH_CONFIDENCE_KEYWORDS: list[str] = _data["highConfidenceKeywords"]

LANG_HISTORY: dict[str, str] = _data["langHistory"]
LANG_HELLO_WORLD: dict[str, str] = _data["langHelloWorld"]
LANG_EXAMPLES: dict[str, dict[str, str]] = _data["langExamples"]
GENERAL_KNOWLEDGE: dict[str, str] = _data["generalKnowledge"]
CODING_HELP: dict[str, str] = _data["codingHelp"]
