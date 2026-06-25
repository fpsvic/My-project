"""
ForgeAI Brain — dynamic response generation engine.

Instead of returning pre-written strings, every answer is WRITTEN fresh from
fact atoms using a personality + sentence-pattern system. The same question
asked twice will get a different answer in structure, tone, emphasis and length.
"""

import random
import re


# ── Personalities ─────────────────────────────────────────────────────────────

_PERSONALITIES = {
    "explorer": {
        "openers": [
            "Oh, this is interesting — ",
            "You know, I find this genuinely fascinating.",
            "Great question. So —",
            "I actually love this topic.",
            "Okay, there's a lot to unpack here.",
            "There's something really cool about this.",
        ],
        "connectors": [
            "What's also interesting is that ",
            "Here's the part that gets really wild: ",
            "And here's something most people don't realize — ",
            "Oh, and this is worth knowing: ",
            "The rabbit hole goes deeper: ",
            "Another layer to this: ",
        ],
        "reactions": [
            "Kind of blows your mind a little.",
            "Nature figured this out before we did.",
            "The universe really doesn't mess around.",
            "That connection is so elegant when you think about it.",
            "I never get tired of this stuff.",
        ],
        "closers": [
            "Want me to go deeper on any part of that?",
            "There's honestly so much more here if you want it.",
            "I could talk about this all day.",
            "Let me know if you want to chase this further.",
        ],
    },
    "professor": {
        "openers": [
            "Let me give you the complete picture.",
            "Right, so — the accurate answer here is:",
            "Good question. Here's what the evidence actually says.",
            "To be precise about this:",
            "Let's break this down properly.",
            "The key facts here are:",
        ],
        "connectors": [
            "Furthermore, ",
            "It's also worth noting that ",
            "An important detail: ",
            "To add precision here: ",
            "The underlying reason is that ",
            "This connects to the fact that ",
        ],
        "reactions": [
            "The numbers really do speak for themselves.",
            "This is well-established science.",
            "Precision matters here — the difference is significant.",
            "This is often misunderstood, so it's worth being exact.",
        ],
        "closers": [
            "Happy to go into more technical depth on any of that.",
            "Let me know if you want sources or further detail.",
            "I can elaborate on any specific aspect.",
        ],
    },
    "casual": {
        "openers": [
            "Okay so basically —",
            "Yeah, so here's the deal:",
            "Oh yeah, good one. So,",
            "Alright,",
            "Short version first: ",
            "So the thing is,",
            "Yeah this is actually really cool.",
        ],
        "connectors": [
            "Also, ",
            "Oh and —",
            "Worth mentioning: ",
            "On top of that, ",
            "And get this — ",
            "Btw, ",
        ],
        "reactions": [
            "Pretty wild ngl.",
            "Kind of crazy honestly.",
            "Not what most people expect.",
            "Yeah it's wild.",
            "Low-key mind-blowing.",
        ],
        "closers": [
            "Lmk if you want more on this.",
            "Got more questions? Go for it.",
            "Anything else you're curious about?",
            "",
            "",
        ],
    },
    "direct": {
        "openers": [
            "Here's what you need to know:",
            "Straight answer:",
            "Right —",
            "",
            "",
            "Bottom line:",
        ],
        "connectors": [
            "Also: ",
            "Key point: ",
            "Detail worth knowing: ",
            "Add to that: ",
        ],
        "reactions": [
            "Worth knowing.",
            "That's the key number.",
            "Significant.",
            "",
            "",
        ],
        "closers": [
            "Need more detail?",
            "Want me to expand on that?",
            "",
            "",
        ],
    },
}

_PERSONALITY_KEYS = list(_PERSONALITIES.keys())


def _pick() -> dict:
    return _PERSONALITIES[random.choice(_PERSONALITY_KEYS)]


# ── Sentence rewriters ────────────────────────────────────────────────────────
# These take a plain fact string and rephrase it using one of several patterns.

_REPHRASE_PATTERNS = [
    # pattern 0 — direct statement (no change)
    lambda s: s,
    # pattern 1 — "The answer is X" → "X — that's the answer."
    lambda s: s,
    # pattern 2 — leading emphasis on first bold token
    lambda s: _lead_with_bold(s),
    # pattern 3 — split at first comma and swap
    lambda s: _swap_clauses(s),
    # pattern 4 — prefix with "So, "
    lambda s: "So, " + s[0].lower() + s[1:] if s else s,
    # pattern 5 — suffix with "— that's the short answer."
    lambda s: s.rstrip(".") + " — that's the short answer.",
]


def _lead_with_bold(s: str) -> str:
    """Pull the first bold item to the front: 'X is **Y**' → '**Y** — that's X.'"""
    m = re.search(r"\*\*([^*]+)\*\*", s)
    if not m:
        return s
    value = m.group(1)
    rest = re.sub(r"\*\*[^*]+\*\*", "", s, count=1).strip().strip("—").strip()
    if rest:
        return f"**{value}** — {rest[0].lower()}{rest[1:]}"
    return s


def _swap_clauses(s: str) -> str:
    """'A, B' → 'B — A'"""
    if ", " not in s[:80]:
        return s
    parts = s.split(", ", 1)
    if len(parts) == 2:
        return parts[1].strip() + " — " + parts[0][0].lower() + parts[0][1:]
    return s


def _rephrase(fact: str) -> str:
    fn = random.choice(_REPHRASE_PATTERNS)
    try:
        result = fn(fact)
        return result if result and len(result) > 3 else fact
    except Exception:
        return fact


# ── Length variation ──────────────────────────────────────────────────────────

def _vary_depth(content: str) -> str:
    """Sometimes trim a long response to its first 2 sections; sometimes keep full."""
    if random.random() < 0.25:
        # short mode: first paragraph / section only
        parts = re.split(r"\n\n+", content, maxsplit=2)
        return parts[0].strip() if parts else content
    return content


# ── Main entry point ─────────────────────────────────────────────────────────

def forge(content: str, query: str, intent: str = "knowledge") -> str:
    """
    Take any content string and return a personality-wrapped, varied version.
    For 'build'/'game'/'math' intents the content is returned mostly unchanged
    (code blocks should not be wrapped in casual banter).
    """
    # Don't touch code-heavy or build responses
    if intent in ("build_game", "build_app", "build_any", "math", "programming"):
        return content
    # Don't touch responses that are mostly code blocks
    if content.count("```") >= 2:
        return content

    p = _pick()

    opener = random.choice(p["openers"]).strip()
    reaction = random.choice(p["reactions"]).strip() if random.random() < 0.4 else ""
    closer = random.choice(p["closers"]).strip() if random.random() < 0.45 else ""

    # Vary content depth
    body = _vary_depth(content)

    # For short single-line facts, rephrase the sentence
    if "\n" not in body.strip() and len(body) < 200:
        body = _rephrase(body)

    parts = []
    if opener:
        # Don't put an opener before a markdown heading — looks weird
        if not body.lstrip().startswith("#"):
            parts.append(opener + "\n\n")

    parts.append(body)

    if reaction and not body.endswith(reaction):
        parts.append(f"\n\n*{reaction}*")

    if closer:
        parts.append(f"\n\n{closer}")

    return "".join(parts)


# ── Greeting generator ────────────────────────────────────────────────────────

_GREETING_INTROS = [
    "Hey! I'm **ForgeAI** — your local cognitive engine.",
    "What's up! I'm **ForgeAI**, running fully offline on your machine.",
    "Hi there! **ForgeAI** here.",
    "Hello! I'm **ForgeAI**, your local AI.",
    "Hey — **ForgeAI** at your service.",
    "What's good! I'm **ForgeAI**.",
]

_CAPABILITY_SETS = [
    [
        "- **Build games** — `make a snake game`, `build flappy bird`, `create a space shooter`",
        "- **Build apps** — `make a calculator`, `build a kanban board`, `create a budget tracker`",
        "- **Answer questions** — science, space, history, animals, math, programming",
        "- **Solve math** — derivatives, integrals, trig, algebra",
    ],
    [
        "- **Games** — any arcade game you can think of, built and playable instantly",
        "- **Apps & tools** — calculators, timers, trackers, converters, drawing tools",
        "- **Science & space** — from black holes to DNA to quantum mechanics",
        "- **Math** — calculus, trig, algebra, anything with numbers",
        "- **History & programming** — language origins, code examples, historical events",
    ],
    [
        "- Ask me to **build something** — games, apps, tools",
        "- Ask me **anything** — science, space, history, animals",
        "- Give me **a math problem** — I'll solve it step by step",
        "- Ask about **programming** — any language, any concept",
    ],
]

_GREETING_CLOSERS = [
    "What do you want to explore?",
    "What should we build or learn about?",
    "What are you thinking about today?",
    "Tell me what you want — I'll make it happen.",
    "What's on your mind?",
    "Ask me anything or tell me what to build.",
]

_SELF_DESCRIPTIONS = [
    "I run entirely offline — no internet needed, everything processed locally.",
    "I'm fully local — your data never leaves your machine.",
    "Everything I do runs on your device. No cloud, no tracking.",
    "I'm offline-first — fast, private, and always available.",
]


def forge_greeting(mode: str) -> str:
    """Generate a fresh, varied greeting every time."""
    intro = random.choice(_GREETING_INTROS)
    caps = random.choice(_CAPABILITY_SETS)
    closer = random.choice(_GREETING_CLOSERS)
    self_desc = random.choice(_SELF_DESCRIPTIONS) if random.random() < 0.5 else ""

    # Vary the structure
    if random.random() < 0.3:
        # Short version
        return f"{intro}\n\n**Here's what I can do:**\n" + "\n".join(caps[:3]) + f"\n\n{closer}"

    lines = [intro]
    if self_desc:
        lines.append(f"\n*{self_desc}*")
    lines.append(f"\n\n**What I can help with:**\n" + "\n".join(caps))
    lines.append(f"\n\n{closer}")
    return "".join(lines)
