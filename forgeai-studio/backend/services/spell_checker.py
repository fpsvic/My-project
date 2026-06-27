from data.knowledge_base import PROTECTED_ENGLISH_WORDS, HIGH_CONFIDENCE_KEYWORDS

_RAW_DICTIONARY = (
    "the and of to in is you that it he was for on are as with his they i at be "
    "this have from or one had by word but not what all were we when your can said "
    "there use an each which she do how their if will up other about out many then "
    "them these so some her would make like him into time has look more write go see "
    "number no way could people my than first water been call who oil its now find "
    "long down day did get come made may part over new sound take only little work "
    "know place year live me back give most very after thing our just name good "
    "sentence man think say great where help through much before line right too mean "
    "old any same tell boy follow came want show also around form three small set put "
    "end does another well large must big even such because turn here why ask went "
    "kind off need house picture try us again change play spell air away land "
    "different home move hand science physics chemistry biology astronomy geology "
    "mathematics calculus trigonometry geometry algebra arithmetic logic computing "
    "programming algorithms hardware software network database server client cloud "
    "web browser compiler terminal editor system process thread processor memory "
    "disk drive folder file document sheet presentation image photo audio video "
    "music track song signal wave frequency amplitude phase electricity current "
    "voltage resistance power energy force gravity velocity acceleration momentum "
    "inertia mass density volume capacity area length width height depth weight "
    "scale temperature heat cold pressure flow fluid liquid gas solid plasma vapor "
    "steam ice rain snow hail wind storm cloud sky sun moon star planet asteroid "
    "comet meteor galaxy nebula universe space cosmic vacuum orbit trajectory "
    "satellite rocket capsule probe launch booster engine thruster fuel propellant "
    "oxygen nitrogen hydrogen carbon helium argon neon krypton xenon radon lithium "
    "beryllium boron fluorine sodium magnesium aluminum silicon phosphorus sulfur "
    "chlorine potassium calcium iron cobalt nickel copper zinc silver gold mercury "
    "lead uranium plutonium history president election constitution democracy "
    "congress senate government governor mayor law court judge attorney jury trial "
    "crime police prison freedom liberty justice equality rights amendment treaty "
    "war peace military army navy volcano lithosphere rock mineral stone basalt "
    "granite obsidian sediment metamorphic sandstone shale marble slate eruption "
    "caldera subduction mariana trench hydrothermal vent chemosynthesis crust "
    "mantle core asthenosphere magnetic seismic boundary quantum planck boltzmann "
    "electronegativity transcription dna gene cell biology golden euler irrational "
    "washington lincoln roosevelt constitution federalist python javascript "
    "typescript golang kotlin rust derivative integral calculus trigonometry "
    "rarest fastest rocks ocean underwater"
)


def _build_dictionary() -> tuple[list[str], dict[str, list[str]]]:
    seen: set[str] = set()
    words: list[str] = []

    for raw in _RAW_DICTIONARY.split():
        w = "".join(c for c in raw.lower() if c.isalpha())
        if w and w not in seen:
            seen.add(w)
            words.append(w)

    for kw in HIGH_CONFIDENCE_KEYWORDS:
        w = kw.lower().strip()
        if w and w not in seen:
            seen.add(w)
            words.append(w)

    buckets: dict[str, list[str]] = {}
    for w in words:
        buckets.setdefault(w[0], []).append(w)

    return words, buckets


_DICTIONARY, _BUCKETS = _build_dictionary()


def _edit_distance(a: str, b: str) -> int:
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(la + 1))
    for i in range(1, lb + 1):
        curr = [i] + [0] * la
        for j in range(1, la + 1):
            cost = 0 if b[i - 1] == a[j - 1] else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[la]


def spell_correct_query(query: str) -> dict:
    tokens = (
        query.lower()
        .replace("?", "")
        .replace("!", "")
        .replace(",", "")
        .replace(".", "")
        .split()
    )
    corrected: list[str] = []
    corrections: list[dict] = []

    for word in tokens:
        if len(word) <= 4 or word in PROTECTED_ENGLISH_WORDS or word in _DICTIONARY:
            corrected.append(word)
            continue

        bucket = _BUCKETS.get(word[0], [])
        best_match: str | None = None
        min_dist = 3

        for vocab in bucket:
            if vocab not in HIGH_CONFIDENCE_KEYWORDS:
                continue
            if abs(len(word) - len(vocab)) >= min_dist:
                continue
            d = _edit_distance(word, vocab)
            if d < min_dist:
                min_dist = d
                best_match = vocab

        if best_match and min_dist < 3:
            corrections.append({"original": word, "corrected": best_match})
            corrected.append(best_match)
        else:
            corrected.append(word)

    return {"text": " ".join(corrected), "corrections": corrections}
