/**
 * ForgeAI domain topic database — single source of truth for space/earth/science/history topics.
 * Regenerate Python seed: npm run db:export
 */

export type Domain = 'math' | 'space' | 'earth' | 'science' | 'history';

export interface TopicMatch {
  any?: string[];
  all?: string[];
}

export interface DomainTopic {
  id: string;
  domain: Domain;
  match: TopicMatch;
  heading: string;
  body: string;
  thinking: string;
  priority?: number;
}

export const mathKeywords: readonly string[] = [
  "derivative",
  "differentiate",
  "differentiation",
  "integral",
  "integrate",
  "integration",
  "antiderivative",
  "limit",
  "chain rule",
  "product rule",
  "quotient rule",
  "power rule",
  "polynomial",
  "calculus",
  "sin",
  "cos",
  "tan",
  "csc",
  "sec",
  "cot",
  "arcsin",
  "arccos",
  "arctan",
  "solve",
  "compute",
  "calculate",
  "evaluate",
  "simplify",
  "quadratic",
  "factorial",
  "fibonacci",
  "gcd",
  "lcm",
  "prime",
  "pythagorean",
  "hypotenuse",
  "mean",
  "median",
  "mode",
  "average",
  "variance",
  "standard deviation",
  "permutation",
  "combination",
  "convert",
  "geometry",
  "circle",
  "sphere",
  "cylinder",
  "cone",
  "triangle",
  "rectangle",
  "area",
  "volume",
  "perimeter"
];
export const spaceKeywords: readonly string[] = [
  "sun",
  "earth",
  "moon",
  "mars",
  "space",
  "astronom",
  "galaxy",
  "universe",
  "distance",
  "miles",
  "gravity",
  "orbit",
  "planet",
  "speed of light",
  "cosmic",
  "sol",
  "luna",
  "star",
  "solar",
  "venus",
  "saturn",
  "jupiter",
  "neptune",
  "uranus",
  "mercury",
  "milky way",
  "black hole",
  "nebula",
  "supernova",
  "neutron star",
  "dark matter",
  "dark energy",
  "big bang",
  "light year",
  "parsec",
  "hubble",
  "telescope",
  "asteroid",
  "comet",
  "meteor",
  "atmosphere",
  "exoplanet",
  "wormhole"
];
export const earthKeywords: readonly string[] = [
  "rock",
  "mineral",
  "stone",
  "geolog",
  "petrolog",
  "basalt",
  "granite",
  "sediment",
  "metamorph",
  "igneous",
  "volcano",
  "lava",
  "magma",
  "magmatic",
  "caldera",
  "tectonic",
  "plate",
  "ring of fire",
  "subduction",
  "trench",
  "mariana",
  "ocean",
  "underwater",
  "hydrothermal",
  "vent",
  "black smoker",
  "seafloor",
  "crust",
  "mantle",
  "mohs",
  "earthquake",
  "seismic",
  "richter",
  "fossil",
  "erosion",
  "glacier",
  "ice age",
  "carbon dating"
];
export const scienceKeywords: readonly string[] = [
  "quantum",
  "physics",
  "planck",
  "boltzmann",
  "chemistry",
  "element",
  "carbon",
  "noble",
  "electroneg",
  "dna",
  "gene",
  "cell",
  "transcription",
  "biology",
  "golden ratio",
  "phi",
  "euler",
  "irrational",
  "einstein",
  "relativity",
  "e=mc",
  "photon",
  "electron",
  "proton",
  "neutron",
  "atom",
  "molecule",
  "compound",
  "periodic",
  "mendeleev",
  "entropy",
  "thermodynamics",
  "maxwell",
  "faraday",
  "newton",
  "gravity constant",
  "avogadro",
  "mole",
  "bohr",
  "schrodinger",
  "heisenberg",
  "uncertainty"
];
export const historyKeywords: readonly string[] = [
  "washington",
  "president",
  "lincoln",
  "fdr",
  "new deal",
  "civil war",
  "party",
  "whig",
  "federalist",
  "constitution",
  "politic",
  "align",
  "congress",
  "senate",
  "amendment",
  "declaration",
  "jefferson",
  "adams",
  "hamilton",
  "madison",
  "jackson",
  "grant",
  "wilson",
  "eisenhower",
  "kennedy",
  "reagan",
  "clinton",
  "obama",
  "trump",
  "biden",
  "world war",
  "revolution",
  "declaration of independence",
  "founding fathers",
  "slavery",
  "abolition",
  "reconstruction",
  "great depression",
  "cold war",
  "vietnam",
  "roosevelt",
  "democrat",
  "republican",
  "colonial",
  "egypt",
  "pharaoh",
  "pyramid",
  "rome",
  "renaissance",
  "history",
  "ancient",
  "empire",
  "medieval",
  "century",
  "war",
  "battle",
  "dynasty",
  "civilization"
];

export const domainTopics: DomainTopic[] = [
  {
    "id": "space-01-how-stars-form-and-die-the-stellar-life-cycle",
    "domain": "space",
    "match": {
      "any": [
        "star form",
        "star die",
        "stellar",
        "main sequence",
        "red giant",
        "white dwarf",
        "neutron star",
        "how stars"
      ]
    },
    "heading": "How Stars Form and Die: The Stellar Life Cycle",
    "body": "Stars are born, live, and die on timescales of millions to trillions of years depending on their mass:\n\n**Birth: Stellar Nurseries**\n* Giant molecular clouds of hydrogen and dust collapse under gravity, heating to form a **protostar**.\n* When core temperatures reach ~10 million °C, **nuclear fusion** ignites — a star is born.\n\n**Main Sequence (Hydrogen-burning phase)**\n* Stars spend most of their lives fusing hydrogen into helium in their cores.\n* Our Sun is halfway through its ~**10 billion year** main-sequence life.\n* More massive stars burn hotter and faster — a 10-solar-mass star lives only ~**30 million years**.\n\n**Death Scenarios (by mass)**\n| Initial Mass | Path | Final Remnant |\n|-------------|------|---------------|\n| < 8 solar masses | Red Giant → Planetary Nebula | **White Dwarf** |\n| 8–20 solar masses | Red Supergiant → Supernova | **Neutron Star** |\n| > 20 solar masses | Red Supergiant → Supernova | **Black Hole** |\n\n**Key stages**\n* **Red Giant**: Hydrogen exhausted in core — outer layers expand enormously. The Sun will engulf Mercury and Venus in ~5 billion years.\n* **Supernova**: A cataclysmic explosion visible across galaxies — forges heavy elements (iron, gold, uranium) and seeds them into space.\n* **Neutron Star**: Incredibly dense (~1 solar mass in a 20 km sphere); may spin 700 times/second as a **pulsar**.\n* **White Dwarf**: Earth-sized ember of carbon and oxygen that slowly cools over billions of years.\n\n[COSMIC_CARD: formula: Sun's Main Sequence Lifespan | result: ~10 Billion Years | style: indigo]",
    "thinking": "- **Intent:** Stellar evolution lifecycle query.\n- **Parameters:** Mass-dependent death pathways, main sequence timescales, supernova remnant types.",
    "priority": 1
  },
  {
    "id": "space-02-dark-matter-dark-energy-the-invisible-universe",
    "domain": "space",
    "match": {
      "any": [
        "dark matter",
        "dark energy"
      ]
    },
    "heading": "Dark Matter & Dark Energy: The Invisible Universe",
    "body": "Together, dark matter and dark energy make up ~**95% of the total content** of the universe:\n\n**Dark Matter (~27% of universe)**\n* Does not emit, absorb, or reflect light — detected only through its **gravitational effects**.\n* Evidence:\n  - Galaxy rotation curves: stars at galaxy edges orbit too fast to be explained by visible matter alone.\n  - Gravitational lensing: light bends around invisible mass concentrations.\n  - Bullet Cluster: two colliding galaxy clusters show dark matter separating from normal matter.\n* Leading candidates: **WIMPs** (Weakly Interacting Massive Particles) and **axions** (both unconfirmed).\n\n**Dark Energy (~68% of universe)**\n* A mysterious force causing the **accelerating expansion** of the universe.\n* Discovered in 1998 by Saul Perlmutter, Brian Schmidt, and Adam Riess (Nobel Prize 2011) from observations of distant Type Ia supernovae.\n* May be the **cosmological constant (Λ)** Einstein originally added (then removed) from his equations.\n* The ultimate fate of the universe depends on its nature — possibilities include the **Big Rip**, **Big Freeze**, or **Big Crunch**.\n\n**Normal matter (us):** only ~**5%** of everything.\n\n[COSMIC_CARD: formula: Universe Composition | result: 68% Dark Energy, 27% Dark Matter, 5% Normal | style: indigo]",
    "thinking": "- **Intent:** Cosmology dark matter/energy query.\n- **Parameters:** Observational evidence, composition percentages, candidate particles.",
    "priority": 2
  },
  {
    "id": "space-03-the-voyager-probes-humanity-s-farthest-traveller",
    "domain": "space",
    "match": {
      "any": [
        "voyager",
        "interstellar"
      ]
    },
    "heading": "The Voyager Probes: Humanity's Farthest Travellers",
    "body": "NASA's twin Voyager spacecraft, launched in **1977**, are the most distant human-made objects:\n\n**Voyager 1**\n* Launched: **September 5, 1977**\n* Crossed into **interstellar space** in August 2012 — the first spacecraft to do so.\n* Distance (2024): over **24 billion km** (~162 AU) from the Sun.\n* Still transmitting data; signals take ~22 hours to reach Earth at the speed of light.\n\n**Voyager 2**\n* Launched: **August 20, 1977** (first, but slower trajectory)\n* The only spacecraft to fly past all four outer planets: Jupiter, Saturn, Uranus, Neptune.\n* Entered interstellar space in **November 2018**.\n* Distance (2024): over **20 billion km** (~135 AU) from the Sun.\n\n**The Golden Record**\nBoth Voyagers carry a gold-plated copper disc containing:\n- 115 images of Earth and life\n- Greetings in 55 languages\n- 90 minutes of music from around the world\n- Sounds of Earth (waves, wind, animals)\n\n**Power**: Nuclear RTGs (Radioisotope Thermoelectric Generators) fuelled by Plutonium-238. Expected to lose power ~**2025–2030**.\n\n[COSMIC_CARD: formula: Voyager 1 Distance (2024) | result: >162 AU from Sun | style: indigo]",
    "thinking": "- **Intent:** Voyager mission status and specifications query.\n- **Parameters:** Launch dates, interstellar crossing milestones, Golden Record contents.",
    "priority": 3
  },
  {
    "id": "space-04-james-webb-space-telescope-jwst",
    "domain": "space",
    "match": {
      "any": [
        "james webb",
        "jwst",
        "webb telescope"
      ]
    },
    "heading": "James Webb Space Telescope (JWST)",
    "body": "The **James Webb Space Telescope** is NASA's premier space observatory, succeeding Hubble:\n\n**Key Facts**\n* Launched: **December 25, 2021** on an Ariane 5 rocket.\n* Orbits the **L2 Lagrange point** — 1.5 million km from Earth, always in Earth's shadow.\n* Primary mirror: **6.5 metres** diameter (18 gold-plated beryllium segments) — 2.7× Hubble's mirror.\n* Observes primarily in **infrared** (0.6–28 μm), revealing what Hubble cannot see.\n* Sunshield size: tennis-court-sized (5 layers of Kapton film) — maintains mirror at −233°C.\n\n**Scientific Goals**\n1. Observe the **first galaxies** formed after the Big Bang (looking back >13.5 billion years).\n2. Study **exoplanet atmospheres** for biosignatures (water, methane, oxygen).\n3. Reveal the formation of **stars and planetary systems**.\n4. Investigate dark matter and the early universe's structure.\n\n**First Images (July 2022)**\n- Deepest infrared image of the universe ever taken (SMACS 0723 galaxy cluster)\n- Atmospheric composition of exoplanet WASP-96b\n- Carina Nebula stellar nursery in unprecedented detail\n\n[COSMIC_CARD: formula: JWST Primary Mirror | result: 6.5 m diameter (18 segments) | style: indigo]",
    "thinking": "- **Intent:** James Webb Space Telescope specifications and mission query.\n- **Parameters:** Mirror size, L2 orbit, infrared capabilities, scientific objectives.",
    "priority": 4
  },
  {
    "id": "space-05-hubble-s-law-the-expanding-universe",
    "domain": "space",
    "match": {
      "any": [
        "hubble",
        "hubble's law",
        "expanding universe",
        "expansion",
        "redshift",
        "recession"
      ]
    },
    "heading": "Hubble's Law & The Expanding Universe",
    "body": "**Hubble's Law** (1929) states that galaxies are moving away from us, and the farther they are, the faster they recede:\n\n$$v = H_0 \\times d$$\n\nWhere:\n* $v$ = recession velocity of the galaxy\n* $d$ = distance to the galaxy\n* $H_0$ = **Hubble Constant** ≈ **67–74 km/s per megaparsec** (current measurements disagree slightly — the 'Hubble tension')\n\n**What it means**\n* Discovered by Edwin Hubble using galaxy **redshifts** — light from receding galaxies is stretched to longer (redder) wavelengths.\n* Running the expansion backward implies all matter originated from a single point ~**13.8 billion years ago** (the Big Bang).\n* The expansion is **accelerating** — driven by dark energy (discovered 1998).\n* Galaxies beyond the **Hubble horizon** (~46 billion light-years) are receding faster than light and are permanently unobservable.\n\n**Cosmic Distance Ladder**\nAstronomers measure $H_0$ using: Cepheid variable stars → Type Ia supernovae → galaxy recession velocities.\n\n[COSMIC_CARD: formula: Hubble Constant (H₀) | result: ~70 km/s/Mpc | style: indigo]",
    "thinking": "- **Intent:** Cosmological expansion and Hubble's Law query.\n- **Parameters:** Hubble constant value, redshift mechanism, Hubble tension debate.",
    "priority": 5
  },
  {
    "id": "space-06-cosmic-microwave-background-radiation-cmb",
    "domain": "space",
    "match": {
      "any": [
        "cosmic microwave",
        "cmb",
        "microwave background",
        "afterglow",
        "big bang radiation"
      ]
    },
    "heading": "Cosmic Microwave Background Radiation (CMB)",
    "body": "The **CMB** is the thermal afterglow of the Big Bang — the oldest light in the universe:\n\n**What is it?**\n* About **380,000 years** after the Big Bang, the universe cooled enough for electrons and protons to combine into neutral hydrogen (**recombination**). The universe became transparent to light for the first time.\n* That first light — released everywhere simultaneously — has been travelling ever since and is now detected as microwave radiation permeating the entire sky.\n\n**Key Properties**\n* Temperature: **2.725 K** (−270.4°C) — almost perfectly uniform across the sky.\n* Tiny temperature fluctuations of ~**1 part in 100,000** reveal the seeds of today's galaxy structure.\n* Spectrum: perfect **blackbody radiation** — the most precisely measured blackbody in nature.\n\n**Discovery & Measurement**\n* Accidentally discovered by **Arno Penzias and Robert Wilson** in 1965 (Nobel Prize 1978).\n* Mapped in detail by **COBE** (1989), **WMAP** (2001), and **Planck** satellite (2009–2013).\n* Planck data gave us the most precise age of the universe: **13.787 ± 0.020 billion years**.\n\n[COSMIC_CARD: formula: CMB Temperature | result: 2.725 K | style: indigo]",
    "thinking": "- **Intent:** Cosmic microwave background query.\n- **Parameters:** Recombination epoch, blackbody temperature, satellite measurements.",
    "priority": 6
  },
  {
    "id": "space-07-the-multiverse-theory",
    "domain": "space",
    "match": {
      "any": [
        "multiverse",
        "parallel universe",
        "many worlds",
        "inflationary multiverse"
      ]
    },
    "heading": "The Multiverse Theory",
    "body": "The **multiverse** is the hypothetical collection of multiple universes beyond our own observable universe:\n\n**1. Inflationary Multiverse (Level I & II)**\n* Cosmic inflation may have spawned countless separate 'bubble universes', each with potentially different physical constants.\n\n**2. Many-Worlds Interpretation (Level III — Quantum)**\n* Proposed by Hugh Everett (1957): every quantum measurement causes the universe to **branch** into separate realities.\n\n**3. String Theory Landscape (Level II)**\n* String theory allows ~$10^{500}$ different configurations of extra dimensions — each could be a different universe with different physics.\n\n**4. Mathematical Multiverse (Level IV)**\n* Max Tegmark's proposal: every mathematically consistent structure is a physical reality.\n\n**Status**: Currently **not falsifiable** — remains speculative but considered a legitimate extension of established physics by many researchers.\n\n[COSMIC_CARD: formula: String Theory Landscape | result: ~10⁵⁰⁰ possible universes | style: indigo]",
    "thinking": "- **Intent:** Multiverse theoretical cosmology query.\n- **Parameters:** Inflationary, quantum many-worlds, string landscape scenarios.",
    "priority": 7
  },
  {
    "id": "space-08-exoplanet-detection-methods",
    "domain": "space",
    "match": {
      "any": [
        "exoplanet",
        "transit method",
        "radial velocity",
        "planet detection",
        "kepler",
        "habitable zone"
      ]
    },
    "heading": "Exoplanet Detection Methods",
    "body": "Over **5,600 confirmed exoplanets** have been found (as of 2024). The two primary detection methods:\n\n**1. Transit Method (~75% of discoveries)**\n* When a planet passes in front of its star, it blocks a tiny fraction of starlight.\n* A **1% dip** in brightness typically indicates a Jupiter-sized planet; Earth would cause a ~**0.008% dip**.\n* Used by: **Kepler** (2009–2018, 2,600+ planets), **TESS** (2018–present), **JWST**.\n\n**2. Radial Velocity (Doppler Method, ~20% of discoveries)**\n* A planet's gravity causes its host star to **wobble** slightly.\n* The star's light is **blueshifted** as it moves toward us and **redshifted** as it moves away.\n\n**Other Methods**: Direct imaging, gravitational microlensing, astrometry.\n\n**Notable Discoveries**\n- **Proxima Centauri b**: Closest known exoplanet (4.24 ly), potentially habitable.\n- **TRAPPIST-1 system**: 7 Earth-sized planets, 3 in the habitable zone, 39 ly away.\n- **51 Pegasi b** (1995): First exoplanet around a Sun-like star (Nobel Prize 2019).\n\n[COSMIC_CARD: formula: Confirmed Exoplanets (2024) | result: >5,600 confirmed | style: indigo]",
    "thinking": "- **Intent:** Exoplanet detection methodology query.\n- **Parameters:** Transit photometry, Doppler spectroscopy, Kepler/TESS missions.",
    "priority": 8
  },
  {
    "id": "space-09-asteroid-belt-vs-kuiper-belt",
    "domain": "space",
    "match": {
      "any": [
        "asteroid belt",
        "kuiper belt",
        "kuiper",
        "asteroid",
        "ceres",
        "pluto"
      ]
    },
    "heading": "Asteroid Belt vs. Kuiper Belt",
    "body": "**Asteroid Belt**\n* Location: Between **Mars and Jupiter** (2.2–3.2 AU from the Sun).\n* Contains millions of rocky/metallic objects — remnants from the proto-planetary disk that never coalesced due to Jupiter's gravity.\n* Largest object: **Ceres** (dwarf planet, 945 km diameter) — contains ~1/3 of the belt's total mass.\n* Total mass: only ~4% of Earth's Moon.\n* NASA's DART mission **deflected** the asteroid Dimorphos in **September 2022**.\n\n**Kuiper Belt**\n* Location: Beyond **Neptune's orbit** (30–50 AU from the Sun).\n* Contains icy bodies (comets, dwarf planets) — ~**20× wider** and **20–200× more massive** than the asteroid belt.\n* Contains: **Pluto** (2,377 km), Eris, Makemake, Haumea — all dwarf planets.\n* Source of **short-period comets** (orbital period <200 years).\n* Explored by **New Horizons** (Pluto flyby July 2015; Arrokoth flyby January 2019).\n\n**Oort Cloud** (beyond Kuiper Belt, 2,000–100,000 AU) — source of long-period comets.\n\n[COSMIC_CARD: formula: Kuiper Belt Location | result: 30–50 AU from the Sun | style: indigo]",
    "thinking": "- **Intent:** Solar system small body region query.\n- **Parameters:** Asteroid belt vs Kuiper belt composition, location, major objects.",
    "priority": 9
  },
  {
    "id": "space-10-colonisation-of-mars-challenges-plans",
    "domain": "space",
    "match": {
      "all": [
        "mars"
      ],
      "any": [
        "coloniz",
        "colonise",
        "colony",
        "terraforming",
        "settle",
        "live on",
        "inhabit",
        "mission to"
      ]
    },
    "heading": "Colonisation of Mars: Challenges & Plans",
    "body": "Mars is the top candidate for human colonisation beyond Earth:\n\n**Why Mars?** Day length of 24h 37m, water ice at poles and subsurface, rocky terrain with usable resources. Average distance: **225 million km** (~7 months travel one-way).\n\n**Key Challenges**\n* **Radiation**: No global magnetic field — surface radiation is **700× Earth's**.\n* **Atmosphere**: 95% CO₂, pressure only 0.6% of Earth's.\n* **Temperature**: Average −60°C (range −125°C to +20°C).\n* **Gravity**: 38% of Earth's — long-term health effects unknown.\n* **Communication delay**: 4–24 minutes one-way.\n\n**Current Missions**\n* **NASA Perseverance rover** (2021): Collecting rock samples and testing MOXIE (oxygen from CO₂).\n* **SpaceX Starship**: Designed to carry 100 people; crewed missions targeted **late 2020s**.\n* NASA's **Moon to Mars** programme aims for humans on Mars in the **2030s**.\n\n**Terraforming**: Would require centuries to millennia to make Mars Earth-like.\n\n[COSMIC_CARD: formula: Mars Surface Gravity | result: 38% of Earth (3.72 m/s²) | style: indigo]",
    "thinking": "- **Intent:** Mars colonisation feasibility and plans query.\n- **Parameters:** Environmental hazards, radiation levels, current mission timelines.",
    "priority": 10
  },
  {
    "id": "space-11-mars-the-red-planet",
    "domain": "space",
    "match": {
      "any": [
        "mars",
        "red planet"
      ]
    },
    "heading": "Mars: The Red Planet",
    "body": "Mars is the fourth planet from the Sun with an average distance of **142 million miles** ($228\\text{ million km}$) from it.\n\nIts red hue comes from iron oxide (rust) dust. A year on Mars lasts **687 Earth days** and its surface gravity is only **38% of Earth's**.\n\n[COSMIC_CARD: formula: Mars Gravity Ratio | result: 38% of Earth | style: indigo]",
    "thinking": "- **Intent:** Planet specific mechanics query (Mars).\n- **Data Points:** Surface rust oxidation chemistry, orbital timeline metrics.",
    "priority": 11
  },
  {
    "id": "space-12-earth-to-sun-orbit-distance",
    "domain": "space",
    "match": {
      "all": [
        "sun"
      ],
      "any": [
        "earth",
        "distance",
        "apart",
        "far"
      ]
    },
    "heading": "Earth-to-Sun Orbit Distance",
    "body": "The distance between the Earth and the Sun is not perfectly static because our orbit is elliptical. On average, the Earth is about **93 million miles** away from the Sun.\n\nThis distance is mathematically represented as **1 Astronomical Unit (AU)**. Sunlight, traveling at $186{,}282\\text{ miles per second}$, takes approximately **8 minutes and 20 seconds** to reach us.\n\n[COSMIC_CARD: formula: Average Earth-Sun Distance (1 AU) | result: 93,000,000 Miles | style: indigo]",
    "thinking": "- **Intent:** Astronomy constant query (Earth-Sun distance).\n- **Parameters:** Elliptical orbit variance, AU coordinate translation.\n- **Speed Integration:** Sunlight travel delta $\\approx 500\\text{ seconds}$.",
    "priority": 12
  },
  {
    "id": "space-13-earth-to-moon-orbit-distance",
    "domain": "space",
    "match": {
      "all": [
        "moon"
      ],
      "any": [
        "earth",
        "distance",
        "far",
        "apart"
      ]
    },
    "heading": "Earth-to-Moon Orbit Distance",
    "body": "Our natural satellite orbits the Earth in an elliptical path. Its average distance is **238,855 miles** ($384{,}400\\text{ km}$).\n\nAt perigee it is about $225{,}623\\text{ miles}$ away; at apogee $252{,}088\\text{ miles}$. This is roughly equivalent to wrapping 30 Earths in a row!\n\n[COSMIC_CARD: formula: Average Earth-Moon Distance | result: 238,855 Miles | style: indigo]",
    "thinking": "- **Intent:** Moon orbit constant query.\n- **Math Check:** Translating metric apogee/perigee scale limits to statute miles.",
    "priority": 13
  },
  {
    "id": "space-14-universal-speed-limit-c",
    "domain": "space",
    "match": {
      "any": [
        "speed of light"
      ]
    },
    "heading": "Universal Speed Limit (c)",
    "body": "According to Einstein's Theory of Special Relativity, the speed of light in a vacuum ($c$) is the absolute cosmic speed limit: **186,282 miles per second** ($299{,}792\\text{ km/s}$).\n\nAt this speed you could circle Earth's equator **7.5 times in a single second**!\n\n[COSMIC_CARD: formula: Speed of Light in Vacuum (c) | result: 186,282 mi/s | style: emerald]",
    "thinking": "- **Intent:** Universal constant query (c).\n- **Reference Framework:** Einstein's Special Relativity model boundaries.",
    "priority": 14
  },
  {
    "id": "space-15-scale-of-the-observable-universe",
    "domain": "space",
    "match": {
      "all": [
        "universe"
      ],
      "any": [
        "size",
        "big",
        "scale",
        "diameter"
      ]
    },
    "heading": "Scale of the Observable Universe",
    "body": "The observable universe is the spherical region of space visible from Earth. Its diameter is estimated at about **93 billion light-years**.\n\nAlthough the universe is only $13.8\\text{ billion years}$ old, space has expanded faster than the speed of light, stretching the observable edge far beyond $13.8\\text{ billion light-years}$.\n\n[COSMIC_CARD: formula: Observable Universe Diameter | result: 93,000,000,000 ly | style: indigo]",
    "thinking": "- **Intent:** Cosmological scale query.\n- **Cosmic Metric:** Big Bang timeline delta versus cosmological expansion speed ratio.",
    "priority": 15
  },
  {
    "id": "space-16-fundamental-constant-of-gravity",
    "domain": "space",
    "match": {
      "any": [
        "gravity",
        " g "
      ]
    },
    "heading": "Fundamental Constant of Gravity",
    "body": "Gravity is the attractive force that acts between all matter. On Earth's surface, the acceleration due to gravity is approximately **$9.81\\text{ m/s}^2$**.\n\nThe universal gravitational constant ($G$) is:\n\n$$G \\approx 6.674 \\times 10^{-11}\\text{ m}^3\\text{ kg}^{-1}\\text{ s}^{-2}$$\n\n[COSMIC_CARD: formula: Gravitational Acceleration (Earth) | result: 9.81 m/s² | style: indigo]",
    "thinking": "- **Intent:** Gravity mechanics query.\n- **Parameters:** Surface gravity $g$ versus Newtonian gravitational constant $G$.",
    "priority": 16
  },
  {
    "id": "earth-01-rarest-minerals-on-earth",
    "domain": "earth",
    "match": {
      "any": [
        "rarest",
        "rare"
      ]
    },
    "heading": "Rarest Minerals on Earth",
    "body": "The rarest minerals on Earth are dictated by precise geological compositions:\n\n1. **Kyawthuite**: The single rarest mineral in the world — only one specimen has ever been found, in Myanmar. It is an orange-hued bismuth-antimony oxide ($Bi^{3+}Sb^{5+}O_4$).\n2. **Painite**: A complex calcium zirconium borate ($CaZrBAl_9O_{18}$) with trace chromium impurities producing deep reddish-brown crystals.\n3. **Lonsdaleite**: A hexagonal carbon allotrope found in meteorites, theoretically 58% harder than diamond.\n\n[EARTH_CARD: topic: World's Rarest Specimen | value: Kyawthuite (1 Verified Crystal) | style: amber]",
    "thinking": "- **Intent:** Geologic mineral metrics (rarest rocks).\n- **Data Points:** Kyawthuite bismuth stoichiometry, Painite discovery parameters.",
    "priority": 1
  },
  {
    "id": "earth-02-petrological-foundations-rock-cycles",
    "domain": "earth",
    "match": {
      "any": [
        "rock",
        "stone",
        "mineral",
        "petrolog",
        "granite",
        "basalt",
        "sediment",
        "metamorph"
      ]
    },
    "heading": "Petrological Foundations & Rock Cycles",
    "body": "Rocks are the solid building blocks of Earth's crust, divided into three primary families:\n\n1. **Igneous Rocks**: Formed from cooling magma. *Intrusive* rocks like **Granite** cool slowly deep underground; *Extrusive* rocks like **Basalt** and **Obsidian** cool rapidly at the surface.\n2. **Sedimentary Rocks**: Formed by the compaction and cementation of particles over millions of years. Examples: **Limestone**, **Sandstone**, **Shale**.\n3. **Metamorphic Rocks**: Pre-existing rocks altered by extreme heat and pressure. **Marble** is metamorphosed limestone; **Slate** arises from shale.\n\n[EARTH_CARD: topic: Crustal Rock Cycle Interplay | value: Igneous, Sedimentary & Metamorphic | style: emerald]",
    "thinking": "- **Intent:** Petrologic classification query.\n- **Taxonomy:** Intrusive vs extrusive igneous, lithification of sediments, recrystallization.",
    "priority": 2
  },
  {
    "id": "earth-03-volcanological-magmatic-systems",
    "domain": "earth",
    "match": {
      "any": [
        "volcano",
        "lava",
        "magma",
        "caldera",
        "ring of fire"
      ]
    },
    "heading": "Volcanological & Magmatic Systems",
    "body": "Volcanoes are vents where molten magma escapes to the surface. Their explosiveness depends on silica content:\n\n* **Stratovolcanoes**: Tall, steep mountains formed from viscous, silica-rich lavas. They erupt violently with devastating **pyroclastic flows**.\n* **Shield Volcanoes**: Broad, low-profile structures formed by fluid basaltic lava. They erupt effusively without major explosions.\n* **Calderas**: Colossal bowl-shaped depressions formed when a magma chamber empties and the overlying peak collapses inward.\n\n[EARTH_CARD: topic: Maximum Volcanic Eruptive Scale | value: VEI-8 Caldera Supervolcanoes | style: rose]",
    "thinking": "- **Intent:** Volcanology structural query.\n- **Fluid Dynamics:** Viscosity vs silica ratio, composite stratovolcano gas pressure buildup.",
    "priority": 3
  },
  {
    "id": "earth-04-underwater-oceanic-geomorphology",
    "domain": "earth",
    "match": {
      "any": [
        "underwater",
        "trench",
        "mariana",
        "vent",
        "black smoker",
        "seafloor"
      ]
    },
    "heading": "Underwater Oceanic Geomorphology",
    "body": "The deep ocean floor is geologically active, driven by plate tectonics:\n\n* **Oceanic Trenches**: Where plates collide, the denser oceanic plate is forced into the mantle via **subduction**. The **Challenger Deep** in the Mariana Trench plunges to **36,070 feet (10,994 m)** — pressure of $1{,}086\\text{ bar}$.\n* **Hydrothermal Vents & Black Smokers**: Along divergent boundaries, superheated water exceeding **$400^\\circ\\text{C}$** vents into the ocean, depositing heavy metal chimneys called **Black Smokers**. These support ecosystems driven by **chemosynthesis**.\n\n[EARTH_CARD: topic: Challenger Deep Hydrostatic Pressure | value: 1,086 Bar / 15,750 PSI | style: sky]",
    "thinking": "- **Intent:** Oceanography and marine geology.\n- **Physical Limits:** Deep trench subduction physics, Mariana plate geometry.",
    "priority": 4
  },
  {
    "id": "science-01-quantum-mechanics-the-science-of-the-very-small",
    "domain": "science",
    "match": {
      "any": [
        "quantum",
        "planck",
        "boltzmann",
        "heisenberg",
        "wave function",
        "superposition",
        "entanglement"
      ]
    },
    "heading": "Quantum Mechanics: The Science of the Very Small",
    "body": "Quantum mechanics describes nature at the atomic and subatomic scale, where classical physics breaks down:\n\n**Core Principles**\n* **Wave-Particle Duality**: Every particle (electron, photon) exhibits both wave-like and particle-like behaviour depending on how it is observed.\n* **Heisenberg Uncertainty Principle**: It is impossible to simultaneously know both the exact position and momentum of a particle: $\\Delta x \\cdot \\Delta p \\geq \\hbar/2$.\n* **Superposition**: A quantum system can exist in multiple states at once until measured (Schrödinger's cat thought experiment).\n* **Quantum Entanglement**: Two particles can be correlated so that measuring one instantly determines the state of the other, regardless of distance.\n* **Planck Constant ($h$)**: $6.626 \\times 10^{-34}$ J·s — the fundamental quantum of action.\n\n**Applications**\n- Transistors and microchips (quantum tunnelling)\n- MRI scanners (nuclear spin states)\n- Lasers (stimulated emission of photons)\n- Quantum computing (qubits in superposition)\n\n[SCIENCE_CARD: topic: Planck Constant (h) | value: 6.626 × 10⁻³⁴ J·s | style: violet]",
    "thinking": "- **Intent:** Quantum physics telemetry query.\n- **Parameters:** Planck energy-frequency constants, uncertainty bounds, wave-particle duality.",
    "priority": 1
  },
  {
    "id": "science-02-the-standard-model-of-particle-physics",
    "domain": "science",
    "match": {
      "any": [
        "standard model",
        "particle physics",
        "quark",
        "lepton",
        "boson",
        "higgs",
        "fermion",
        "gluon"
      ]
    },
    "heading": "The Standard Model of Particle Physics",
    "body": "The Standard Model is the theory describing three of the four fundamental forces (electromagnetic, weak, strong) and classifying all known elementary particles:\n\n**Matter Particles (Fermions)**\n* **Quarks** (6 flavours): up, down, charm, strange, top, bottom — combine to form protons and neutrons.\n* **Leptons** (6 types): electron, muon, tau, and three corresponding neutrinos.\n\n**Force Carriers (Bosons)**\n* **Photon (γ)**: Carries the electromagnetic force.\n* **W⁺, W⁻, Z bosons**: Carry the weak nuclear force (responsible for radioactive decay).\n* **Gluons (8 types)**: Carry the strong nuclear force, binding quarks inside protons/neutrons.\n* **Higgs Boson**: Discovered at CERN in 2012 — gives other particles their mass via the Higgs field.\n\n**What it does NOT explain**\n- Gravity (no graviton confirmed)\n- Dark matter or dark energy\n- Why there is more matter than antimatter\n\n[SCIENCE_CARD: topic: Higgs Boson Discovery | value: CERN, July 4, 2012 | style: violet]",
    "thinking": "- **Intent:** Particle physics standard model lookup.\n- **Parameters:** Fermion/boson taxonomy, force carrier identification, Higgs mechanism.",
    "priority": 2
  },
  {
    "id": "science-03-crispr-cas9-precision-gene-editing",
    "domain": "science",
    "match": {
      "any": [
        "crispr",
        "gene editing",
        "gene edit",
        "cas9"
      ]
    },
    "heading": "CRISPR-Cas9: Precision Gene Editing",
    "body": "CRISPR (Clustered Regularly Interspaced Short Palindromic Repeats) is a revolutionary gene-editing technology derived from bacterial immune systems:\n\n**How it works**\n1. A **guide RNA (gRNA)** is designed to match a specific DNA sequence in the target genome.\n2. The gRNA binds to the **Cas9 enzyme**, directing it to the target location.\n3. Cas9 acts as **molecular scissors**, cutting both strands of DNA at the precise site.\n4. The cell's natural repair mechanisms either **disable** the gene (NHEJ) or **insert new DNA** (HDR).\n\n**Applications**\n* Treating genetic diseases: sickle cell disease (FDA approved 2023), beta-thalassemia\n* Cancer immunotherapy (CAR-T cell engineering)\n* Agricultural improvements (disease-resistant crops)\n* Basic research into gene function\n\n**Nobel Prize**: Jennifer Doudna and Emmanuelle Charpentier won the 2020 Nobel Prize in Chemistry for developing CRISPR-Cas9.\n\n[SCIENCE_CARD: topic: CRISPR Nobel Prize | value: Doudna & Charpentier, 2020 | style: fuchsia]",
    "thinking": "- **Intent:** Biotechnology gene editing query.\n- **Parameters:** CRISPR mechanism, Cas9 function, therapeutic applications.",
    "priority": 3
  },
  {
    "id": "science-04-nuclear-fission-vs-nuclear-fusion",
    "domain": "science",
    "match": {
      "any": [
        "fission",
        "fusion",
        "nuclear",
        "reactor",
        "uranium",
        "plutonium",
        "deuterium",
        "tritium"
      ]
    },
    "heading": "Nuclear Fission vs. Nuclear Fusion",
    "body": "Both fission and fusion release enormous energy via Einstein's **E = mc²**, but they work oppositely:\n\n**Nuclear Fission**\n* A heavy nucleus (Uranium-235 or Plutonium-239) is split into smaller nuclei by a neutron.\n* Releases ~200 MeV per reaction; chain reactions can be sustained in a reactor.\n* Powers all current nuclear power plants (~10% of world electricity).\n* Produces radioactive waste with half-lives of thousands of years.\n\n**Nuclear Fusion**\n* Light nuclei (Deuterium + Tritium) are forced together at extreme temperatures (>100 million °C) to form Helium.\n* Releases ~17.6 MeV per D-T reaction — weight-for-weight ~4× more energy than fission.\n* Fuel (hydrogen isotopes) is virtually unlimited; waste is non-radioactive Helium.\n* The challenge: sustaining a plasma hotter than the Sun's core.\n* ITER (France) is the world's largest fusion experiment — target first plasma ~2025.\n* NIF (USA) achieved **fusion ignition** in December 2022 — more energy out than laser energy in.\n\n[SCIENCE_CARD: topic: NIF Fusion Ignition | value: December 5, 2022 | style: amber]",
    "thinking": "- **Intent:** Nuclear physics comparison query.\n- **Parameters:** Fission chain reaction mechanics, fusion plasma confinement, energy yields.",
    "priority": 4
  },
  {
    "id": "science-05-the-speed-of-light-einstein-s-relativity",
    "domain": "science",
    "match": {
      "any": [
        "speed of light",
        "relativity",
        "special relativity",
        "general relativity",
        "e=mc",
        "time dilation",
        "length contraction"
      ]
    },
    "heading": "The Speed of Light & Einstein's Relativity",
    "body": "**The Speed of Light**\n* In a vacuum: **$c = 299{,}792{,}458$ m/s** (exactly, by definition)\n* Light travels from the Sun to Earth in ~**8 minutes 20 seconds**.\n* It circles Earth's equator **7.5 times per second**.\n\n**Special Relativity (1905)**\n* The laws of physics are identical for all observers in uniform motion.\n* The speed of light is the same for all observers regardless of their motion.\n* **Mass-Energy Equivalence**: $E = mc^2$ — a tiny mass converts to enormous energy.\n* **Time Dilation**: Moving clocks run slower — GPS satellites must correct for this effect.\n* **Length Contraction**: Objects moving at relativistic speeds appear shorter in the direction of travel.\n\n**General Relativity (1915)**\n* Gravity is not a force but the **curvature of spacetime** caused by mass and energy.\n* Predicts black holes, gravitational waves (confirmed 2015 by LIGO), and the expanding universe.\n* Light bends around massive objects — confirmed during the 1919 solar eclipse.\n\n[SCIENCE_CARD: topic: Speed of Light (c) | value: 299,792,458 m/s | style: emerald]",
    "thinking": "- **Intent:** Relativistic physics query.\n- **Parameters:** Special vs general relativity, time dilation, E=mc² derivation.",
    "priority": 5
  },
  {
    "id": "science-06-black-holes-event-horizons",
    "domain": "science",
    "match": {
      "any": [
        "black hole",
        "event horizon",
        "singularity",
        "hawking radiation",
        "spaghettification"
      ]
    },
    "heading": "Black Holes & Event Horizons",
    "body": "A **black hole** is a region of spacetime where gravity is so extreme that nothing — not even light — can escape.\n\n**Formation**\n* Stellar black holes form when a massive star (>20 solar masses) collapses at the end of its life in a **supernova**.\n* Supermassive black holes (millions–billions of solar masses) reside at the centre of most galaxies, including the Milky Way (**Sagittarius A***, 4 million solar masses).\n\n**Key Concepts**\n* **Event Horizon**: The point of no return — the boundary beyond which escape velocity exceeds $c$.\n* **Singularity**: The mathematical point at the centre of infinite density where known physics breaks down.\n* **Hawking Radiation**: Stephen Hawking (1974) theorised that black holes slowly emit thermal radiation due to quantum effects near the event horizon, causing them to evaporate over trillions of years.\n* **Spaghettification**: Tidal forces near a black hole stretch infalling objects into long thin strands.\n\n**Observations**\n* First image: M87* black hole captured by the Event Horizon Telescope in **April 2019**.\n* Second image: Sagittarius A* imaged in **May 2022**.\n* Gravitational waves from black hole mergers detected by LIGO since **2015**.\n\n[SCIENCE_CARD: topic: First Black Hole Image | value: M87*, Event Horizon Telescope 2019 | style: violet]",
    "thinking": "- **Intent:** Astrophysics black hole query.\n- **Parameters:** Event horizon mechanics, Hawking radiation, observational milestones.",
    "priority": 6
  },
  {
    "id": "science-07-string-theory-an-overview",
    "domain": "science",
    "match": {
      "any": [
        "string theory",
        "m-theory",
        "extra dimension",
        "brane",
        "superstring"
      ]
    },
    "heading": "String Theory: An Overview",
    "body": "**String theory** is a theoretical framework proposing that the fundamental constituents of nature are not point-like particles but tiny one-dimensional **vibrating strings** of energy.\n\n**Core Ideas**\n* Different **vibrational modes** of a string correspond to different particles (electrons, quarks, photons, gravitons).\n* Requires **10 dimensions** (superstring theory) or **11 dimensions** (M-theory) — extra dimensions are compactified at the Planck scale (~$10^{-35}$ m).\n* Naturally incorporates **gravity** alongside quantum mechanics — something the Standard Model cannot do.\n\n**Variants**\n* Five consistent superstring theories were unified by **M-theory** (Edward Witten, 1995).\n* **Branes** (membranes) are higher-dimensional objects in M-theory; our universe may be a 3-brane.\n\n**Status**\n* No direct experimental evidence exists yet — predictions require energies far beyond current accelerators.\n* Remains a leading candidate for a **Theory of Everything** but is not yet a falsifiable scientific theory.\n* Alternative approaches include Loop Quantum Gravity (LQG).\n\n[SCIENCE_CARD: topic: String Theory Dimensions | value: 10 (superstring) / 11 (M-theory) | style: violet]",
    "thinking": "- **Intent:** Theoretical physics string theory query.\n- **Parameters:** Vibrational modes, extra dimensions, M-theory unification.",
    "priority": 7
  },
  {
    "id": "science-08-climate-science-the-greenhouse-effect-carbon-cyc",
    "domain": "science",
    "match": {
      "any": [
        "greenhouse",
        "carbon cycle",
        "climate",
        "global warming",
        "co2",
        "atmosphere",
        "ozone"
      ]
    },
    "heading": "Climate Science: The Greenhouse Effect & Carbon Cycle",
    "body": "**The Greenhouse Effect**\n* Solar radiation passes through Earth's atmosphere and warms the surface.\n* Earth re-emits heat as **infrared radiation** (longer wavelengths).\n* **Greenhouse gases** (CO₂, CH₄, N₂O, H₂O vapour) absorb and re-emit this infrared radiation, warming the atmosphere.\n* Without any greenhouse effect Earth's average temperature would be ~**−18°C** instead of +15°C.\n* **Enhanced greenhouse effect**: Human emissions amplify this warming — CO₂ has risen from 280 ppm (pre-industrial) to over **420 ppm** (2024).\n\n**The Carbon Cycle**\n* **Photosynthesis**: Plants absorb CO₂ and release O₂.\n* **Respiration & Decomposition**: Organisms release CO₂ back.\n* **Ocean absorption**: Oceans absorb ~25–30% of human CO₂ emissions (causing ocean acidification).\n* **Fossil fuel burning**: Returns carbon buried millions of years ago back to the atmosphere in decades.\n\n**Key facts**\n- Global average temperature has risen ~**1.2°C** since pre-industrial times.\n- The Paris Agreement (2015) targets limiting warming to **1.5–2°C**.\n- Arctic is warming ~4× faster than the global average.\n\n[SCIENCE_CARD: topic: Atmospheric CO₂ (2024) | value: >420 ppm | style: emerald]",
    "thinking": "- **Intent:** Climate science query.\n- **Parameters:** Greenhouse gas mechanisms, carbon cycle flows, anthropogenic warming data.",
    "priority": 8
  },
  {
    "id": "science-09-human-genetics-inheritance-chromosomes",
    "domain": "science",
    "match": {
      "any": [
        "dominant",
        "recessive",
        "chromosome",
        "allele",
        "mendel",
        "genetics",
        "heredity",
        "trait",
        "genotype",
        "phenotype"
      ]
    },
    "heading": "Human Genetics: Inheritance & Chromosomes",
    "body": "**Chromosomes**\n* Humans have **46 chromosomes** in 23 pairs in every somatic cell.\n* Pair 23 determines biological sex: **XX** (female) or **XY** (male).\n* Each chromosome contains thousands of **genes** — segments of DNA encoding proteins.\n\n**Mendelian Inheritance**\n* **Dominant alleles** (written uppercase, e.g. **A**): expressed even when only one copy is present.\n* **Recessive alleles** (lowercase, e.g. **a**): expressed only when two copies are inherited (homozygous).\n* **Genotype** = actual allele combination (AA, Aa, aa); **Phenotype** = observable trait.\n\n| Genotype | Phenotype (if A is dominant) |\n|----------|-----------------------------|\n| AA       | Dominant trait              |\n| Aa       | Dominant trait (carrier)    |\n| aa       | Recessive trait             |\n\n**Inheritance Patterns**\n* **Autosomal dominant** (e.g., Huntington's disease): one copy causes disease.\n* **Autosomal recessive** (e.g., cystic fibrosis): two copies needed.\n* **X-linked recessive** (e.g., haemophilia): more common in males (only one X chromosome).\n* **Codominance** (e.g., ABO blood types): both alleles expressed simultaneously.\n\n[SCIENCE_CARD: topic: Human Chromosome Count | value: 46 (23 pairs) | style: fuchsia]",
    "thinking": "- **Intent:** Mendelian genetics and chromosome query.\n- **Parameters:** Dominant/recessive allele mechanics, inheritance patterns, chromosome structure.",
    "priority": 9
  },
  {
    "id": "science-10-neuroscience-neurons-synapses-brain-waves",
    "domain": "science",
    "match": {
      "any": [
        "neuron",
        "synapse",
        "brain wave",
        "neuroscience",
        "action potential",
        "dendrite",
        "axon",
        "neurotransmitter"
      ]
    },
    "heading": "Neuroscience: Neurons, Synapses & Brain Waves",
    "body": "The brain is a network of ~**86 billion neurons** communicating via electrical and chemical signals.\n\n**Neuron Structure**\n* **Cell body (soma)**: Contains the nucleus and metabolic machinery.\n* **Dendrites**: Tree-like extensions that receive incoming signals from other neurons.\n* **Axon**: Long fibre that transmits electrical impulses (action potentials) away from the cell body.\n* **Myelin sheath**: Fatty insulation that speeds up signal transmission up to 120 m/s.\n\n**Synaptic Transmission**\n1. An **action potential** travels down the axon (all-or-nothing electrical spike, ~+40 mV).\n2. Triggers release of **neurotransmitters** from vesicles into the **synaptic cleft**.\n3. Neurotransmitters bind to **receptors** on the postsynaptic neuron, causing excitation or inhibition.\n4. Key neurotransmitters: **Dopamine** (reward), **Serotonin** (mood), **GABA** (inhibition), **Glutamate** (excitation), **Acetylcholine** (muscle control, memory).\n\n**Brain Waves (EEG)**\n| Wave | Frequency | State |\n|------|-----------|-------|\n| Delta (δ) | 0.5–4 Hz | Deep sleep |\n| Theta (θ) | 4–8 Hz | Drowsiness, creativity |\n| Alpha (α) | 8–12 Hz | Relaxed wakefulness |\n| Beta (β) | 12–30 Hz | Active thinking |\n| Gamma (γ) | 30–100 Hz | High-level cognition |\n\n[SCIENCE_CARD: topic: Neurons in Human Brain | value: ~86 billion | style: violet]",
    "thinking": "- **Intent:** Neuroscience and brain function query.\n- **Parameters:** Neuron anatomy, synaptic transmission, EEG brain wave frequencies.",
    "priority": 10
  },
  {
    "id": "science-11-molecular-chemistry-electronegativity-scales",
    "domain": "science",
    "match": {
      "any": [
        "chemistry",
        "element",
        "carbon",
        "noble",
        "electroneg"
      ]
    },
    "heading": "Molecular Chemistry & Electronegativity Scales",
    "body": "Chemical interactions are governed by electron configurations and atomic properties:\n\n* **Carbon Allotropes**: **Diamond** forms a rigid tetrahedral 3D lattice making it exceptionally hard. **Graphite** forms stacked planar hexagonal sheets that slide easily.\n* **Electronegativity (Pauling Scale)**: Measures an atom's tendency to attract shared electrons. Fluorine is the most electronegative; Francium is the least.\n* **Noble Gases**: Group 18 elements with completely filled valence shells — exceptionally stable and chemically inert under standard conditions.\n\n[SCIENCE_CARD: topic: Pauling Electronegativity: Fluorine | value: 3.98 (Maximum Scale) | style: amber]",
    "thinking": "- **Intent:** Chemistry element metrics.\n- **Parameters:** Carbon bonding geometries, Pauling electronegativity scales.",
    "priority": 11
  },
  {
    "id": "science-12-genetics-dna-base-pairing-transcription",
    "domain": "science",
    "match": {
      "any": [
        "dna",
        "gene",
        "cell",
        "transcription",
        "biology"
      ]
    },
    "heading": "Genetics, DNA Base-Pairing & Transcription",
    "body": "Biological life is coordinated at the molecular level inside cell nuclei:\n\n* **Double Helix & Hydrogen Bonding**: DNA consists of two complementary chains. Adenine (A) pairs with Thymine (T) via **two hydrogen bonds**; Cytosine (C) pairs with Guanine (G) via **three hydrogen bonds** — making CG pairs stronger.\n* **Transcription & Translation**: RNA polymerase copies a DNA segment into mRNA. The ribosome then decodes this mRNA to assemble amino acid polypeptide chains (proteins).\n\n[SCIENCE_CARD: topic: CG Base-Pair Stability | value: 3 Hydrogen Bonds (Tighter Bind) | style: fuchsia]",
    "thinking": "- **Intent:** Molecular genetics transcription query.\n- **Parameters:** Hydrogen bonding differences between nucleic base pairings.",
    "priority": 12
  },
  {
    "id": "science-13-pure-mathematical-limits-irrational-constants",
    "domain": "science",
    "match": {
      "any": [
        "math",
        "constant",
        "golden ratio",
        "phi",
        "euler"
      ]
    },
    "heading": "Pure Mathematical Limits & Irrational Constants",
    "body": "Mathematics uses unique irrational constants to map natural proportions and limit scales:\n\n* **The Golden Ratio ($\\phi$)**: The limit ratio of consecutive Fibonacci numbers, appearing in biological geometry and spiral galaxy curves.\n$$\\phi = \\frac{1 + \\sqrt{5}}{2} \\approx 1.6180339887...$$\n* **Euler-Mascheroni Constant ($\\gamma$)**: The limiting delta between the harmonic series and the natural logarithm — core to advanced number theory.\n\n[SCIENCE_CARD: topic: The Golden Ratio (Phi) | value: 1.6180339887... | style: emerald]",
    "thinking": "- **Intent:** Pure mathematical constants lookup.\n- **Parameters:** Golden ratio algebra derivations, Euler limits.",
    "priority": 13
  },
  {
    "id": "history-01-ancient-egypt-pharaohs-pyramids-hieroglyphics",
    "domain": "history",
    "match": {
      "any": [
        "egypt",
        "pharaoh",
        "pyramid",
        "hieroglyph",
        "sphinx",
        "nile",
        "ramesses",
        "cleopatra",
        "tutankhamun"
      ]
    },
    "heading": "Ancient Egypt: Pharaohs, Pyramids & Hieroglyphics",
    "body": "Ancient Egypt was one of the world's longest-lasting civilisations, spanning ~**3,000 years** (c. 3100–30 BC):\n\n**The Pharaohs**\n* The pharaoh was considered a living god — both supreme ruler and high priest.\n* **Ramesses II (the Great)** (reigned 1279–1213 BC): Egypt's most celebrated pharaoh, known for the Battle of Kadesh and the Abu Simbel temples.\n* **Tutankhamun** (reigned 1332–1323 BC): The 'boy king' whose largely intact tomb was discovered by Howard Carter in **1922**.\n* **Cleopatra VII** (reigned 51–30 BC): The last active pharaoh, fluent in nine languages; her death ended the Ptolemaic dynasty and Egyptian independence.\n\n**The Pyramids**\n* Built as royal tombs during the **Old Kingdom** (c. 2686–2181 BC).\n* **Great Pyramid of Giza** (c. 2560 BC): Built for Pharaoh Khufu — **146.5 m** tall (originally), constructed with ~**2.3 million stone blocks** averaging 2.5–15 tonnes each.\n* Remained the world's tallest human-made structure for **3,800 years**.\n* Three pyramids at Giza: Khufu, Khafre, Menkaure, with the Great Sphinx guarding the complex.\n\n**Hieroglyphics**\n* A writing system combining logographic and alphabetic elements — over **700 distinct signs**.\n* Used for ~3,500 years (c. 3200 BC – 400 AD).\n* **Rosetta Stone** (196 BC, discovered 1799): Decree written in hieroglyphics, Demotic, and Ancient Greek — allowed Jean-François Champollion to decode hieroglyphics in **1822**.\n\n[HISTORY_CARD: topic: Great Pyramid of Giza | value: Built c. 2560 BC, 146.5 m tall | style: amber]",
    "thinking": "- **Intent:** Ancient Egyptian civilisation query.\n- **Context:** Pharaonic rule, pyramid construction, hieroglyphic writing system.",
    "priority": 1
  },
  {
    "id": "history-02-the-roman-empire-rise-and-fall",
    "domain": "history",
    "match": {
      "any": [
        "roman empire",
        "rome",
        "julius caesar",
        "augustus",
        "gladiator",
        "colosseum",
        "byzantine"
      ]
    },
    "heading": "The Roman Empire: Rise and Fall",
    "body": "The Roman Empire was the most powerful state in the ancient world, lasting from **27 BC to 476 AD** (Western) / **1453 AD** (Eastern/Byzantine):\n\n**Rise of Rome**\n* Rome was a republic from **509 BC** before Julius Caesar's dictatorship destabilised it.\n* **Julius Caesar** (100–44 BC): Conquered Gaul (58–50 BC), crossed the Rubicon, became dictator perpetuo, and was assassinated on the Ides of March (March 15, 44 BC).\n* **Augustus** (27 BC – 14 AD): First Emperor — turned the republic into an empire. The **Pax Romana** (27 BC – 180 AD) was 200 years of relative peace and prosperity.\n\n**At its Peak**\n* At its greatest extent under **Trajan** (117 AD): ~**5 million km²**, ~**70 million people** (20% of the world's population).\n* Iconic engineering: aqueducts (14 in Rome alone), roads (400,000 km of roads), the Colosseum (72 AD, held 50,000–80,000 spectators).\n\n**Fall of the Western Empire**\n* Causes: overextension, economic strain, political instability, barbarian invasions, and the split of the empire.\n* **476 AD**: Last Western emperor **Romulus Augustulus** deposed by Odoacer — traditional end date of the Western Roman Empire.\n\n**Eastern Empire (Byzantine)**\n* Continued for another **1,000 years** until **Constantinople** fell to the Ottoman Turks in **1453**.\n\n[HISTORY_CARD: topic: Roman Empire Peak Extent | value: ~5 million km² under Trajan (117 AD) | style: rose]",
    "thinking": "- **Intent:** Roman Empire history query.\n- **Context:** Republic to empire transition, Pax Romana, causes of decline.",
    "priority": 2
  },
  {
    "id": "history-03-the-renaissance-c-1300-1600",
    "domain": "history",
    "match": {
      "any": [
        "renaissance",
        "da vinci",
        "michelangelo",
        "raphael",
        "humanism",
        "botticelli",
        "medici"
      ]
    },
    "heading": "The Renaissance (c. 1300–1600)",
    "body": "The **Renaissance** ('Rebirth') was a transformative cultural movement that began in Italy and spread across Europe, marking the transition from the Middle Ages to modernity:\n\n**Origins**\n* Began in **Florence, Italy** in the 14th century, fuelled by wealthy merchant patrons like the **Medici family**.\n* Greek and Roman classical texts were rediscovered — partly via Arab scholars — inspiring a revival of ancient learning.\n* **Humanism**: Philosophical focus on human potential, reason, and earthly life rather than solely religious doctrine.\n\n**Key Figures**\n* **Leonardo da Vinci** (1452–1519): Painter (*Mona Lisa*, *The Last Supper*), sculptor, anatomist, engineer, and inventor — the archetypal 'Renaissance man'.\n* **Michelangelo** (1475–1564): Sculptor (*David*, *Pietà*), painted the Sistine Chapel ceiling (1508–1512).\n* **Raphael** (1483–1520): *The School of Athens* — depicting Plato, Aristotle, and other classical thinkers.\n* **Galileo Galilei** (1564–1642): Confirmed heliocentrism, pioneered the scientific method.\n\n**Impact**\n* Art used **linear perspective** (Brunelleschi, 1415) to create realistic depth.\n* The printing press (Gutenberg, ~1440) spread Renaissance ideas across Europe.\n* Led directly to the **Scientific Revolution** and the **Protestant Reformation** (Luther, 1517).\n\n[HISTORY_CARD: topic: Sistine Chapel Ceiling | value: Michelangelo, 1508–1512 | style: amber]",
    "thinking": "- **Intent:** Renaissance history query.\n- **Context:** Italian origins, humanist philosophy, artistic innovations, key figures.",
    "priority": 3
  },
  {
    "id": "history-04-the-scientific-revolution-c-1543-1687",
    "domain": "history",
    "match": {
      "any": [
        "scientific revolution",
        "copernicus",
        "galileo",
        "kepler",
        "newton",
        "descartes",
        "bacon"
      ]
    },
    "heading": "The Scientific Revolution (c. 1543–1687)",
    "body": "The **Scientific Revolution** transformed humanity's understanding of nature, establishing modern science as a discipline based on observation, experiment, and mathematics:\n\n**Key Milestones**\n* **1543**: **Nicolaus Copernicus** publishes *De revolutionibus* — proposes a **heliocentric** (Sun-centred) model of the solar system, overturning 1,400 years of Ptolemaic Earth-centred astronomy.\n* **1609–1619**: **Johannes Kepler** publishes his three laws of planetary motion — planets move in **ellipses**, not circles.\n* **1610**: **Galileo Galilei** observes Jupiter's moons with a telescope, confirming objects can orbit bodies other than Earth. Later placed under house arrest by the Inquisition.\n* **1628**: **William Harvey** describes the **circulation of blood** — overturning 1,400-year-old Galenic medicine.\n* **1687**: **Isaac Newton** publishes *Principia Mathematica* — Laws of Motion and Universal Gravitation, unifying terrestrial and celestial mechanics.\n\n**The Scientific Method**\n* **Francis Bacon** (1620) championed empirical induction — knowledge from experiment, not authority.\n* **René Descartes** introduced systematic doubt and mathematical modelling of nature.\n\n**Legacy**\n* Undermined the authority of the Church in explaining the natural world.\n* Laid foundations for the **Enlightenment**, the **Industrial Revolution**, and all modern science.\n\n[HISTORY_CARD: topic: Newton's Principia Mathematica | value: Published 1687 | style: sky]",
    "thinking": "- **Intent:** Scientific Revolution history query.\n- **Context:** Copernican revolution, Kepler's laws, Galileo, Newton's synthesis.",
    "priority": 4
  },
  {
    "id": "history-05-the-age-of-exploration-c-1400-1600",
    "domain": "history",
    "match": {
      "any": [
        "age of exploration",
        "columbus",
        "magellan",
        "vasco da gama",
        "exploration",
        "new world",
        "conquistador"
      ]
    },
    "heading": "The Age of Exploration (c. 1400–1600)",
    "body": "The **Age of Exploration** was a period of European global maritime exploration that permanently connected the world's continents:\n\n**Why it Happened**\n* European powers sought direct sea routes to Asia for spices and silk, bypassing Ottoman-controlled overland routes.\n* Advances in navigation: the **compass**, **astrolabe**, and **caravel** ships enabled deep-ocean voyaging.\n\n**Key Voyages**\n* **1488**: **Bartolomeu Dias** (Portugal) rounds the Cape of Good Hope — first European to do so.\n* **1492**: **Christopher Columbus** reaches the Caribbean (believing it to be Asia) — opens the Americas to European contact.\n* **1497–1498**: **Vasco da Gama** sails from Portugal to India, establishing the sea route that would dominate trade for centuries.\n* **1519–1522**: **Ferdinand Magellan**'s expedition (completed by Elcano) becomes the first to **circumnavigate the globe**.\n* **1519–1521**: **Hernán Cortés** conquers the Aztec Empire; **Francisco Pizarro** conquers the Inca Empire (1532).\n\n**The Columbian Exchange**\n* The transfer of plants, animals, diseases, and people between the Old and New Worlds.\n* **Crops from Americas to Europe**: potatoes, tomatoes, maize, cacao, tobacco.\n* **Diseases from Europe to Americas**: smallpox, measles — killed up to **90%** of indigenous populations.\n\n[HISTORY_CARD: topic: Columbus's First Voyage | value: August–October 1492 | style: amber]",
    "thinking": "- **Intent:** Age of Exploration history query.\n- **Context:** Navigation technology, key voyages, the Columbian Exchange and its consequences.",
    "priority": 5
  },
  {
    "id": "history-06-the-cold-war-1947-1991",
    "domain": "history",
    "match": {
      "any": [
        "cold war",
        "soviet union",
        "ussr",
        "nato",
        "berlin wall",
        "cuban missile",
        "iron curtain",
        "communism",
        "containment"
      ]
    },
    "heading": "The Cold War (1947–1991)",
    "body": "The **Cold War** was a geopolitical rivalry between the **United States** and the **Soviet Union** (USSR), fought through proxy wars, arms races, and ideological competition — never direct military conflict between the two superpowers:\n\n**Origins**\n* After WWII, the US and USSR emerged as rival superpowers with incompatible ideologies: **liberal democracy/capitalism** vs. **communist totalitarianism**.\n* Winston Churchill's **'Iron Curtain' speech** (1946) defined the division of Europe.\n* **Truman Doctrine** (1947): US pledged to contain the spread of communism globally.\n\n**Key Events**\n* **1949**: USSR tests its first atomic bomb; China becomes communist.\n* **1950–1953**: Korean War — first major proxy conflict.\n* **1957**: USSR launches **Sputnik** — sparks the Space Race.\n* **1961**: **Berlin Wall** built, dividing East and West Germany.\n* **1962**: **Cuban Missile Crisis** — 13 days in October brought the world closest to nuclear war. Ended when USSR withdrew missiles from Cuba.\n* **1965–1975**: Vietnam War — US-backed South Vietnam vs. communist North Vietnam.\n* **1979–1989**: Soviet-Afghan War — USSR's 'Vietnam'.\n\n**End of the Cold War**\n* **Mikhail Gorbachev**'s reforms (glasnost and perestroika) loosened Soviet control.\n* **Berlin Wall falls**: November 9, **1989**.\n* **USSR dissolves**: December 25, **1991** — 15 independent states formed.\n\n[HISTORY_CARD: topic: Cuban Missile Crisis | value: October 16–28, 1962 | style: rose]",
    "thinking": "- **Intent:** Cold War history query.\n- **Context:** US-USSR ideological rivalry, key crises, arms race, eventual dissolution.",
    "priority": 6
  },
  {
    "id": "history-07-the-space-race-from-sputnik-to-apollo-11",
    "domain": "history",
    "match": {
      "any": [
        "space race",
        "sputnik",
        "apollo",
        "apollo 11",
        "moon landing",
        "yuri gagarin",
        "neil armstrong",
        "nasa"
      ]
    },
    "heading": "The Space Race: From Sputnik to Apollo 11",
    "body": "The **Space Race** (1957–1969) was a Cold War competition between the USA and USSR to achieve supremacy in spaceflight:\n\n**Early Soviet Leads**\n* **October 4, 1957**: USSR launches **Sputnik 1** — Earth's first artificial satellite. A beach-ball-sized sphere beeping from orbit shocked the West.\n* **November 3, 1957**: **Sputnik 2** carries **Laika** — first animal in orbit.\n* **April 12, 1961**: **Yuri Gagarin** (USSR) completes the first human spaceflight — a 108-minute orbit aboard **Vostok 1**.\n\n**America Responds**\n* **May 5, 1961**: **Alan Shepard** becomes the first American in space (15-minute suborbital flight).\n* **May 25, 1961**: President Kennedy commits to landing a man on the Moon before the decade's end.\n* **February 20, 1962**: **John Glenn** — first American to orbit Earth.\n\n**Apollo 11: The Moon Landing**\n* **July 16, 1969**: Launch from Kennedy Space Center, Florida.\n* **July 20, 1969 at 20:17 UTC**: **Neil Armstrong** and **Buzz Aldrin** land the Lunar Module *Eagle* in the Sea of Tranquility.\n* **20:56 UTC**: Armstrong steps onto the Moon — *'That's one small step for [a] man, one giant leap for mankind.'*\n* **Michael Collins** orbited above in the Command Module.\n* They collected **21.5 kg** of lunar rock samples and planted a US flag.\n* Total Apollo programme: **12 astronauts** walked on the Moon across **6 successful landings** (Apollo 11, 12, 14, 15, 16, 17).\n\n**Legacy**: Demonstrated that human ingenuity could achieve seemingly impossible goals; drove advances in computing, materials science, and telecommunications.\n\n[HISTORY_CARD: topic: Apollo 11 Moon Landing | value: July 20, 1969, 20:17 UTC | style: indigo]",
    "thinking": "- **Intent:** Space Race history query.\n- **Context:** Cold War context, Sputnik shock, Apollo 11 mission details.",
    "priority": 7
  },
  {
    "id": "history-08-the-invention-of-the-internet",
    "domain": "history",
    "match": {
      "any": [
        "internet",
        "arpanet",
        "world wide web",
        "www",
        "tim berners-lee",
        "tcp/ip"
      ]
    },
    "heading": "The Invention of the Internet",
    "body": "The Internet evolved over decades from a military research network to a global communication system:\n\n**ARPANET (1969)**\n* Funded by the US Department of Defense's ARPA (Advanced Research Projects Agency).\n* **October 29, 1969**: First message sent between UCLA and Stanford — only 'LO' (the system crashed before completing 'LOGIN').\n* Designed to survive nuclear attack by routing data through multiple paths.\n\n**TCP/IP Protocol (1983)**\n* **Vint Cerf** and **Bob Kahn** designed **TCP/IP** (Transmission Control Protocol/Internet Protocol) — the common language allowing different networks to interconnect.\n* January 1, 1983: ARPANET switched to TCP/IP — often called the internet's official birthday.\n\n**The World Wide Web (1991)**\n* **Tim Berners-Lee** (CERN) invented the **WWW** in 1989, publishing the first website on **August 6, 1991**.\n* The Web uses **HTTP**, **HTML**, and **URLs** — a layer running on top of the Internet.\n* **Mosaic** (1993): First graphical web browser — made the web accessible to ordinary people.\n\n**Growth**\n* **1995**: ~16 million users worldwide.\n* **2024**: ~**5.4 billion** users (67% of the global population).\n* Transformed commerce, communication, entertainment, science, and politics.\n\n[HISTORY_CARD: topic: First Website | value: Tim Berners-Lee, August 6, 1991 | style: sky]",
    "thinking": "- **Intent:** Internet history and invention query.\n- **Context:** ARPANET origins, TCP/IP standardisation, WWW invention by Berners-Lee.",
    "priority": 8
  },
  {
    "id": "history-09-the-manhattan-project-1942-1946",
    "domain": "history",
    "match": {
      "any": [
        "manhattan project",
        "atomic bomb",
        "nuclear bomb",
        "hiroshima",
        "nagasaki",
        "oppenheimer"
      ]
    },
    "heading": "The Manhattan Project (1942–1946)",
    "body": "The **Manhattan Project** was the US-led wartime programme to develop the world's first nuclear weapons:\n\n**Origins**\n* Driven by fear that Nazi Germany was developing its own atomic bomb.\n* **Einstein-Szilard Letter** (August 2, 1939): Einstein warned President Roosevelt that uranium chain reactions could produce enormously powerful bombs.\n* Formally launched **December 1941**, following the Pearl Harbor attack.\n\n**Scale & Secrecy**\n* Employed over **130,000 people** at peak; costed ~**$2 billion** ($27 billion today).\n* Sites included Los Alamos (NM), Oak Ridge (TN), and Hanford (WA) — most workers didn't know what they were building.\n* **J. Robert Oppenheimer** directed the Los Alamos Laboratory and the bomb's design.\n\n**The Trinity Test**\n* **July 16, 1945**: First nuclear detonation at Jornada del Muerto desert, New Mexico — a plutonium implosion device ('Gadget') with ~21 kilotons yield.\n* Oppenheimer recalled the Bhagavad Gita: *'Now I am become Death, the destroyer of worlds.'*\n\n**Hiroshima & Nagasaki**\n* **August 6, 1945**: 'Little Boy' (uranium bomb) dropped on **Hiroshima** — ~70,000 killed immediately, ~140,000 by year's end.\n* **August 9, 1945**: 'Fat Man' (plutonium bomb) dropped on **Nagasaki** — ~40,000 killed immediately.\n* Japan surrendered **August 15, 1945** — ending WWII.\n\n**Legacy**: Began the nuclear age, the Cold War arms race, and ongoing debates about nuclear deterrence and disarmament.\n\n[HISTORY_CARD: topic: Trinity Test | value: July 16, 1945 — First Nuclear Detonation | style: rose]",
    "thinking": "- **Intent:** Manhattan Project history query.\n- **Context:** WWII context, project scale, Trinity test, Hiroshima and Nagasaki.",
    "priority": 9
  },
  {
    "id": "history-10-the-printing-press-its-impact-c-1440",
    "domain": "history",
    "match": {
      "any": [
        "printing press",
        "gutenberg",
        "movable type",
        "printing"
      ]
    },
    "heading": "The Printing Press & Its Impact (c. 1440)",
    "body": "**Johannes Gutenberg**'s movable-type printing press (~1440) was arguably the most transformative invention in the history of communication:\n\n**The Invention**\n* Gutenberg combined:\n  - **Movable metal type** (individual reusable letter blocks)\n  - **Oil-based ink** (durable, consistent)\n  - An adapted **wine/olive press** mechanism\n* **Gutenberg Bible** (c. 1455): The first major book printed in Europe using this technology — ~180 copies printed.\n\n**Before the Press**\n* Books were hand-copied by monks — a Bible took ~1–2 years to produce.\n* Only wealthy institutions could afford books; literacy was rare.\n\n**Immediate Impact**\n* Printing speed: A press could produce **3,600 pages per day** vs. ~4 pages hand-copied.\n* By 1500, over **20 million books** had been printed across Europe.\n* Cost of books dropped dramatically — knowledge became accessible to ordinary people.\n\n**Long-Term Consequences**\n* **Protestant Reformation** (1517): Martin Luther's 95 Theses spread rapidly in print, challenging the Catholic Church's monopoly on religious interpretation.\n* **Scientific Revolution**: Researchers could share and build on each other's work universally.\n* **Rise of literacy**: Growing demand for books drove mass education.\n* **Standardisation of languages**: Printed books helped standardise national languages.\n* Some historians argue it was the most significant catalyst for the **modern world**.\n\n[HISTORY_CARD: topic: Gutenberg's Printing Press | value: c. 1440, Mainz, Germany | style: amber]",
    "thinking": "- **Intent:** Printing press historical impact query.\n- **Context:** Gutenberg's mechanism, Reformation, Scientific Revolution, spread of literacy.",
    "priority": 10
  },
  {
    "id": "history-11-george-washington-the-founding-era-1789-1797",
    "domain": "history",
    "match": {
      "any": [
        "washington",
        "founding",
        "hamilton",
        "jefferson"
      ]
    },
    "heading": "George Washington & The Founding Era (1789–1797)",
    "body": "As the first President, **George Washington** established crucial precedents:\n\n* **The Cabinet Concept**: He structured the first formal cabinet — Alexander Hamilton (Treasury, Federalist vision) versus Thomas Jefferson (State, agrarian decentralization).\n* **Foreign Policy Neutrality**: Issued the Proclamation of Neutrality in 1793, keeping the young republic out of European conflicts.\n* **The Two-Term Tradition**: By voluntarily stepping down in 1797 he established a voluntary executive limit later codified by the **22nd Amendment**.\n\n[HISTORY_CARD: topic: Washington's Presidential Tenure | value: 1789 – 1797 (2 Terms) | style: amber]",
    "thinking": "- **Intent:** Early executive history lookup.\n- **Context:** Federalist vs. Democratic-Republican cabinet dynamics.",
    "priority": 11
  },
  {
    "id": "history-12-abraham-lincoln-the-constitutional-crisis-1861-1",
    "domain": "history",
    "match": {
      "any": [
        "lincoln",
        "civil war",
        "gettysburg",
        "emancipation"
      ]
    },
    "heading": "Abraham Lincoln & The Constitutional Crisis (1861–1865)",
    "body": "Presiding over the nation's most profound crisis, **Abraham Lincoln** preserved the Union:\n\n* **Preservation of the Union**: Maintained that secession was legally void and led federal efforts through the Civil War.\n* **The Emancipation Proclamation**: Issued January 1, 1863 — declared all enslaved people in Confederate territories forever free, shifting the war's moral focus.\n* **Gettysburg Address**: Redefined the war as a 'new birth of freedom' ensuring government 'of the people, by the people, for the people, shall not perish from the earth.'\n\n[HISTORY_CARD: topic: Lincoln's Core Milestone | value: Emancipation Proclamation (1863) | style: rose]",
    "thinking": "- **Intent:** Civil War presidency and Lincoln legacy analysis.\n- **Significance:** Wartime executive powers expansion.",
    "priority": 12
  },
  {
    "id": "history-13-franklin-d-roosevelt-the-great-transformation-19",
    "domain": "history",
    "match": {
      "any": [
        "fdr",
        "roosevelt",
        "new deal",
        "depression"
      ]
    },
    "heading": "Franklin D. Roosevelt & The Great Transformation (1933–1945)",
    "body": "Elected to an unprecedented four terms, **FDR** fundamentally restructured the federal government:\n\n* **The New Deal**: Responded to the Great Depression with Relief, Recovery, and Reform programs (Social Security, SEC, FDIC) expanding the federal regulatory footprint significantly.\n* **Global Command**: Guided the nation through WWII, establishing the 'Arsenal of Democracy' and laying foundations for the United Nations.\n* **Institutional Shift**: The modern presidency grew substantially in administrative authority, shifting legislative initiative to the executive branch.\n\n[HISTORY_CARD: topic: FDR's Institutional Precedent | value: 4 Elected Terms (1933 – 1945) | style: sky]",
    "thinking": "- **Intent:** Great Depression & WWII executive legacy study.\n- **Impact:** Administrative state expansion.",
    "priority": 13
  },
  {
    "id": "history-14-evolution-of-the-american-party-system",
    "domain": "history",
    "match": {
      "any": [
        "party",
        "political",
        "realignment",
        "whig",
        "federalist"
      ]
    },
    "heading": "Evolution of the American Party System",
    "body": "The U.S. political landscape has evolved through several distinct **Party Systems**:\n\n1. **First (1790s–1820s)**: Hamilton's Federalists vs. Jefferson's Democratic-Republicans.\n2. **Second (1820s–1850s)**: Jackson's Democrats vs. Clay's Whigs.\n3. **Third (1850s–1890s)**: Anti-slavery Republicans vs. pro-Southern Democrats — solidified during the Civil War.\n4. **Modern Realignments**: Mid-20th century shifts transformed Republicans into fiscal conservatives and Democrats into social welfare advocates.\n\n[HISTORY_CARD: topic: Core Realignment Inflection | value: Creation of the Republican Party (1854) | style: indigo]",
    "thinking": "- **Intent:** Political science party history lookup.\n- **Scope:** Realignment inflection points.",
    "priority": 14
  }
];

export const domainDefaults: Record<Exclude<Domain, 'math'>, DomainTopic> = {
  "space": {
    "id": "space-default",
    "domain": "space",
    "match": {},
    "heading": "Astronomical Analysis",
    "body": "Based on my internal offline cosmological database, I have processed your inquiry regarding **\"{query}\"**.\n\n1. **Cosmic Scaling Boundaries:** Outer space operates on scales that transcend standard human perception.\n2. **The Vacuum Medium:** Space is a nearly perfect vacuum where light travels unimpeded.\n3. **Universal Physics Constants:** Every star and galaxy is governed by $c$, $G$, and $\\hbar$.",
    "thinking": "- **Intent:** Open space topic query.\n- **Formulating Output:** Providing a comprehensive cosmic mechanics overview."
  },
  "earth": {
    "id": "earth-default",
    "domain": "earth",
    "match": {},
    "heading": "Interior Structure of the Earth",
    "body": "The Earth is divided into distinct geological layers mapped by seismic wave velocities:\n\n1. **Crust**: The outermost shell — $5\\text{ km}$ thick (oceanic) to $70\\text{ km}$ (continental).\n2. **Mantle**: A $2{,}900\\text{ km}$ thick zone of solid silicate rock, featuring the ductile **asthenosphere** upon which tectonic plates slide.\n3. **Outer Core**: A $2{,}200\\text{ km}$ thick pool of liquid iron-nickel whose convection generates our planetary **magnetic field**.\n4. **Inner Core**: A solid iron-nickel sphere kept solid despite temperatures exceeding $5{,}400^\\circ\\text{C}$ by immense gravitational pressure.\n\n[EARTH_CARD: topic: Outer Core Magnetic Field Dynamo | value: Churning Liquid Iron-Nickel | style: indigo]",
    "thinking": "- **Intent:** Planet core and interior geophysics.\n- **Seismic Modeling:** P-wave shadow boundaries."
  },
  "science": {
    "id": "science-default",
    "domain": "science",
    "match": {},
    "heading": "Advanced Telemetry Analytics",
    "body": "Based on my internal offline scientific database, I have processed **\"{query}\"**.\n\n1. **Dynamic Energy Quanta**: Microscopic systems are dictated by invariant Planck metrics.\n2. **Molecular Bond Mechanics**: Atoms interact based on strict electronegativity gradients.\n3. **Biological Information Transcription**: Genetic codes use hydrogen bonds to store and replicate operational blueprints with near-zero error tolerances.\n\n[SCIENCE_CARD: topic: Cognitive Database Sync | value: Active & Calibrated | style: violet]",
    "thinking": "- **Intent:** Generic science query fallbacks.\n- **Formulating Output:** Structure multi-disciplinary summary."
  },
  "history": {
    "id": "history-default",
    "domain": "history",
    "match": {},
    "heading": "Constitutional & Presidential Heritage",
    "body": "Based on my internal historical database, I have processed **\"{query}\"**.\n\n1. **Precedential Foundations**: The presidency depends on foundational actions by Washington refined over two centuries.\n2. **Constitutional Preservation**: During critical conflicts, presidential powers expanded to safeguard structural stability and civil rights.\n3. **Institutional Evolution**: The executive branch grew from a small advisory cabinet into a large modern administrative state.\n\n[HISTORY_CARD: topic: Historical Database Sync | value: Active & Synchronized | style: amber]",
    "thinking": "- **Intent:** Generic history fallbacks.\n- **Output:** Structure historical summaries."
  }
};

