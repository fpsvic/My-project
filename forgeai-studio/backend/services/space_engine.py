def _wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_instant":
        return f"### {heading}\n\n{body.split(chr(10)+chr(10))[0]}"
    return f"### {heading}\n{body}"


def generate_space_response(query: str, mode: str) -> str:
    q = query.lower().strip()

    if any(w in q for w in ("star form", "star die", "stellar", "main sequence", "red giant", "white dwarf", "neutron star", "how stars")):
        heading = "How Stars Form and Die: The Stellar Life Cycle"
        body = (
            "Stars are born, live, and die on timescales of millions to trillions of years depending on their mass:\n\n"
            "**Birth: Stellar Nurseries**\n"
            "* Giant molecular clouds of hydrogen and dust collapse under gravity, heating to form a **protostar**.\n"
            "* When core temperatures reach ~10 million °C, **nuclear fusion** ignites — a star is born.\n\n"
            "**Main Sequence (Hydrogen-burning phase)**\n"
            "* Stars spend most of their lives fusing hydrogen into helium in their cores.\n"
            "* Our Sun is halfway through its ~**10 billion year** main-sequence life.\n"
            "* More massive stars burn hotter and faster — a 10-solar-mass star lives only ~**30 million years**.\n\n"
            "**Death Scenarios (by mass)**\n"
            "| Initial Mass | Path | Final Remnant |\n"
            "|-------------|------|---------------|\n"
            "| < 8 solar masses | Red Giant → Planetary Nebula | **White Dwarf** |\n"
            "| 8–20 solar masses | Red Supergiant → Supernova | **Neutron Star** |\n"
            "| > 20 solar masses | Red Supergiant → Supernova | **Black Hole** |\n\n"
            "**Key stages**\n"
            "* **Red Giant**: Hydrogen exhausted in core — outer layers expand enormously. The Sun will engulf Mercury and Venus in ~5 billion years.\n"
            "* **Supernova**: A cataclysmic explosion visible across galaxies — forges heavy elements (iron, gold, uranium) and seeds them into space.\n"
            "* **Neutron Star**: Incredibly dense (~1 solar mass in a 20 km sphere); may spin 700 times/second as a **pulsar**.\n"
            "* **White Dwarf**: Earth-sized ember of carbon and oxygen that slowly cools over billions of years.\n\n"
            "[COSMIC_CARD: formula: Sun's Main Sequence Lifespan | result: ~10 Billion Years | style: indigo]"
        )
        thinking = "- **Intent:** Stellar evolution lifecycle query.\n- **Parameters:** Mass-dependent death pathways, main sequence timescales, supernova remnant types."

    elif any(w in q for w in ("dark matter", "dark energy")):
        heading = "Dark Matter & Dark Energy: The Invisible Universe"
        body = (
            "Together, dark matter and dark energy make up ~**95% of the total content** of the universe:\n\n"
            "**Dark Matter (~27% of universe)**\n"
            "* Does not emit, absorb, or reflect light — detected only through its **gravitational effects**.\n"
            "* Evidence:\n"
            "  - Galaxy rotation curves: stars at galaxy edges orbit too fast to be explained by visible matter alone.\n"
            "  - Gravitational lensing: light bends around invisible mass concentrations.\n"
            "  - Bullet Cluster: two colliding galaxy clusters show dark matter separating from normal matter.\n"
            "* Leading candidates: **WIMPs** (Weakly Interacting Massive Particles) and **axions** (both unconfirmed).\n\n"
            "**Dark Energy (~68% of universe)**\n"
            "* A mysterious force causing the **accelerating expansion** of the universe.\n"
            "* Discovered in 1998 by Saul Perlmutter, Brian Schmidt, and Adam Riess (Nobel Prize 2011) from observations of distant Type Ia supernovae.\n"
            "* May be the **cosmological constant (Λ)** Einstein originally added (then removed) from his equations.\n"
            "* The ultimate fate of the universe depends on its nature — possibilities include the **Big Rip**, **Big Freeze**, or **Big Crunch**.\n\n"
            "**Normal matter (us):** only ~**5%** of everything.\n\n"
            "[COSMIC_CARD: formula: Universe Composition | result: 68% Dark Energy, 27% Dark Matter, 5% Normal | style: indigo]"
        )
        thinking = "- **Intent:** Cosmology dark matter/energy query.\n- **Parameters:** Observational evidence, composition percentages, candidate particles."

    elif any(w in q for w in ("voyager", "interstellar")):
        heading = "The Voyager Probes: Humanity's Farthest Travellers"
        body = (
            "NASA's twin Voyager spacecraft, launched in **1977**, are the most distant human-made objects:\n\n"
            "**Voyager 1**\n"
            "* Launched: **September 5, 1977**\n"
            "* Crossed into **interstellar space** in August 2012 — the first spacecraft to do so.\n"
            "* Distance (2024): over **24 billion km** (~162 AU) from the Sun.\n"
            "* Still transmitting data; signals take ~22 hours to reach Earth at the speed of light.\n\n"
            "**Voyager 2**\n"
            "* Launched: **August 20, 1977** (first, but slower trajectory)\n"
            "* The only spacecraft to fly past all four outer planets: Jupiter, Saturn, Uranus, Neptune.\n"
            "* Entered interstellar space in **November 2018**.\n"
            "* Distance (2024): over **20 billion km** (~135 AU) from the Sun.\n\n"
            "**The Golden Record**\n"
            "Both Voyagers carry a gold-plated copper disc containing:\n"
            "- 115 images of Earth and life\n"
            "- Greetings in 55 languages\n"
            "- 90 minutes of music from around the world\n"
            "- Sounds of Earth (waves, wind, animals)\n\n"
            "**Power**: Nuclear RTGs (Radioisotope Thermoelectric Generators) fuelled by Plutonium-238. Expected to lose power ~**2025–2030**.\n\n"
            "[COSMIC_CARD: formula: Voyager 1 Distance (2024) | result: >162 AU from Sun | style: indigo]"
        )
        thinking = "- **Intent:** Voyager mission status and specifications query.\n- **Parameters:** Launch dates, interstellar crossing milestones, Golden Record contents."

    elif any(w in q for w in ("james webb", "jwst", "webb telescope")):
        heading = "James Webb Space Telescope (JWST)"
        body = (
            "The **James Webb Space Telescope** is NASA's premier space observatory, succeeding Hubble:\n\n"
            "**Key Facts**\n"
            "* Launched: **December 25, 2021** on an Ariane 5 rocket.\n"
            "* Orbits the **L2 Lagrange point** — 1.5 million km from Earth, always in Earth's shadow.\n"
            "* Primary mirror: **6.5 metres** diameter (18 gold-plated beryllium segments) — 2.7× Hubble's mirror.\n"
            "* Observes primarily in **infrared** (0.6–28 μm), revealing what Hubble cannot see.\n"
            "* Sunshield size: tennis-court-sized (5 layers of Kapton film) — maintains mirror at −233°C.\n\n"
            "**Scientific Goals**\n"
            "1. Observe the **first galaxies** formed after the Big Bang (looking back >13.5 billion years).\n"
            "2. Study **exoplanet atmospheres** for biosignatures (water, methane, oxygen).\n"
            "3. Reveal the formation of **stars and planetary systems**.\n"
            "4. Investigate dark matter and the early universe's structure.\n\n"
            "**First Images (July 2022)**\n"
            "- Deepest infrared image of the universe ever taken (SMACS 0723 galaxy cluster)\n"
            "- Atmospheric composition of exoplanet WASP-96b\n"
            "- Carina Nebula stellar nursery in unprecedented detail\n\n"
            "[COSMIC_CARD: formula: JWST Primary Mirror | result: 6.5 m diameter (18 segments) | style: indigo]"
        )
        thinking = "- **Intent:** James Webb Space Telescope specifications and mission query.\n- **Parameters:** Mirror size, L2 orbit, infrared capabilities, scientific objectives."

    elif any(w in q for w in ("hubble", "hubble's law", "expanding universe", "expansion", "redshift", "recession")):
        heading = "Hubble's Law & The Expanding Universe"
        body = (
            "**Hubble's Law** (1929) states that galaxies are moving away from us, and the farther they are, the faster they recede:\n\n"
            "$$v = H_0 \\times d$$\n\n"
            "Where:\n"
            "* $v$ = recession velocity of the galaxy\n"
            "* $d$ = distance to the galaxy\n"
            "* $H_0$ = **Hubble Constant** ≈ **67–74 km/s per megaparsec** (current measurements disagree slightly — the 'Hubble tension')\n\n"
            "**What it means**\n"
            "* Discovered by Edwin Hubble using galaxy **redshifts** — light from receding galaxies is stretched to longer (redder) wavelengths.\n"
            "* Running the expansion backward implies all matter originated from a single point ~**13.8 billion years ago** (the Big Bang).\n"
            "* The expansion is **accelerating** — driven by dark energy (discovered 1998).\n"
            "* Galaxies beyond the **Hubble horizon** (~46 billion light-years) are receding faster than light and are permanently unobservable.\n\n"
            "**Cosmic Distance Ladder**\n"
            "Astronomers measure $H_0$ using: Cepheid variable stars → Type Ia supernovae → galaxy recession velocities.\n\n"
            "[COSMIC_CARD: formula: Hubble Constant (H₀) | result: ~70 km/s/Mpc | style: indigo]"
        )
        thinking = "- **Intent:** Cosmological expansion and Hubble's Law query.\n- **Parameters:** Hubble constant value, redshift mechanism, Hubble tension debate."

    elif any(w in q for w in ("cosmic microwave", "cmb", "microwave background", "afterglow", "big bang radiation")):
        heading = "Cosmic Microwave Background Radiation (CMB)"
        body = (
            "The **CMB** is the thermal afterglow of the Big Bang — the oldest light in the universe:\n\n"
            "**What is it?**\n"
            "* About **380,000 years** after the Big Bang, the universe cooled enough for electrons and protons to combine into neutral hydrogen (**recombination**). The universe became transparent to light for the first time.\n"
            "* That first light — released everywhere simultaneously — has been travelling ever since and is now detected as microwave radiation permeating the entire sky.\n\n"
            "**Key Properties**\n"
            "* Temperature: **2.725 K** (−270.4°C) — almost perfectly uniform across the sky.\n"
            "* Tiny temperature fluctuations of ~**1 part in 100,000** reveal the seeds of today's galaxy structure.\n"
            "* Spectrum: perfect **blackbody radiation** — the most precisely measured blackbody in nature.\n\n"
            "**Discovery & Measurement**\n"
            "* Accidentally discovered by **Arno Penzias and Robert Wilson** in 1965 (Nobel Prize 1978).\n"
            "* Mapped in detail by **COBE** (1989), **WMAP** (2001), and **Planck** satellite (2009–2013).\n"
            "* Planck data gave us the most precise age of the universe: **13.787 ± 0.020 billion years**.\n\n"
            "[COSMIC_CARD: formula: CMB Temperature | result: 2.725 K | style: indigo]"
        )
        thinking = "- **Intent:** Cosmic microwave background query.\n- **Parameters:** Recombination epoch, blackbody temperature, satellite measurements."

    elif any(w in q for w in ("multiverse", "parallel universe", "many worlds", "inflationary multiverse")):
        heading = "The Multiverse Theory"
        body = (
            "The **multiverse** is the hypothetical collection of multiple universes beyond our own observable universe:\n\n"
            "**1. Inflationary Multiverse (Level I & II)**\n"
            "* Cosmic inflation may have spawned countless separate 'bubble universes', each with potentially different physical constants.\n\n"
            "**2. Many-Worlds Interpretation (Level III — Quantum)**\n"
            "* Proposed by Hugh Everett (1957): every quantum measurement causes the universe to **branch** into separate realities.\n\n"
            "**3. String Theory Landscape (Level II)**\n"
            "* String theory allows ~$10^{500}$ different configurations of extra dimensions — each could be a different universe with different physics.\n\n"
            "**4. Mathematical Multiverse (Level IV)**\n"
            "* Max Tegmark's proposal: every mathematically consistent structure is a physical reality.\n\n"
            "**Status**: Currently **not falsifiable** — remains speculative but considered a legitimate extension of established physics by many researchers.\n\n"
            "[COSMIC_CARD: formula: String Theory Landscape | result: ~10⁵⁰⁰ possible universes | style: indigo]"
        )
        thinking = "- **Intent:** Multiverse theoretical cosmology query.\n- **Parameters:** Inflationary, quantum many-worlds, string landscape scenarios."

    elif any(w in q for w in ("exoplanet", "transit method", "radial velocity", "planet detection", "kepler", "habitable zone")):
        heading = "Exoplanet Detection Methods"
        body = (
            "Over **5,600 confirmed exoplanets** have been found (as of 2024). The two primary detection methods:\n\n"
            "**1. Transit Method (~75% of discoveries)**\n"
            "* When a planet passes in front of its star, it blocks a tiny fraction of starlight.\n"
            "* A **1% dip** in brightness typically indicates a Jupiter-sized planet; Earth would cause a ~**0.008% dip**.\n"
            "* Used by: **Kepler** (2009–2018, 2,600+ planets), **TESS** (2018–present), **JWST**.\n\n"
            "**2. Radial Velocity (Doppler Method, ~20% of discoveries)**\n"
            "* A planet's gravity causes its host star to **wobble** slightly.\n"
            "* The star's light is **blueshifted** as it moves toward us and **redshifted** as it moves away.\n\n"
            "**Other Methods**: Direct imaging, gravitational microlensing, astrometry.\n\n"
            "**Notable Discoveries**\n"
            "- **Proxima Centauri b**: Closest known exoplanet (4.24 ly), potentially habitable.\n"
            "- **TRAPPIST-1 system**: 7 Earth-sized planets, 3 in the habitable zone, 39 ly away.\n"
            "- **51 Pegasi b** (1995): First exoplanet around a Sun-like star (Nobel Prize 2019).\n\n"
            "[COSMIC_CARD: formula: Confirmed Exoplanets (2024) | result: >5,600 confirmed | style: indigo]"
        )
        thinking = "- **Intent:** Exoplanet detection methodology query.\n- **Parameters:** Transit photometry, Doppler spectroscopy, Kepler/TESS missions."

    elif any(w in q for w in ("asteroid belt", "kuiper belt", "kuiper", "asteroid", "ceres", "pluto")):
        heading = "Asteroid Belt vs. Kuiper Belt"
        body = (
            "**Asteroid Belt**\n"
            "* Location: Between **Mars and Jupiter** (2.2–3.2 AU from the Sun).\n"
            "* Contains millions of rocky/metallic objects — remnants from the proto-planetary disk that never coalesced due to Jupiter's gravity.\n"
            "* Largest object: **Ceres** (dwarf planet, 945 km diameter) — contains ~1/3 of the belt's total mass.\n"
            "* Total mass: only ~4% of Earth's Moon.\n"
            "* NASA's DART mission **deflected** the asteroid Dimorphos in **September 2022**.\n\n"
            "**Kuiper Belt**\n"
            "* Location: Beyond **Neptune's orbit** (30–50 AU from the Sun).\n"
            "* Contains icy bodies (comets, dwarf planets) — ~**20× wider** and **20–200× more massive** than the asteroid belt.\n"
            "* Contains: **Pluto** (2,377 km), Eris, Makemake, Haumea — all dwarf planets.\n"
            "* Source of **short-period comets** (orbital period <200 years).\n"
            "* Explored by **New Horizons** (Pluto flyby July 2015; Arrokoth flyby January 2019).\n\n"
            "**Oort Cloud** (beyond Kuiper Belt, 2,000–100,000 AU) — source of long-period comets.\n\n"
            "[COSMIC_CARD: formula: Kuiper Belt Location | result: 30–50 AU from the Sun | style: indigo]"
        )
        thinking = "- **Intent:** Solar system small body region query.\n- **Parameters:** Asteroid belt vs Kuiper belt composition, location, major objects."

    elif "mars" in q and any(w in q for w in ("coloniz", "colonise", "colony", "terraforming", "settle", "live on", "inhabit", "mission to")):
        heading = "Colonisation of Mars: Challenges & Plans"
        body = (
            "Mars is the top candidate for human colonisation beyond Earth:\n\n"
            "**Why Mars?** Day length of 24h 37m, water ice at poles and subsurface, rocky terrain with usable resources. Average distance: **225 million km** (~7 months travel one-way).\n\n"
            "**Key Challenges**\n"
            "* **Radiation**: No global magnetic field — surface radiation is **700× Earth's**.\n"
            "* **Atmosphere**: 95% CO₂, pressure only 0.6% of Earth's.\n"
            "* **Temperature**: Average −60°C (range −125°C to +20°C).\n"
            "* **Gravity**: 38% of Earth's — long-term health effects unknown.\n"
            "* **Communication delay**: 4–24 minutes one-way.\n\n"
            "**Current Missions**\n"
            "* **NASA Perseverance rover** (2021): Collecting rock samples and testing MOXIE (oxygen from CO₂).\n"
            "* **SpaceX Starship**: Designed to carry 100 people; crewed missions targeted **late 2020s**.\n"
            "* NASA's **Moon to Mars** programme aims for humans on Mars in the **2030s**.\n\n"
            "**Terraforming**: Would require centuries to millennia to make Mars Earth-like.\n\n"
            "[COSMIC_CARD: formula: Mars Surface Gravity | result: 38% of Earth (3.72 m/s²) | style: indigo]"
        )
        thinking = "- **Intent:** Mars colonisation feasibility and plans query.\n- **Parameters:** Environmental hazards, radiation levels, current mission timelines."

    elif "mars" in q or "red planet" in q:
        heading = "Mars: The Red Planet"
        body = (
            "Mars is the fourth planet from the Sun with an average distance of **142 million miles** "
            "($228\\text{ million km}$) from it.\n\n"
            "Its red hue comes from iron oxide (rust) dust. A year on Mars lasts **687 Earth days** "
            "and its surface gravity is only **38% of Earth's**.\n\n"
            "[COSMIC_CARD: formula: Mars Gravity Ratio | result: 38% of Earth | style: indigo]"
        )
        thinking = "- **Intent:** Planet specific mechanics query (Mars).\n- **Data Points:** Surface rust oxidation chemistry, orbital timeline metrics."

    elif "sun" in q and any(w in q for w in ("earth", "distance", "apart", "far")):
        heading = "Earth-to-Sun Orbit Distance"
        body = (
            "The distance between the Earth and the Sun is not perfectly static because our orbit is elliptical. "
            "On average, the Earth is about **93 million miles** away from the Sun.\n\n"
            "This distance is mathematically represented as **1 Astronomical Unit (AU)**. "
            "Sunlight, traveling at $186{,}282\\text{ miles per second}$, takes approximately "
            "**8 minutes and 20 seconds** to reach us.\n\n"
            "[COSMIC_CARD: formula: Average Earth-Sun Distance (1 AU) | result: 93,000,000 Miles | style: indigo]"
        )
        thinking = "- **Intent:** Astronomy constant query (Earth-Sun distance).\n- **Parameters:** Elliptical orbit variance, AU coordinate translation.\n- **Speed Integration:** Sunlight travel delta $\\approx 500\\text{ seconds}$."

    elif "moon" in q and any(w in q for w in ("earth", "distance", "far", "apart")):
        heading = "Earth-to-Moon Orbit Distance"
        body = (
            "Our natural satellite orbits the Earth in an elliptical path. Its average distance is "
            "**238,855 miles** ($384{,}400\\text{ km}$).\n\n"
            "At perigee it is about $225{,}623\\text{ miles}$ away; at apogee $252{,}088\\text{ miles}$. "
            "This is roughly equivalent to wrapping 30 Earths in a row!\n\n"
            "[COSMIC_CARD: formula: Average Earth-Moon Distance | result: 238,855 Miles | style: indigo]"
        )
        thinking = "- **Intent:** Moon orbit constant query.\n- **Math Check:** Translating metric apogee/perigee scale limits to statute miles."

    elif "speed of light" in q:
        heading = "Universal Speed Limit (c)"
        body = (
            "According to Einstein's Theory of Special Relativity, the speed of light in a vacuum ($c$) "
            "is the absolute cosmic speed limit: **186,282 miles per second** ($299{,}792\\text{ km/s}$).\n\n"
            "At this speed you could circle Earth's equator **7.5 times in a single second**!\n\n"
            "[COSMIC_CARD: formula: Speed of Light in Vacuum (c) | result: 186,282 mi/s | style: emerald]"
        )
        thinking = "- **Intent:** Universal constant query (c).\n- **Reference Framework:** Einstein's Special Relativity model boundaries."

    elif "universe" in q and any(w in q for w in ("size", "big", "scale", "diameter")):
        heading = "Scale of the Observable Universe"
        body = (
            "The observable universe is the spherical region of space visible from Earth. "
            "Its diameter is estimated at about **93 billion light-years**.\n\n"
            "Although the universe is only $13.8\\text{ billion years}$ old, space has expanded faster "
            "than the speed of light, stretching the observable edge far beyond $13.8\\text{ billion light-years}$.\n\n"
            "[COSMIC_CARD: formula: Observable Universe Diameter | result: 93,000,000,000 ly | style: indigo]"
        )
        thinking = "- **Intent:** Cosmological scale query.\n- **Cosmic Metric:** Big Bang timeline delta versus cosmological expansion speed ratio."

    elif "gravity" in q or " g " in q:
        heading = "Fundamental Constant of Gravity"
        body = (
            "Gravity is the attractive force that acts between all matter. On Earth's surface, "
            "the acceleration due to gravity is approximately **$9.81\\text{ m/s}^2$**.\n\n"
            "The universal gravitational constant ($G$) is:\n\n"
            "$$G \\approx 6.674 \\times 10^{-11}\\text{ m}^3\\text{ kg}^{-1}\\text{ s}^{-2}$$\n\n"
            "[COSMIC_CARD: formula: Gravitational Acceleration (Earth) | result: 9.81 m/s² | style: indigo]"
        )
        thinking = "- **Intent:** Gravity mechanics query.\n- **Parameters:** Surface gravity $g$ versus Newtonian gravitational constant $G$."

    else:
        heading = "Astronomical Analysis"
        body = (
            f"Based on my internal offline cosmological database, I have processed your inquiry regarding **\"{query}\"**.\n\n"
            "1. **Cosmic Scaling Boundaries:** Outer space operates on scales that transcend standard human perception.\n"
            "2. **The Vacuum Medium:** Space is a nearly perfect vacuum where light travels unimpeded.\n"
            "3. **Universal Physics Constants:** Every star and galaxy is governed by $c$, $G$, and $\\hbar$."
        )
        thinking = "- **Intent:** Open space topic query.\n- **Formulating Output:** Providing a comprehensive cosmic mechanics overview."

    return _wrap(thinking, heading, body, mode)
