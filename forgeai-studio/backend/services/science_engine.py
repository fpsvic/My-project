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

    if any(w in q for w in ("quantum", "physics", "planck", "boltzmann")):
        heading = "Quantum Mechanics & Cosmic Constants"
        body = (
            "At subatomic scales, nature operates in discrete packets of energy called **quanta**:\n\n"
            "* **Planck Constant ($h$)**: Relates the energy of a photon to its frequency — "
            "the core mathematical value of quantum mechanics.\n"
            "* **Heisenberg Uncertainty Principle**: One cannot simultaneously measure both the precise "
            "position and momentum of a particle with absolute certainty.\n"
            "* **Boltzmann Constant ($k_B$)**: Links absolute temperature to kinetic energy in "
            "individual gas particles, connecting thermodynamics with quantum states.\n\n"
            "[SCIENCE_CARD: topic: Planck Constant (h) | value: 6.626 x 10⁻³⁴ J·s | style: violet]"
        )
        thinking = (
            "- **Intent:** Quantum physics telemetry query.\n"
            "- **Parameters:** Planck energy-frequency constants, uncertainty bounds."
        )

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
