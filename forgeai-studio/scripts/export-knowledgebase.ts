/**
 * Export shared/knowledgebase.ts → backend/data/knowledge_seed.py
 * Run: npm run kb:export
 */
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  advancedScienceKeywords,
  codingHelp,
  earthKeywords,
  generalKnowledge,
  highConfidenceKeywords,
  langExamples,
  langHelloWorld,
  langHistory,
  politicalKeywords,
  protectedEnglishWords,
  resolveAliases,
  spaceKeywords,
} from "../shared/knowledgebase";

const general = { ...generalKnowledge };
resolveAliases(general);

const payload = {
  spaceKeywords: [...spaceKeywords],
  earthKeywords: [...earthKeywords],
  advancedScienceKeywords: [...advancedScienceKeywords],
  politicalKeywords: [...politicalKeywords],
  protectedEnglishWords: [...protectedEnglishWords],
  highConfidenceKeywords: [...highConfidenceKeywords],
  langHistory: { ...langHistory },
  langHelloWorld: { ...langHelloWorld },
  langExamples: structuredClone(langExamples),
  generalKnowledge: general,
  codingHelp: { ...codingHelp },
};

const blob = JSON.stringify(JSON.stringify(payload));

const py = `"""Auto-generated from shared/knowledgebase.ts — run: npm run kb:export"""
from __future__ import annotations

import json

_DATA = json.loads(${blob})

SPACE_KEYWORDS: list[str] = _DATA["spaceKeywords"]
EARTH_KEYWORDS: list[str] = _DATA["earthKeywords"]
ADVANCED_SCIENCE_KEYWORDS: list[str] = _DATA["advancedScienceKeywords"]
POLITICAL_KEYWORDS: list[str] = _DATA["politicalKeywords"]
PROTECTED_ENGLISH_WORDS: list[str] = _DATA["protectedEnglishWords"]
HIGH_CONFIDENCE_KEYWORDS: list[str] = _DATA["highConfidenceKeywords"]
LANG_HISTORY: dict[str, str] = _DATA["langHistory"]
LANG_HELLO_WORLD: dict[str, str] = _DATA["langHelloWorld"]
LANG_EXAMPLES: dict[str, dict[str, str]] = _DATA["langExamples"]
GENERAL_KNOWLEDGE: dict[str, str] = _DATA["generalKnowledge"]
CODING_HELP: dict[str, str] = _DATA["codingHelp"]
`;

const out = resolve(__dirname, "../backend/data/knowledge_seed.py");
writeFileSync(out, py, "utf-8");
console.log(`Wrote ${out}`);
