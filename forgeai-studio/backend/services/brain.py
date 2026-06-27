"""
ForgeAI Brain — public interface for response generation.

vary_structure.py handles all structural rewriting.
This module provides forge() (re-exported) and forge_greeting().
"""

import random

# Re-export the structural engine as the public forge() entry point
from services.vary_structure import forge  # noqa: F401


# ── Greeting generator ────────────────────────────────────────────────────────

_GREETING_INTROS = [
    "I'm **ForgeAI** — your local AI.",
    "**ForgeAI** here.",
    "**ForgeAI** — running fully offline on your machine.",
    "Hey, **ForgeAI** is up.",
    "**ForgeAI** ready.",
    "Local AI, fully offline — **ForgeAI**.",
]

_CAPABILITY_SETS = [
    [
        "- **Build games** — `make a snake game`, `build flappy bird`, `create a space shooter`",
        "- **Build apps** — `make a calculator`, `build a kanban board`, `create a budget tracker`",
        "- **Answer questions** — science, space, history, animals, math, programming",
        "- **Solve math** — derivatives, integrals, trig, algebra",
    ],
    [
        "- **Games** — any arcade game, built and playable instantly",
        "- **Apps & tools** — calculators, timers, trackers, converters, drawing tools",
        "- **Science & space** — from black holes to DNA to quantum mechanics",
        "- **Math** — calculus, trig, algebra, step-by-step",
        "- **History & programming** — language origins, code examples, events",
    ],
    [
        "- **Build something** — games, apps, tools — just describe it",
        "- **Ask anything** — science, space, history, animals, people",
        "- **Math problems** — I solve them step by step",
        "- **Programming** — any language, any concept, with examples",
    ],
    [
        "- Games and apps — built live, playable in-browser",
        "- Science, space, animals, history — deep knowledge base",
        "- Math — calculus, trig, algebra, full working shown",
        "- Programming — history, syntax, examples across 20+ languages",
    ],
]

_CLOSERS = [
    "What do you want to build or learn about?",
    "What should we work on?",
    "Ask me anything or tell me what to build.",
    "What are you thinking?",
    "What's the question?",
    "Go ahead — what do you need?",
]

_SELF_DESC = [
    "No internet required — everything runs locally.",
    "Fully local. No cloud, no tracking.",
    "Everything processes on your device.",
    "Offline-first — always available, fully private.",
]

_SECTION_LABELS = [
    "**What I can do:**",
    "**Capabilities:**",
    "**Here's what I handle:**",
    "**What's available:**",
]


def forge_greeting(mode: str) -> str:
    intro = random.choice(_GREETING_INTROS)
    caps = random.choice(_CAPABILITY_SETS)
    closer = random.choice(_CLOSERS)
    label = random.choice(_SECTION_LABELS)

    lines = [intro]

    if random.random() < 0.45:
        lines.append(f"\n*{random.choice(_SELF_DESC)}*")

    lines.append(f"\n\n{label}\n" + "\n".join(caps))
    lines.append(f"\n\n{closer}")

    return "".join(lines)
