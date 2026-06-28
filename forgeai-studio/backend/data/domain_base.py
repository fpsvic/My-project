"""
Loader for domain topic data generated from shared/database.ts.

Source of truth: forgeai-studio/shared/database.ts
Regenerate Python seed: npm run db:export (from forgeai-studio/)
"""

from __future__ import annotations

from data.database_seed import (
    DOMAIN_DEFAULTS,
    DOMAIN_TOPICS,
    EARTH_KEYWORDS,
    HISTORY_KEYWORDS,
    MATH_KEYWORDS,
    SCIENCE_KEYWORDS,
    SPACE_KEYWORDS,
)

# Backward-compatible alias used by brain scoring for advanced science intent.
ADVANCED_SCIENCE_KEYWORDS: list[str] = SCIENCE_KEYWORDS
