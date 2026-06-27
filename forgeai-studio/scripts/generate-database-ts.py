#!/usr/bin/env python3
"""One-shot generator (legacy): was used to bootstrap shared/database.ts from engine .py files.

database.ts is now the source of truth. Edit shared/database.ts directly, then npm run db:export.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPACE_KW = [
    "sun", "earth", "moon", "mars", "space", "astronom", "galaxy", "universe", "distance", "miles",
    "gravity", "orbit", "planet", "speed of light", "cosmic", "sol", "luna", "star", "solar",
    "venus", "saturn", "jupiter", "neptune", "uranus", "mercury", "milky way", "black hole",
    "nebula", "supernova", "neutron star", "dark matter", "dark energy", "big bang", "light year",
    "parsec", "hubble", "telescope", "asteroid", "comet", "meteor", "atmosphere", "exoplanet", "wormhole",
]
EARTH_KW = [
    "rock", "mineral", "stone", "geolog", "petrolog", "basalt", "granite", "sediment", "metamorph",
    "igneous", "volcano", "lava", "magma", "magmatic", "caldera", "tectonic", "plate", "ring of fire",
    "subduction", "trench", "mariana", "ocean", "underwater", "hydrothermal", "vent", "black smoker",
    "seafloor", "crust", "mantle", "mohs", "earthquake", "seismic", "richter", "fossil", "erosion",
    "glacier", "ice age", "carbon dating",
]
SCIENCE_KW = [
    "quantum", "physics", "planck", "boltzmann", "chemistry", "element", "carbon", "noble", "electroneg",
    "dna", "gene", "cell", "transcription", "biology", "golden ratio", "phi", "euler", "irrational",
    "einstein", "relativity", "e=mc", "photon", "electron", "proton", "neutron", "atom", "molecule",
    "compound", "periodic", "mendeleev", "entropy", "thermodynamics", "maxwell", "faraday", "newton",
    "gravity constant", "avogadro", "mole", "bohr", "schrodinger", "heisenberg", "uncertainty",
]
POLITICAL_KW = [
    "washington", "president", "lincoln", "fdr", "new deal", "civil war", "party", "whig", "federalist",
    "constitution", "politic", "align", "congress", "senate", "amendment", "declaration", "jefferson",
    "adams", "hamilton", "madison", "jackson", "grant", "wilson", "eisenhower", "kennedy", "reagan",
    "clinton", "obama", "trump", "biden",
]
HISTORY_EXTRA = [
    "world war", "revolution", "declaration of independence", "founding fathers", "slavery",
    "abolition", "reconstruction", "great depression", "cold war", "vietnam", "roosevelt", "democrat",
    "republican", "colonial", "egypt", "pharaoh", "pyramid", "rome", "renaissance", "history",
    "ancient", "empire", "medieval", "century", "war", "battle", "dynasty", "civilization",
]
MATH_KW = [
    "derivative", "differentiate", "differentiation", "integral", "integrate", "integration",
    "antiderivative", "limit", "chain rule", "product rule", "quotient rule", "power rule",
    "polynomial", "calculus", "sin", "cos", "tan", "csc", "sec", "cot", "arcsin", "arccos", "arctan",
    "solve", "compute", "calculate", "evaluate", "simplify", "quadratic", "factorial", "fibonacci",
    "gcd", "lcm", "prime", "pythagorean", "hypotenuse", "mean", "median", "mode", "average",
    "variance", "standard deviation", "permutation", "combination", "convert", "geometry",
    "circle", "sphere", "cylinder", "cone", "triangle", "rectangle", "area", "volume", "perimeter",
]


def _ts_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _parse_match(cond: str) -> dict:
    cond = cond.strip()
    m = re.match(
        r'"(\w[\w ]*)" in q and any\(w in q for w in \(([^)]+)\)\)',
        cond,
    )
    if m:
        all_kw = [m.group(1)]
        any_kw = re.findall(r'"([^"]*)"', m.group(2))
        return {"all": all_kw, "any": any_kw}
    m = re.match(r'any\(w in q for w in \(([^)]+)\)\)', cond)
    if m:
        return {"any": re.findall(r'"([^"]*)"', m.group(1))}
    m = re.match(r'_kw\(q, ([^)]+)\)', cond)
    if m:
        return {"any": [w.strip().strip('"').strip("'") for w in m.group(1).split(",")]}
    m = re.match(r'"([^"]+)" in q or "([^"]+)" in q', cond)
    if m:
        return {"any": [m.group(1), m.group(2)]}
    m = re.match(r'"([^"]+)" in q', cond)
    if m:
        return {"any": [m.group(1)]}
    m = re.match(
        r'"(\w[\w ]*)" in q and any\(w in q for w in \(([^)]+)\)\)',
        cond,
    )
    raise ValueError(f"Unparsed condition: {cond!r}")


def _extract_string_expr(src: str, start: int) -> tuple[str, int]:
    """Extract a Python string literal or parenthesized concat starting at start."""
    i = start
    while i < len(src) and src[i] in " \t\n":
        i += 1
    if i >= len(src):
        raise ValueError("empty expr")
    if src[i] == "(":
        depth = 0
        begin = i
        while i < len(src):
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
                if depth == 0:
                    chunk = src[begin : i + 1]
                    parts = re.findall(r'"(?:[^"\\]|\\.)*"', chunk, re.DOTALL)
                    text = "".join(json.loads(p) for p in parts)
                    return text, i + 1
            i += 1
        raise ValueError("unclosed paren")
    m = re.match(r'"(?:[^"\\]|\\.)*"', src[i:], re.DOTALL)
    if not m:
        raise ValueError(f"no string at {i}: {src[i:i+40]!r}")
    return json.loads(m.group(0)), i + m.end()


def _extract_blocks(py_src: str) -> tuple[list[dict], dict | None]:
    fn = re.search(r"def generate_\w+_response\(.*?\n(.*?)\n    return _wrap", py_src, re.DOTALL)
    if not fn:
        raise ValueError("function body not found")
    body = fn.group(1)
    parts = re.split(r"\n    (elif |else:|if )", body)
    topics: list[dict] = []
    default: dict | None = None
    priority = 0
    i = 1
    while i < len(parts):
        kind = parts[i]
        block = parts[i + 1]
        i += 2
        if kind.startswith("else"):
            cond = None
        else:
            cm = re.match(r"(.+?):\n", block)
            if not cm:
                continue
            cond = cm.group(1).strip()
            block = block[cm.end() :]

        hm = re.search(r"heading = ", block)
        bm = re.search(r"body = ", block)
        tm = re.search(r"thinking = ", block)
        if not (hm and bm and tm):
            continue
        heading, _ = _extract_string_expr(block, hm.end())
        body_text, _ = _extract_string_expr(block, bm.end())
        thinking, _ = _extract_string_expr(block, tm.end())
        body_text = body_text.replace("{query}", "{query}")

        entry = {
            "heading": heading,
            "body": body_text,
            "thinking": thinking,
        }
        if cond is None:
            default = entry
        else:
            priority += 1
            entry["priority"] = priority
            entry["match"] = _parse_match(cond)
            topics.append(entry)
    return topics, default


def _slug(domain: str, heading: str, n: int) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")[:48]
    return f"{domain}-{n:02d}-{s}"


def main() -> None:
    engines = {
        "space": ROOT / "backend/services/space_engine.py",
        "earth": ROOT / "backend/services/earth_engine.py",
        "science": ROOT / "backend/services/science_engine.py",
        "history": ROOT / "backend/services/history_engine.py",
    }
    all_topics: list[dict] = []
    defaults: dict[str, dict] = {}
    for domain, path in engines.items():
        src = path.read_text(encoding="utf-8")
        topics, default = _extract_blocks(src)
        for n, t in enumerate(topics, 1):
            all_topics.append(
                {
                    "id": _slug(domain, t["heading"], n),
                    "domain": domain,
                    "match": t["match"],
                    "heading": t["heading"],
                    "body": t["body"],
                    "thinking": t["thinking"],
                    "priority": t["priority"],
                }
            )
        if default:
            defaults[domain] = {
                "id": f"{domain}-default",
                "domain": domain,
                "match": {},
                "heading": default["heading"],
                "body": default["body"],
                "thinking": default["thinking"],
            }

    history_kw = list(dict.fromkeys([*POLITICAL_KW, *HISTORY_EXTRA]))

    lines = [
        "/**",
        " * ForgeAI domain topic database — single source of truth for space/earth/science/history topics.",
        " * Auto-generated by scripts/generate-database-ts.py from engine files.",
        " * Regenerate Python seed: npm run db:export",
        " */",
        "",
        "export type Domain = 'math' | 'space' | 'earth' | 'science' | 'history';",
        "",
        "export interface TopicMatch {",
        "  any?: string[];",
        "  all?: string[];",
        "}",
        "",
        "export interface DomainTopic {",
        "  id: string;",
        "  domain: Domain;",
        "  match: TopicMatch;",
        "  heading: string;",
        "  body: string;",
        "  thinking: string;",
        "  priority?: number;",
        "}",
        "",
        f"export const mathKeywords: readonly string[] = {json.dumps(MATH_KW, indent=2)};",
        f"export const spaceKeywords: readonly string[] = {json.dumps(SPACE_KW, indent=2)};",
        f"export const earthKeywords: readonly string[] = {json.dumps(EARTH_KW, indent=2)};",
        f"export const scienceKeywords: readonly string[] = {json.dumps(SCIENCE_KW, indent=2)};",
        f"export const historyKeywords: readonly string[] = {json.dumps(history_kw, indent=2)};",
        "",
        "export const domainTopics: DomainTopic[] = " + json.dumps(all_topics, indent=2, ensure_ascii=False) + ";",
        "",
        "export const domainDefaults: Record<Exclude<Domain, 'math'>, DomainTopic> = "
        + json.dumps(defaults, indent=2, ensure_ascii=False)
        + ";",
        "",
    ]
    out = ROOT / "shared/database.ts"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(all_topics)} topics, {len(defaults)} defaults)")


if __name__ == "__main__":
    main()
