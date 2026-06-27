"""One-time migration helper: export legacy knowledge_base.py → knowledgebase.ts/json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from data import knowledge_base as kb  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "shared"


def ts_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def ts_dict(d: dict) -> str:
    lines = ["{"]
    for k, v in d.items():
        lines.append(f"  {ts_string(k)}: {ts_string(v)},")
    lines.append("}")
    return "\n".join(lines)


def ts_nested_dict(d: dict) -> str:
    if not d:
        return "{}"
    lines = ["{"]
    for lang, concepts in d.items():
        inner = ", ".join(f"{ts_string(c)}: {ts_string(code)}" for c, code in concepts.items())
        lines.append(f"  {ts_string(lang)}: {{ {inner} }},")
    lines.append("}")
    return "\n".join(lines)


def ts_array(arr: list) -> str:
    return "[" + ", ".join(ts_string(x) for x in arr) + "]"


def main() -> None:
    payload = {
        "spaceKeywords": kb.SPACE_KEYWORDS,
        "earthKeywords": kb.EARTH_KEYWORDS,
        "advancedScienceKeywords": kb.ADVANCED_SCIENCE_KEYWORDS,
        "politicalKeywords": kb.POLITICAL_KEYWORDS,
        "protectedEnglishWords": kb.PROTECTED_ENGLISH_WORDS,
        "highConfidenceKeywords": kb.HIGH_CONFIDENCE_KEYWORDS,
        "langHistory": kb.LANG_HISTORY,
        "langHelloWorld": kb.LANG_HELLO_WORLD,
        "langExamples": kb.LANG_EXAMPLES,
        "generalKnowledge": kb.GENERAL_KNOWLEDGE,
        "codingHelp": kb.CODING_HELP,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "knowledgebase.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    ts_path = OUT / "knowledgebase.ts"
    ts_content = f'''/**
 * ForgeAI knowledge base — single source of truth for static KB data.
 * Seeded into SQLite on backend startup; available to frontend imports.
 */

export type KnowledgeMap = Record<string, string>;
export type CodeExamplesMap = Record<string, Record<string, string>>;

export const spaceKeywords: readonly string[] = {ts_array(kb.SPACE_KEYWORDS)};
export const earthKeywords: readonly string[] = {ts_array(kb.EARTH_KEYWORDS)};
export const advancedScienceKeywords: readonly string[] = {ts_array(kb.ADVANCED_SCIENCE_KEYWORDS)};
export const politicalKeywords: readonly string[] = {ts_array(kb.POLITICAL_KEYWORDS)};
export const protectedEnglishWords: readonly string[] = {ts_array(kb.PROTECTED_ENGLISH_WORDS)};
export const highConfidenceKeywords: readonly string[] = {ts_array(kb.HIGH_CONFIDENCE_KEYWORDS)};

export const langHistory: KnowledgeMap = {ts_dict(kb.LANG_HISTORY)};

export const langHelloWorld: KnowledgeMap = {ts_dict(kb.LANG_HELLO_WORLD)};

export const langExamples: CodeExamplesMap = {ts_nested_dict(kb.LANG_EXAMPLES)};

export const generalKnowledge: KnowledgeMap = {ts_dict(kb.GENERAL_KNOWLEDGE)};

export const codingHelp: KnowledgeMap = {ts_dict(kb.CODING_HELP)};

/** Resolve alias entries where a value is itself another key. */
export function resolveAliases(map: KnowledgeMap): void {{
  let changed = true;
  while (changed) {{
    changed = false;
    for (const [key, value] of Object.entries(map)) {{
      if (typeof value === "string" && value in map) {{
        map[key] = map[value];
        changed = true;
      }}
    }}
  }}
}}

export const knowledgeBase = {{
  spaceKeywords,
  earthKeywords,
  advancedScienceKeywords,
  politicalKeywords,
  protectedEnglishWords,
  highConfidenceKeywords,
  langHistory,
  langHelloWorld,
  langExamples,
  generalKnowledge,
  codingHelp,
}} as const;

export default knowledgeBase;
'''
    with open(ts_path, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"Wrote {ts_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
