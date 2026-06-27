"""
Thin loader for knowledge data generated from shared/knowledgebase.ts and shared/database.ts.

Domain keywords source: shared/database.ts (npm run db:export)
Other KB data source: shared/knowledgebase.ts (npm run kb:export)
"""

from __future__ import annotations

from data.domain_base import (
    ADVANCED_SCIENCE_KEYWORDS,
    EARTH_KEYWORDS,
    SPACE_KEYWORDS,
)
from data.knowledge_seed import (
    CODING_HELP,
    GENERAL_KNOWLEDGE,
    HIGH_CONFIDENCE_KEYWORDS,
    LANG_EXAMPLES,
    LANG_HELLO_WORLD,
    LANG_HISTORY,
    POLITICAL_KEYWORDS,
    PROTECTED_ENGLISH_WORDS,
)
