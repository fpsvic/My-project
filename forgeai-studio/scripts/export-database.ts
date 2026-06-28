/**
 * Export shared/database.ts → backend/data/database_seed.py
 * Run: npm run db:export
 */
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  domainDefaults,
  domainTopics,
  earthKeywords,
  historyKeywords,
  mathKeywords,
  scienceKeywords,
  spaceKeywords,
} from "../shared/database";

const payload = {
  mathKeywords: [...mathKeywords],
  spaceKeywords: [...spaceKeywords],
  earthKeywords: [...earthKeywords],
  scienceKeywords: [...scienceKeywords],
  historyKeywords: [...historyKeywords],
  domainTopics: domainTopics.map((t) => ({
    ...t,
    match: { ...t.match },
  })),
  domainDefaults: Object.fromEntries(
    Object.entries(domainDefaults).map(([k, v]) => [k, { ...v, match: { ...v.match } }]),
  ),
};

const blob = JSON.stringify(JSON.stringify(payload));

const py = `"""Auto-generated from shared/database.ts — run: npm run db:export"""
from __future__ import annotations

import json

_DATA = json.loads(${blob})

MATH_KEYWORDS: list[str] = _DATA["mathKeywords"]
SPACE_KEYWORDS: list[str] = _DATA["spaceKeywords"]
EARTH_KEYWORDS: list[str] = _DATA["earthKeywords"]
SCIENCE_KEYWORDS: list[str] = _DATA["scienceKeywords"]
HISTORY_KEYWORDS: list[str] = _DATA["historyKeywords"]
DOMAIN_TOPICS: list[dict] = _DATA["domainTopics"]
DOMAIN_DEFAULTS: dict[str, dict] = _DATA["domainDefaults"]
`;

const out = resolve(__dirname, "../backend/data/database_seed.py");
writeFileSync(out, py, "utf-8");
console.log(`Wrote ${out}`);
