def _wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_thinking":
        return (
            f"### <i class=\"fa-solid fa-atom text-violet-500 mr-2\"></i> Thinking Process\n"
            f"{thinking}\n\n---\n\n### {heading}\n{body}"
        )
    if mode == "forge_instant":
        return f"### {heading}\n\n{body.split(chr(10)+chr(10))[0]}"
    return f"### {heading}\n{body}"


def generate_science_response(query: str, mode: str) -> str:
    q = query.lower().strip()

    # ── Quantum Mechanics ─────────────────────────────────────────────────────
    if any(w in q for w in ("quantum", "planck", "boltzmann", "heisenberg", "wave function", "superposition", "entanglement")):
        heading = "Quantum Mechanics: The Science of the Very Small"
        body = (
            "Quantum mechanics describes nature at the atomic and subatomic scale, where classical physics breaks down:\n\n"
            "**Core Principles**\n"
            "* **Wave-Particle Duality**: Every particle (electron, photon) exhibits both wave-like and particle-like behaviour depending on how it is observed.\n"
            "* **Heisenberg Uncertainty Principle**: It is impossible to simultaneously know both the exact position and momentum of a particle: $\\Delta x \\cdot \\Delta p \\geq \\hbar/2$.\n"
            "* **Superposition**: A quantum system can exist in multiple states at once until measured (Schrödinger's cat thought experiment).\n"
            "* **Quantum Entanglement**: Two particles can be correlated so that measuring one instantly determines the state of the other, regardless of distance.\n"
            "* **Planck Constant ($h$)**: $6.626 \\times 10^{-34}$ J·s — the fundamental quantum of action.\n\n"
            "**Applications**\n"
            "- Transistors and microchips (quantum tunnelling)\n"
            "- MRI scanners (nuclear spin states)\n"
            "- Lasers (stimulated emission of photons)\n"
            "- Quantum computing (qubits in superposition)\n\n"
            "[SCIENCE_CARD: topic: Planck Constant (h) | value: 6.626 × 10⁻³⁴ J·s | style: violet]"
        )
        thinking = (
            "- **Intent:** Quantum physics telemetry query.\n"
            "- **Parameters:** Planck energy-frequency constants, uncertainty bounds, wave-particle duality."
        )

    # ── Standard Model ────────────────────────────────────────────────────────
    elif any(w in q for w in ("standard model", "particle physics", "quark", "lepton", "boson", "higgs", "fermion", "gluon")):
        heading = "The Standard Model of Particle Physics"
        body = (
            "The Standard Model is the theory describing three of the four fundamental forces (electromagnetic, weak, strong) and classifying all known elementary particles:\n\n"
            "**Matter Particles (Fermions)**\n"
            "* **Quarks** (6 flavours): up, down, charm, strange, top, bottom — combine to form protons and neutrons.\n"
            "* **Leptons** (6 types): electron, muon, tau, and three corresponding neutrinos.\n\n"
            "**Force Carriers (Bosons)**\n"
            "* **Photon (γ)**: Carries the electromagnetic force.\n"
            "* **W⁺, W⁻, Z bosons**: Carry the weak nuclear force (responsible for radioactive decay).\n"
            "* **Gluons (8 types)**: Carry the strong nuclear force, binding quarks inside protons/neutrons.\n"
            "* **Higgs Boson**: Discovered at CERN in 2012 — gives other particles their mass via the Higgs field.\n\n"
            "**What it does NOT explain**\n"
            "- Gravity (no graviton confirmed)\n"
            "- Dark matter or dark energy\n"
            "- Why there is more matter than antimatter\n\n"
            "[SCIENCE_CARD: topic: Higgs Boson Discovery | value: CERN, July 4, 2012 | style: violet]"
        )
        thinking = (
            "- **Intent:** Particle physics standard model lookup.\n"
            "- **Parameters:** Fermion/boson taxonomy, force carrier identification, Higgs mechanism."
        )

    # ── CRISPR ────────────────────────────────────────────────────────────────
    elif any(w in q for w in ("crispr", "gene editing", "gene edit", "cas9")):
        heading = "CRISPR-Cas9: Precision Gene Editing"
        body = (
            "CRISPR (Clustered Regularly Interspaced Short Palindromic Repeats) is a revolutionary gene-editing technology derived from bacterial immune systems:\n\n"
            "**How it works**\n"
            "1. A **guide RNA (gRNA)** is designed to match a specific DNA sequence in the target genome.\n"
            "2. The gRNA binds to the **Cas9 enzyme**, directing it to the target location.\n"
            "3. Cas9 acts as **molecular scissors**, cutting both strands of DNA at the precise site.\n"
            "4. The cell's natural repair mechanisms either **disable** the gene (NHEJ) or **insert new DNA** (HDR).\n\n"
            "**Applications**\n"
            "* Treating genetic diseases: sickle cell disease (FDA approved 2023), beta-thalassemia\n"
            "* Cancer immunotherapy (CAR-T cell engineering)\n"
            "* Agricultural improvements (disease-resistant crops)\n"
            "* Basic research into gene function\n\n"
            "**Nobel Prize**: Jennifer Doudna and Emmanuelle Charpentier won the 2020 Nobel Prize in Chemistry for developing CRISPR-Cas9.\n\n"
            "[SCIENCE_CARD: topic: CRISPR Nobel Prize | value: Doudna & Charpentier, 2020 | style: fuchsia]"
        )
        thinking = (
            "- **Intent:** Biotechnology gene editing query.\n"
            "- **Parameters:** CRISPR mechanism, Cas9 function, therapeutic applications."
        )

    # ── Nuclear Fission vs Fusion ─────────────────────────────────────────────
    elif any(w in q for w in ("fission", "fusion", "nuclear", "reactor", "uranium", "plutonium", "deuterium", "tritium")):
        heading = "Nuclear Fission vs. Nuclear Fusion"
        body = (
            "Both fission and fusion release enormous energy via Einstein's **E = mc²**, but they work oppositely:\n\n"
            "**Nuclear Fission**\n"
            "* A heavy nucleus (Uranium-235 or Plutonium-239) is split into smaller nuclei by a neutron.\n"
            "* Releases ~200 MeV per reaction; chain reactions can be sustained in a reactor.\n"
            "* Powers all current nuclear power plants (~10% of world electricity).\n"
            "* Produces radioactive waste with half-lives of thousands of years.\n\n"
            "**Nuclear Fusion**\n"
            "* Light nuclei (Deuterium + Tritium) are forced together at extreme temperatures (>100 million °C) to form Helium.\n"
            "* Releases ~17.6 MeV per D-T reaction — weight-for-weight ~4× more energy than fission.\n"
            "* Fuel (hydrogen isotopes) is virtually unlimited; waste is non-radioactive Helium.\n"
            "* The challenge: sustaining a plasma hotter than the Sun's core.\n"
            "* ITER (France) is the world's largest fusion experiment — target first plasma ~2025.\n"
            "* NIF (USA) achieved **fusion ignition** in December 2022 — more energy out than laser energy in.\n\n"
            "[SCIENCE_CARD: topic: NIF Fusion Ignition | value: December 5, 2022 | style: amber]"
        )
        thinking = (
            "- **Intent:** Nuclear physics comparison query.\n"
            "- **Parameters:** Fission chain reaction mechanics, fusion plasma confinement, energy yields."
        )

    # ── Speed of Light & Relativity ───────────────────────────────────────────
    elif any(w in q for w in ("speed of light", "relativity", "special relativity", "general relativity", "e=mc", "time dilation", "length contraction")):
        heading = "The Speed of Light & Einstein's Relativity"
        body = (
            "**The Speed of Light**\n"
            "* In a vacuum: **$c = 299{,}792{,}458$ m/s** (exactly, by definition)\n"
            "* Light travels from the Sun to Earth in ~**8 minutes 20 seconds**.\n"
            "* It circles Earth's equator **7.5 times per second**.\n\n"
            "**Special Relativity (1905)**\n"
            "* The laws of physics are identical for all observers in uniform motion.\n"
            "* The speed of light is the same for all observers regardless of their motion.\n"
            "* **Mass-Energy Equivalence**: $E = mc^2$ — a tiny mass converts to enormous energy.\n"
            "* **Time Dilation**: Moving clocks run slower — GPS satellites must correct for this effect.\n"
            "* **Length Contraction**: Objects moving at relativistic speeds appear shorter in the direction of travel.\n\n"
            "**General Relativity (1915)**\n"
            "* Gravity is not a force but the **curvature of spacetime** caused by mass and energy.\n"
            "* Predicts black holes, gravitational waves (confirmed 2015 by LIGO), and the expanding universe.\n"
            "* Light bends around massive objects — confirmed during the 1919 solar eclipse.\n\n"
            "[SCIENCE_CARD: topic: Speed of Light (c) | value: 299,792,458 m/s | style: emerald]"
        )
        thinking = (
            "- **Intent:** Relativistic physics query.\n"
            "- **Parameters:** Special vs general relativity, time dilation, E=mc² derivation."
        )

    # ── Black Holes ───────────────────────────────────────────────────────────
    elif any(w in q for w in ("black hole", "event horizon", "singularity", "hawking radiation", "spaghettification")):
        heading = "Black Holes & Event Horizons"
        body = (
            "A **black hole** is a region of spacetime where gravity is so extreme that nothing — not even light — can escape.\n\n"
            "**Formation**\n"
            "* Stellar black holes form when a massive star (>20 solar masses) collapses at the end of its life in a **supernova**.\n"
            "* Supermassive black holes (millions–billions of solar masses) reside at the centre of most galaxies, including the Milky Way (**Sagittarius A***, 4 million solar masses).\n\n"
            "**Key Concepts**\n"
            "* **Event Horizon**: The point of no return — the boundary beyond which escape velocity exceeds $c$.\n"
            "* **Singularity**: The mathematical point at the centre of infinite density where known physics breaks down.\n"
            "* **Hawking Radiation**: Stephen Hawking (1974) theorised that black holes slowly emit thermal radiation due to quantum effects near the event horizon, causing them to evaporate over trillions of years.\n"
            "* **Spaghettification**: Tidal forces near a black hole stretch infalling objects into long thin strands.\n\n"
            "**Observations**\n"
            "* First image: M87* black hole captured by the Event Horizon Telescope in **April 2019**.\n"
            "* Second image: Sagittarius A* imaged in **May 2022**.\n"
            "* Gravitational waves from black hole mergers detected by LIGO since **2015**.\n\n"
            "[SCIENCE_CARD: topic: First Black Hole Image | value: M87*, Event Horizon Telescope 2019 | style: violet]"
        )
        thinking = (
            "- **Intent:** Astrophysics black hole query.\n"
            "- **Parameters:** Event horizon mechanics, Hawking radiation, observational milestones."
        )

    # ── String Theory ─────────────────────────────────────────────────────────
    elif any(w in q for w in ("string theory", "m-theory", "extra dimension", "brane", "superstring")):
        heading = "String Theory: An Overview"
        body = (
            "**String theory** is a theoretical framework proposing that the fundamental constituents of nature are not point-like particles but tiny one-dimensional **vibrating strings** of energy.\n\n"
            "**Core Ideas**\n"
            "* Different **vibrational modes** of a string correspond to different particles (electrons, quarks, photons, gravitons).\n"
            "* Requires **10 dimensions** (superstring theory) or **11 dimensions** (M-theory) — extra dimensions are compactified at the Planck scale (~$10^{-35}$ m).\n"
            "* Naturally incorporates **gravity** alongside quantum mechanics — something the Standard Model cannot do.\n\n"
            "**Variants**\n"
            "* Five consistent superstring theories were unified by **M-theory** (Edward Witten, 1995).\n"
            "* **Branes** (membranes) are higher-dimensional objects in M-theory; our universe may be a 3-brane.\n\n"
            "**Status**\n"
            "* No direct experimental evidence exists yet — predictions require energies far beyond current accelerators.\n"
            "* Remains a leading candidate for a **Theory of Everything** but is not yet a falsifiable scientific theory.\n"
            "* Alternative approaches include Loop Quantum Gravity (LQG).\n\n"
            "[SCIENCE_CARD: topic: String Theory Dimensions | value: 10 (superstring) / 11 (M-theory) | style: violet]"
        )
        thinking = (
            "- **Intent:** Theoretical physics string theory query.\n"
            "- **Parameters:** Vibrational modes, extra dimensions, M-theory unification."
        )

    # ── Climate Science ───────────────────────────────────────────────────────
    elif any(w in q for w in ("greenhouse", "carbon cycle", "climate", "global warming", "co2", "atmosphere", "ozone")):
        heading = "Climate Science: The Greenhouse Effect & Carbon Cycle"
        body = (
            "**The Greenhouse Effect**\n"
            "* Solar radiation passes through Earth's atmosphere and warms the surface.\n"
            "* Earth re-emits heat as **infrared radiation** (longer wavelengths).\n"
            "* **Greenhouse gases** (CO₂, CH₄, N₂O, H₂O vapour) absorb and re-emit this infrared radiation, warming the atmosphere.\n"
            "* Without any greenhouse effect Earth's average temperature would be ~**−18°C** instead of +15°C.\n"
            "* **Enhanced greenhouse effect**: Human emissions amplify this warming — CO₂ has risen from 280 ppm (pre-industrial) to over **420 ppm** (2024).\n\n"
            "**The Carbon Cycle**\n"
            "* **Photosynthesis**: Plants absorb CO₂ and release O₂.\n"
            "* **Respiration & Decomposition**: Organisms release CO₂ back.\n"
            "* **Ocean absorption**: Oceans absorb ~25–30% of human CO₂ emissions (causing ocean acidification).\n"
            "* **Fossil fuel burning**: Returns carbon buried millions of years ago back to the atmosphere in decades.\n\n"
            "**Key facts**\n"
            "- Global average temperature has risen ~**1.2°C** since pre-industrial times.\n"
            "- The Paris Agreement (2015) targets limiting warming to **1.5–2°C**.\n"
            "- Arctic is warming ~4× faster than the global average.\n\n"
            "[SCIENCE_CARD: topic: Atmospheric CO₂ (2024) | value: >420 ppm | style: emerald]"
        )
        thinking = (
            "- **Intent:** Climate science query.\n"
            "- **Parameters:** Greenhouse gas mechanisms, carbon cycle flows, anthropogenic warming data."
        )

    # ── Human Genetics ────────────────────────────────────────────────────────
    elif any(w in q for w in ("dominant", "recessive", "chromosome", "allele", "mendel", "genetics", "heredity", "trait", "genotype", "phenotype")):
        heading = "Human Genetics: Inheritance & Chromosomes"
        body = (
            "**Chromosomes**\n"
            "* Humans have **46 chromosomes** in 23 pairs in every somatic cell.\n"
            "* Pair 23 determines biological sex: **XX** (female) or **XY** (male).\n"
            "* Each chromosome contains thousands of **genes** — segments of DNA encoding proteins.\n\n"
            "**Mendelian Inheritance**\n"
            "* **Dominant alleles** (written uppercase, e.g. **A**): expressed even when only one copy is present.\n"
            "* **Recessive alleles** (lowercase, e.g. **a**): expressed only when two copies are inherited (homozygous).\n"
            "* **Genotype** = actual allele combination (AA, Aa, aa); **Phenotype** = observable trait.\n\n"
            "| Genotype | Phenotype (if A is dominant) |\n"
            "|----------|-----------------------------|\n"
            "| AA       | Dominant trait              |\n"
            "| Aa       | Dominant trait (carrier)    |\n"
            "| aa       | Recessive trait             |\n\n"
            "**Inheritance Patterns**\n"
            "* **Autosomal dominant** (e.g., Huntington's disease): one copy causes disease.\n"
            "* **Autosomal recessive** (e.g., cystic fibrosis): two copies needed.\n"
            "* **X-linked recessive** (e.g., haemophilia): more common in males (only one X chromosome).\n"
            "* **Codominance** (e.g., ABO blood types): both alleles expressed simultaneously.\n\n"
            "[SCIENCE_CARD: topic: Human Chromosome Count | value: 46 (23 pairs) | style: fuchsia]"
        )
        thinking = (
            "- **Intent:** Mendelian genetics and chromosome query.\n"
            "- **Parameters:** Dominant/recessive allele mechanics, inheritance patterns, chromosome structure."
        )

    # ── Neuroscience ──────────────────────────────────────────────────────────
    elif any(w in q for w in ("neuron", "synapse", "brain wave", "neuroscience", "action potential", "dendrite", "axon", "neurotransmitter")):
        heading = "Neuroscience: Neurons, Synapses & Brain Waves"
        body = (
            "The brain is a network of ~**86 billion neurons** communicating via electrical and chemical signals.\n\n"
            "**Neuron Structure**\n"
            "* **Cell body (soma)**: Contains the nucleus and metabolic machinery.\n"
            "* **Dendrites**: Tree-like extensions that receive incoming signals from other neurons.\n"
            "* **Axon**: Long fibre that transmits electrical impulses (action potentials) away from the cell body.\n"
            "* **Myelin sheath**: Fatty insulation that speeds up signal transmission up to 120 m/s.\n\n"
            "**Synaptic Transmission**\n"
            "1. An **action potential** travels down the axon (all-or-nothing electrical spike, ~+40 mV).\n"
            "2. Triggers release of **neurotransmitters** from vesicles into the **synaptic cleft**.\n"
            "3. Neurotransmitters bind to **receptors** on the postsynaptic neuron, causing excitation or inhibition.\n"
            "4. Key neurotransmitters: **Dopamine** (reward), **Serotonin** (mood), **GABA** (inhibition), **Glutamate** (excitation), **Acetylcholine** (muscle control, memory).\n\n"
            "**Brain Waves (EEG)**\n"
            "| Wave | Frequency | State |\n"
            "|------|-----------|-------|\n"
            "| Delta (δ) | 0.5–4 Hz | Deep sleep |\n"
            "| Theta (θ) | 4–8 Hz | Drowsiness, creativity |\n"
            "| Alpha (α) | 8–12 Hz | Relaxed wakefulness |\n"
            "| Beta (β) | 12–30 Hz | Active thinking |\n"
            "| Gamma (γ) | 30–100 Hz | High-level cognition |\n\n"
            "[SCIENCE_CARD: topic: Neurons in Human Brain | value: ~86 billion | style: violet]"
        )
        thinking = (
            "- **Intent:** Neuroscience and brain function query.\n"
            "- **Parameters:** Neuron anatomy, synaptic transmission, EEG brain wave frequencies."
        )

    # ── General Chemistry ─────────────────────────────────────────────────────
    elif any(w in q for w in ("chemistry", "element", "carbon", "noble", "electroneg")):
        heading = "Molecular Chemistry & Electronegativity Scales"
        body = (
            "Chemical interactions are governed by electron configurations and atomic properties:\n\n"
            "* **Carbon Allotropes**: **Diamond** forms a rigid tetrahedral 3D lattice making it "
            "exceptionally hard. **Graphite** forms stacked planar hexagonal sheets that slide easily.\n"
            "* **Electronegativity (Pauling Scale)**: Measures an atom's tendency to attract shared "
            "electrons. Fluorine is the most electronegative; Francium is the least.\n"
            "* **Noble Gases**: Group 18 elements with completely filled valence shells — "
            "exceptionally stable and chemically inert under standard conditions.\n\n"
            "[SCIENCE_CARD: topic: Pauling Electronegativity: Fluorine | value: 3.98 (Maximum Scale) | style: amber]"
        )
        thinking = (
            "- **Intent:** Chemistry element metrics.\n"
            "- **Parameters:** Carbon bonding geometries, Pauling electronegativity scales."
        )

    # ── DNA / Biology ─────────────────────────────────────────────────────────
    elif any(w in q for w in ("dna", "gene", "cell", "transcription", "biology")):
        heading = "Genetics, DNA Base-Pairing & Transcription"
        body = (
            "Biological life is coordinated at the molecular level inside cell nuclei:\n\n"
            "* **Double Helix & Hydrogen Bonding**: DNA consists of two complementary chains. "
            "Adenine (A) pairs with Thymine (T) via **two hydrogen bonds**; "
            "Cytosine (C) pairs with Guanine (G) via **three hydrogen bonds** — making CG pairs stronger.\n"
            "* **Transcription & Translation**: RNA polymerase copies a DNA segment into mRNA. "
            "The ribosome then decodes this mRNA to assemble amino acid polypeptide chains (proteins).\n\n"
            "[SCIENCE_CARD: topic: CG Base-Pair Stability | value: 3 Hydrogen Bonds (Tighter Bind) | style: fuchsia]"
        )
        thinking = (
            "- **Intent:** Molecular genetics transcription query.\n"
            "- **Parameters:** Hydrogen bonding differences between nucleic base pairings."
        )

    # ── Mathematics ───────────────────────────────────────────────────────────
    elif any(w in q for w in ("math", "constant", "golden ratio", "phi", "euler")):
        heading = "Pure Mathematical Limits & Irrational Constants"
        body = (
            "Mathematics uses unique irrational constants to map natural proportions and limit scales:\n\n"
            "* **The Golden Ratio ($\\phi$)**: The limit ratio of consecutive Fibonacci numbers, "
            "appearing in biological geometry and spiral galaxy curves.\n"
            "$$\\phi = \\frac{1 + \\sqrt{5}}{2} \\approx 1.6180339887...$$\n"
            "* **Euler-Mascheroni Constant ($\\gamma$)**: The limiting delta between the harmonic series "
            "and the natural logarithm — core to advanced number theory.\n\n"
            "[SCIENCE_CARD: topic: The Golden Ratio (Phi) | value: 1.6180339887... | style: emerald]"
        )
        thinking = (
            "- **Intent:** Pure mathematical constants lookup.\n"
            "- **Parameters:** Golden ratio algebra derivations, Euler limits."
        )

    else:
        heading = "Advanced Telemetry Analytics"
        body = (
            f"Based on my internal offline scientific database, I have processed **\"{query}\"**.\n\n"
            "1. **Dynamic Energy Quanta**: Microscopic systems are dictated by invariant Planck metrics.\n"
            "2. **Molecular Bond Mechanics**: Atoms interact based on strict electronegativity gradients.\n"
            "3. **Biological Information Transcription**: Genetic codes use hydrogen bonds to store "
            "and replicate operational blueprints with near-zero error tolerances.\n\n"
            "[SCIENCE_CARD: topic: Cognitive Database Sync | value: Active & Calibrated | style: violet]"
        )
        thinking = (
            "- **Intent:** Generic science query fallbacks.\n"
            "- **Formulating Output:** Structure multi-disciplinary summary."
        )

    return _wrap(thinking, heading, body, mode)
