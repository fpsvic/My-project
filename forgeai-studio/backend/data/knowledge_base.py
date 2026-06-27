"""
Thin loader for knowledge data generated from shared/knowledgebase.ts.

Source of truth: forgeai-studio/shared/knowledgebase.ts
Regenerate Python seed: npm run kb:export (from forgeai-studio/)
"""

from __future__ import annotations

from data.knowledge_seed import (
    ADVANCED_SCIENCE_KEYWORDS,
    CODING_HELP,
    EARTH_KEYWORDS,
    GENERAL_KNOWLEDGE,
    HIGH_CONFIDENCE_KEYWORDS,
    LANG_EXAMPLES,
    LANG_HELLO_WORLD,
    LANG_HISTORY,
    POLITICAL_KEYWORDS,
    PROTECTED_ENGLISH_WORDS,
    SPACE_KEYWORDS,
)
