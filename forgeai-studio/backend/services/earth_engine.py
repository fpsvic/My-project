def _wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_thinking":
        return (
            f"### <i class=\"fa-solid fa-mountain-sun text-emerald-500 mr-2\"></i> Thinking Process\n"
            f"{thinking}\n\n---\n\n### {heading}\n{body}"
        )
    if mode == "forge_instant":
        return f"### {heading}\n\n{body.split(chr(10)+chr(10))[0]}"
    return f"### {heading}\n{body}"


def generate_earth_response(query: str, mode: str) -> str:
    q = query.lower().strip()

    if "rarest" in q or "rare" in q:
        heading = "Rarest Minerals on Earth"
        body = (
            "The rarest minerals on Earth are dictated by precise geological compositions:\n\n"
            "1. **Kyawthuite**: The single rarest mineral in the world — only one specimen has ever been found, "
            "in Myanmar. It is an orange-hued bismuth-antimony oxide ($Bi^{3+}Sb^{5+}O_4$).\n"
            "2. **Painite**: A complex calcium zirconium borate ($CaZrBAl_9O_{18}$) with trace chromium "
            "impurities producing deep reddish-brown crystals.\n"
            "3. **Lonsdaleite**: A hexagonal carbon allotrope found in meteorites, theoretically 58% harder than diamond.\n\n"
            "[EARTH_CARD: topic: World's Rarest Specimen | value: Kyawthuite (1 Verified Crystal) | style: amber]"
        )
        thinking = (
            "- **Intent:** Geologic mineral metrics (rarest rocks).\n"
            "- **Data Points:** Kyawthuite bismuth stoichiometry, Painite discovery parameters."
        )

    elif any(w in q for w in ("rock", "stone", "mineral", "petrolog", "granite", "basalt", "sediment", "metamorph")):
        heading = "Petrological Foundations & Rock Cycles"
        body = (
            "Rocks are the solid building blocks of Earth's crust, divided into three primary families:\n\n"
            "1. **Igneous Rocks**: Formed from cooling magma. *Intrusive* rocks like **Granite** cool slowly "
            "deep underground; *Extrusive* rocks like **Basalt** and **Obsidian** cool rapidly at the surface.\n"
            "2. **Sedimentary Rocks**: Formed by the compaction and cementation of particles over millions of years. "
            "Examples: **Limestone**, **Sandstone**, **Shale**.\n"
            "3. **Metamorphic Rocks**: Pre-existing rocks altered by extreme heat and pressure. "
            "**Marble** is metamorphosed limestone; **Slate** arises from shale.\n\n"
            "[EARTH_CARD: topic: Crustal Rock Cycle Interplay | value: Igneous, Sedimentary & Metamorphic | style: emerald]"
        )
        thinking = (
            "- **Intent:** Petrologic classification query.\n"
            "- **Taxonomy:** Intrusive vs extrusive igneous, lithification of sediments, recrystallization."
        )

    elif any(w in q for w in ("volcano", "lava", "magma", "caldera", "ring of fire")):
        heading = "Volcanological & Magmatic Systems"
        body = (
            "Volcanoes are vents where molten magma escapes to the surface. Their explosiveness depends on silica content:\n\n"
            "* **Stratovolcanoes**: Tall, steep mountains formed from viscous, silica-rich lavas. "
            "They erupt violently with devastating **pyroclastic flows**.\n"
            "* **Shield Volcanoes**: Broad, low-profile structures formed by fluid basaltic lava. "
            "They erupt effusively without major explosions.\n"
            "* **Calderas**: Colossal bowl-shaped depressions formed when a magma chamber empties "
            "and the overlying peak collapses inward.\n\n"
            "[EARTH_CARD: topic: Maximum Volcanic Eruptive Scale | value: VEI-8 Caldera Supervolcanoes | style: rose]"
        )
        thinking = (
            "- **Intent:** Volcanology structural query.\n"
            "- **Fluid Dynamics:** Viscosity vs silica ratio, composite stratovolcano gas pressure buildup."
        )

    elif any(w in q for w in ("underwater", "trench", "mariana", "vent", "black smoker", "seafloor")):
        heading = "Underwater Oceanic Geomorphology"
        body = (
            "The deep ocean floor is geologically active, driven by plate tectonics:\n\n"
            "* **Oceanic Trenches**: Where plates collide, the denser oceanic plate is forced into the mantle "
            "via **subduction**. The **Challenger Deep** in the Mariana Trench plunges to "
            "**36,070 feet (10,994 m)** — pressure of $1{,}086\\text{ bar}$.\n"
            "* **Hydrothermal Vents & Black Smokers**: Along divergent boundaries, superheated water "
            "exceeding **$400^\\circ\\text{C}$** vents into the ocean, depositing heavy metal chimneys "
            "called **Black Smokers**. These support ecosystems driven by **chemosynthesis**.\n\n"
            "[EARTH_CARD: topic: Challenger Deep Hydrostatic Pressure | value: 1,086 Bar / 15,750 PSI | style: sky]"
        )
        thinking = (
            "- **Intent:** Oceanography and marine geology.\n"
            "- **Physical Limits:** Deep trench subduction physics, Mariana plate geometry."
        )

    else:
        heading = "Interior Structure of the Earth"
        body = (
            "The Earth is divided into distinct geological layers mapped by seismic wave velocities:\n\n"
            "1. **Crust**: The outermost shell — $5\\text{ km}$ thick (oceanic) to $70\\text{ km}$ (continental).\n"
            "2. **Mantle**: A $2{,}900\\text{ km}$ thick zone of solid silicate rock, featuring the ductile "
            "**asthenosphere** upon which tectonic plates slide.\n"
            "3. **Outer Core**: A $2{,}200\\text{ km}$ thick pool of liquid iron-nickel whose convection "
            "generates our planetary **magnetic field**.\n"
            "4. **Inner Core**: A solid iron-nickel sphere kept solid despite temperatures exceeding "
            "$5{,}400^\\circ\\text{C}$ by immense gravitational pressure.\n\n"
            "[EARTH_CARD: topic: Outer Core Magnetic Field Dynamo | value: Churning Liquid Iron-Nickel | style: indigo]"
        )
        thinking = (
            "- **Intent:** Planet core and interior geophysics.\n"
            "- **Seismic Modeling:** P-wave shadow boundaries."
        )

    return _wrap(thinking, heading, body, mode)
