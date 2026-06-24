def _wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_thinking":
        return (
            f"### <i class=\"fa-solid fa-scroll text-amber-600 mr-2\"></i> Thinking Process\n"
            f"{thinking}\n\n---\n\n### {heading}\n{body}"
        )
    if mode == "forge_instant":
        return f"### {heading}\n\n{body.split(chr(10)+chr(10))[0]}"
    return f"### {heading}\n{body}"


def generate_history_response(query: str, mode: str) -> str:
    q = query.lower().strip()

    if any(w in q for w in ("washington", "founding", "hamilton", "jefferson")):
        heading = "George Washington & The Founding Era (1789–1797)"
        body = (
            "As the first President, **George Washington** established crucial precedents:\n\n"
            "* **The Cabinet Concept**: He structured the first formal cabinet — Alexander Hamilton "
            "(Treasury, Federalist vision) versus Thomas Jefferson (State, agrarian decentralization).\n"
            "* **Foreign Policy Neutrality**: Issued the Proclamation of Neutrality in 1793, keeping "
            "the young republic out of European conflicts.\n"
            "* **The Two-Term Tradition**: By voluntarily stepping down in 1797 he established a "
            "voluntary executive limit later codified by the **22nd Amendment**.\n\n"
            "[HISTORY_CARD: topic: Washington's Presidential Tenure | value: 1789 – 1797 (2 Terms) | style: amber]"
        )
        thinking = (
            "- **Intent:** Early executive history lookup.\n"
            "- **Context:** Federalist vs. Democratic-Republican cabinet dynamics."
        )

    elif any(w in q for w in ("lincoln", "civil war", "gettysburg", "emancipation")):
        heading = "Abraham Lincoln & The Constitutional Crisis (1861–1865)"
        body = (
            "Presiding over the nation's most profound crisis, **Abraham Lincoln** preserved the Union:\n\n"
            "* **Preservation of the Union**: Maintained that secession was legally void and led federal "
            "efforts through the Civil War.\n"
            "* **The Emancipation Proclamation**: Issued January 1, 1863 — declared all enslaved people "
            "in Confederate territories forever free, shifting the war's moral focus.\n"
            "* **Gettysburg Address**: Redefined the war as a 'new birth of freedom' ensuring government "
            "'of the people, by the people, for the people, shall not perish from the earth.'\n\n"
            "[HISTORY_CARD: topic: Lincoln's Core Milestone | value: Emancipation Proclamation (1863) | style: rose]"
        )
        thinking = (
            "- **Intent:** Civil War presidency and Lincoln legacy analysis.\n"
            "- **Significance:** Wartime executive powers expansion."
        )

    elif any(w in q for w in ("fdr", "roosevelt", "new deal", "depression")):
        heading = "Franklin D. Roosevelt & The Great Transformation (1933–1945)"
        body = (
            "Elected to an unprecedented four terms, **FDR** fundamentally restructured the federal government:\n\n"
            "* **The New Deal**: Responded to the Great Depression with Relief, Recovery, and Reform programs "
            "(Social Security, SEC, FDIC) expanding the federal regulatory footprint significantly.\n"
            "* **Global Command**: Guided the nation through WWII, establishing the 'Arsenal of Democracy' "
            "and laying foundations for the United Nations.\n"
            "* **Institutional Shift**: The modern presidency grew substantially in administrative authority, "
            "shifting legislative initiative to the executive branch.\n\n"
            "[HISTORY_CARD: topic: FDR's Institutional Precedent | value: 4 Elected Terms (1933 – 1945) | style: sky]"
        )
        thinking = (
            "- **Intent:** Great Depression & WWII executive legacy study.\n"
            "- **Impact:** Administrative state expansion."
        )

    elif any(w in q for w in ("party", "political", "realignment", "whig", "federalist")):
        heading = "Evolution of the American Party System"
        body = (
            "The U.S. political landscape has evolved through several distinct **Party Systems**:\n\n"
            "1. **First (1790s–1820s)**: Hamilton's Federalists vs. Jefferson's Democratic-Republicans.\n"
            "2. **Second (1820s–1850s)**: Jackson's Democrats vs. Clay's Whigs.\n"
            "3. **Third (1850s–1890s)**: Anti-slavery Republicans vs. pro-Southern Democrats — "
            "solidified during the Civil War.\n"
            "4. **Modern Realignments**: Mid-20th century shifts transformed Republicans into fiscal "
            "conservatives and Democrats into social welfare advocates.\n\n"
            "[HISTORY_CARD: topic: Core Realignment Inflection | value: Creation of the Republican Party (1854) | style: indigo]"
        )
        thinking = (
            "- **Intent:** Political science party history lookup.\n"
            "- **Scope:** Realignment inflection points."
        )

    else:
        heading = "Constitutional & Presidential Heritage"
        body = (
            f"Based on my internal historical database, I have processed **\"{query}\"**.\n\n"
            "1. **Precedential Foundations**: The presidency depends on foundational actions by Washington "
            "refined over two centuries.\n"
            "2. **Constitutional Preservation**: During critical conflicts, presidential powers expanded "
            "to safeguard structural stability and civil rights.\n"
            "3. **Institutional Evolution**: The executive branch grew from a small advisory cabinet "
            "into a large modern administrative state.\n\n"
            "[HISTORY_CARD: topic: Historical Database Sync | value: Active & Synchronized | style: amber]"
        )
        thinking = (
            "- **Intent:** Generic history fallbacks.\n"
            "- **Output:** Structure historical summaries."
        )

    return _wrap(thinking, heading, body, mode)
