def _wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_thinking":
        return (
            f"### <i class=\"fa-solid fa-user-astronaut text-indigo-500 mr-2\"></i> Thinking Process\n"
            f"{thinking}\n\n---\n\n### {heading}\n{body}"
        )
    if mode == "forge_instant":
        return f"### {heading}\n\n{body.split(chr(10)+chr(10))[0]}"
    return f"### {heading}\n{body}"


def generate_space_response(query: str, mode: str) -> str:
    q = query.lower().strip()

    if "sun" in q and any(w in q for w in ("earth", "distance", "apart", "far")):
        heading = "Earth-to-Sun Orbit Distance"
        body = (
            "The distance between the Earth and the Sun is not perfectly static because our orbit is elliptical. "
            "On average, the Earth is about **93 million miles** away from the Sun.\n\n"
            "This distance is mathematically represented as **1 Astronomical Unit (AU)**. "
            "Sunlight, traveling at $186{,}282\\text{ miles per second}$, takes approximately "
            "**8 minutes and 20 seconds** to reach us.\n\n"
            "[COSMIC_CARD: formula: Average Earth-Sun Distance (1 AU) | result: 93,000,000 Miles | style: indigo]"
        )
        thinking = (
            "- **Intent:** Astronomy constant query (Earth-Sun distance).\n"
            "- **Parameters:** Elliptical orbit variance, AU coordinate translation.\n"
            "- **Speed Integration:** Sunlight travel delta $\\approx 500\\text{ seconds}$."
        )

    elif "moon" in q and any(w in q for w in ("earth", "distance", "far", "apart")):
        heading = "Earth-to-Moon Orbit Distance"
        body = (
            "Our natural satellite orbits the Earth in an elliptical path. Its average distance is "
            "**238,855 miles** ($384{,}400\\text{ km}$).\n\n"
            "At perigee it is about $225{,}623\\text{ miles}$ away; at apogee $252{,}088\\text{ miles}$. "
            "This is roughly equivalent to wrapping 30 Earths in a row!\n\n"
            "[COSMIC_CARD: formula: Average Earth-Moon Distance | result: 238,855 Miles | style: indigo]"
        )
        thinking = (
            "- **Intent:** Moon orbit constant query.\n"
            "- **Math Check:** Translating metric apogee/perigee scale limits to statute miles."
        )

    elif "speed of light" in q:
        heading = "Universal Speed Limit (c)"
        body = (
            "According to Einstein's Theory of Special Relativity, the speed of light in a vacuum ($c$) "
            "is the absolute cosmic speed limit: **186,282 miles per second** ($299{,}792\\text{ km/s}$).\n\n"
            "At this speed you could circle Earth's equator **7.5 times in a single second**!\n\n"
            "[COSMIC_CARD: formula: Speed of Light in Vacuum (c) | result: 186,282 mi/s | style: emerald]"
        )
        thinking = (
            "- **Intent:** Universal constant query (c).\n"
            "- **Reference Framework:** Einstein's Special Relativity model boundaries."
        )

    elif "universe" in q and any(w in q for w in ("size", "big", "scale", "diameter")):
        heading = "Scale of the Observable Universe"
        body = (
            "The observable universe is the spherical region of space visible from Earth. "
            "Its diameter is estimated at about **93 billion light-years**.\n\n"
            "Although the universe is only $13.8\\text{ billion years}$ old, space has expanded faster "
            "than the speed of light, stretching the observable edge far beyond $13.8\\text{ billion light-years}$.\n\n"
            "[COSMIC_CARD: formula: Observable Universe Diameter | result: 93,000,000,000 ly | style: indigo]"
        )
        thinking = (
            "- **Intent:** Cosmological scale query.\n"
            "- **Cosmic Metric:** Big Bang timeline delta versus cosmological expansion speed ratio."
        )

    elif "gravity" in q or " g " in q:
        heading = "Fundamental Constant of Gravity"
        body = (
            "Gravity is the attractive force that acts between all matter. On Earth's surface, "
            "the acceleration due to gravity is approximately **$9.81\\text{ m/s}^2$**.\n\n"
            "The universal gravitational constant ($G$) is:\n\n"
            "$$G \\approx 6.674 \\times 10^{-11}\\text{ m}^3\\text{ kg}^{-1}\\text{ s}^{-2}$$\n\n"
            "[COSMIC_CARD: formula: Gravitational Acceleration (Earth) | result: 9.81 m/s² | style: indigo]"
        )
        thinking = (
            "- **Intent:** Gravity mechanics query.\n"
            "- **Parameters:** Surface gravity $g$ versus Newtonian gravitational constant $G$."
        )

    elif "mars" in q or "red planet" in q:
        heading = "Mars: The Red Planet"
        body = (
            "Mars is the fourth planet from the Sun with an average distance of **142 million miles** "
            "($228\\text{ million km}$) from it.\n\n"
            "Its red hue comes from iron oxide (rust) dust. A year on Mars lasts **687 Earth days** "
            "and its surface gravity is only **38% of Earth's**.\n\n"
            "[COSMIC_CARD: formula: Mars Gravity Ratio | result: 38% of Earth | style: indigo]"
        )
        thinking = (
            "- **Intent:** Planet specific mechanics query (Mars).\n"
            "- **Data Points:** Surface rust oxidation chemistry, orbital timeline metrics."
        )

    else:
        heading = "Astronomical Analysis"
        body = (
            f"Based on my internal offline cosmological database, I have processed your inquiry regarding **\"{query}\"**.\n\n"
            "1. **Cosmic Scaling Boundaries:** Outer space operates on scales that transcend standard human perception.\n"
            "2. **The Vacuum Medium:** Space is a nearly perfect vacuum where light travels unimpeded.\n"
            "3. **Universal Physics Constants:** Every star and galaxy is governed by $c$, $G$, and $\\hbar$."
        )
        thinking = (
            "- **Intent:** Open space topic query.\n"
            "- **Formulating Output:** Providing a comprehensive cosmic mechanics overview."
        )

    return _wrap(thinking, heading, body, mode)
