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

    # ── Ancient Egypt ─────────────────────────────────────────────────────────
    if any(w in q for w in ("egypt", "pharaoh", "pyramid", "hieroglyph", "sphinx", "nile", "ramesses", "cleopatra", "tutankhamun")):
        heading = "Ancient Egypt: Pharaohs, Pyramids & Hieroglyphics"
        body = (
            "Ancient Egypt was one of the world's longest-lasting civilisations, spanning ~**3,000 years** (c. 3100–30 BC):\n\n"
            "**The Pharaohs**\n"
            "* The pharaoh was considered a living god — both supreme ruler and high priest.\n"
            "* **Ramesses II (the Great)** (reigned 1279–1213 BC): Egypt's most celebrated pharaoh, known for the Battle of Kadesh and the Abu Simbel temples.\n"
            "* **Tutankhamun** (reigned 1332–1323 BC): The 'boy king' whose largely intact tomb was discovered by Howard Carter in **1922**.\n"
            "* **Cleopatra VII** (reigned 51–30 BC): The last active pharaoh, fluent in nine languages; her death ended the Ptolemaic dynasty and Egyptian independence.\n\n"
            "**The Pyramids**\n"
            "* Built as royal tombs during the **Old Kingdom** (c. 2686–2181 BC).\n"
            "* **Great Pyramid of Giza** (c. 2560 BC): Built for Pharaoh Khufu — **146.5 m** tall (originally), constructed with ~**2.3 million stone blocks** averaging 2.5–15 tonnes each.\n"
            "* Remained the world's tallest human-made structure for **3,800 years**.\n"
            "* Three pyramids at Giza: Khufu, Khafre, Menkaure, with the Great Sphinx guarding the complex.\n\n"
            "**Hieroglyphics**\n"
            "* A writing system combining logographic and alphabetic elements — over **700 distinct signs**.\n"
            "* Used for ~3,500 years (c. 3200 BC – 400 AD).\n"
            "* **Rosetta Stone** (196 BC, discovered 1799): Decree written in hieroglyphics, Demotic, and Ancient Greek — allowed Jean-François Champollion to decode hieroglyphics in **1822**.\n\n"
            "[HISTORY_CARD: topic: Great Pyramid of Giza | value: Built c. 2560 BC, 146.5 m tall | style: amber]"
        )
        thinking = (
            "- **Intent:** Ancient Egyptian civilisation query.\n"
            "- **Context:** Pharaonic rule, pyramid construction, hieroglyphic writing system."
        )

    # ── Roman Empire ──────────────────────────────────────────────────────────
    elif any(w in q for w in ("roman empire", "rome", "julius caesar", "augustus", "gladiator", "colosseum", "byzantine")):
        heading = "The Roman Empire: Rise and Fall"
        body = (
            "The Roman Empire was the most powerful state in the ancient world, lasting from **27 BC to 476 AD** (Western) / **1453 AD** (Eastern/Byzantine):\n\n"
            "**Rise of Rome**\n"
            "* Rome was a republic from **509 BC** before Julius Caesar's dictatorship destabilised it.\n"
            "* **Julius Caesar** (100–44 BC): Conquered Gaul (58–50 BC), crossed the Rubicon, became dictator perpetuo, and was assassinated on the Ides of March (March 15, 44 BC).\n"
            "* **Augustus** (27 BC – 14 AD): First Emperor — turned the republic into an empire. The **Pax Romana** (27 BC – 180 AD) was 200 years of relative peace and prosperity.\n\n"
            "**At its Peak**\n"
            "* At its greatest extent under **Trajan** (117 AD): ~**5 million km²**, ~**70 million people** (20% of the world's population).\n"
            "* Iconic engineering: aqueducts (14 in Rome alone), roads (400,000 km of roads), the Colosseum (72 AD, held 50,000–80,000 spectators).\n\n"
            "**Fall of the Western Empire**\n"
            "* Causes: overextension, economic strain, political instability, barbarian invasions, and the split of the empire.\n"
            "* **476 AD**: Last Western emperor **Romulus Augustulus** deposed by Odoacer — traditional end date of the Western Roman Empire.\n\n"
            "**Eastern Empire (Byzantine)**\n"
            "* Continued for another **1,000 years** until **Constantinople** fell to the Ottoman Turks in **1453**.\n\n"
            "[HISTORY_CARD: topic: Roman Empire Peak Extent | value: ~5 million km² under Trajan (117 AD) | style: rose]"
        )
        thinking = (
            "- **Intent:** Roman Empire history query.\n"
            "- **Context:** Republic to empire transition, Pax Romana, causes of decline."
        )

    # ── The Renaissance ───────────────────────────────────────────────────────
    elif any(w in q for w in ("renaissance", "da vinci", "michelangelo", "raphael", "humanism", "botticelli", "medici")):
        heading = "The Renaissance (c. 1300–1600)"
        body = (
            "The **Renaissance** ('Rebirth') was a transformative cultural movement that began in Italy and spread across Europe, marking the transition from the Middle Ages to modernity:\n\n"
            "**Origins**\n"
            "* Began in **Florence, Italy** in the 14th century, fuelled by wealthy merchant patrons like the **Medici family**.\n"
            "* Greek and Roman classical texts were rediscovered — partly via Arab scholars — inspiring a revival of ancient learning.\n"
            "* **Humanism**: Philosophical focus on human potential, reason, and earthly life rather than solely religious doctrine.\n\n"
            "**Key Figures**\n"
            "* **Leonardo da Vinci** (1452–1519): Painter (*Mona Lisa*, *The Last Supper*), sculptor, anatomist, engineer, and inventor — the archetypal 'Renaissance man'.\n"
            "* **Michelangelo** (1475–1564): Sculptor (*David*, *Pietà*), painted the Sistine Chapel ceiling (1508–1512).\n"
            "* **Raphael** (1483–1520): *The School of Athens* — depicting Plato, Aristotle, and other classical thinkers.\n"
            "* **Galileo Galilei** (1564–1642): Confirmed heliocentrism, pioneered the scientific method.\n\n"
            "**Impact**\n"
            "* Art used **linear perspective** (Brunelleschi, 1415) to create realistic depth.\n"
            "* The printing press (Gutenberg, ~1440) spread Renaissance ideas across Europe.\n"
            "* Led directly to the **Scientific Revolution** and the **Protestant Reformation** (Luther, 1517).\n\n"
            "[HISTORY_CARD: topic: Sistine Chapel Ceiling | value: Michelangelo, 1508–1512 | style: amber]"
        )
        thinking = (
            "- **Intent:** Renaissance history query.\n"
            "- **Context:** Italian origins, humanist philosophy, artistic innovations, key figures."
        )

    # ── Scientific Revolution ─────────────────────────────────────────────────
    elif any(w in q for w in ("scientific revolution", "copernicus", "galileo", "kepler", "newton", "descartes", "bacon")):
        heading = "The Scientific Revolution (c. 1543–1687)"
        body = (
            "The **Scientific Revolution** transformed humanity's understanding of nature, establishing modern science as a discipline based on observation, experiment, and mathematics:\n\n"
            "**Key Milestones**\n"
            "* **1543**: **Nicolaus Copernicus** publishes *De revolutionibus* — proposes a **heliocentric** (Sun-centred) model of the solar system, overturning 1,400 years of Ptolemaic Earth-centred astronomy.\n"
            "* **1609–1619**: **Johannes Kepler** publishes his three laws of planetary motion — planets move in **ellipses**, not circles.\n"
            "* **1610**: **Galileo Galilei** observes Jupiter's moons with a telescope, confirming objects can orbit bodies other than Earth. Later placed under house arrest by the Inquisition.\n"
            "* **1628**: **William Harvey** describes the **circulation of blood** — overturning 1,400-year-old Galenic medicine.\n"
            "* **1687**: **Isaac Newton** publishes *Principia Mathematica* — Laws of Motion and Universal Gravitation, unifying terrestrial and celestial mechanics.\n\n"
            "**The Scientific Method**\n"
            "* **Francis Bacon** (1620) championed empirical induction — knowledge from experiment, not authority.\n"
            "* **René Descartes** introduced systematic doubt and mathematical modelling of nature.\n\n"
            "**Legacy**\n"
            "* Undermined the authority of the Church in explaining the natural world.\n"
            "* Laid foundations for the **Enlightenment**, the **Industrial Revolution**, and all modern science.\n\n"
            "[HISTORY_CARD: topic: Newton's Principia Mathematica | value: Published 1687 | style: sky]"
        )
        thinking = (
            "- **Intent:** Scientific Revolution history query.\n"
            "- **Context:** Copernican revolution, Kepler's laws, Galileo, Newton's synthesis."
        )

    # ── Age of Exploration ────────────────────────────────────────────────────
    elif any(w in q for w in ("age of exploration", "columbus", "magellan", "vasco da gama", "exploration", "new world", "conquistador")):
        heading = "The Age of Exploration (c. 1400–1600)"
        body = (
            "The **Age of Exploration** was a period of European global maritime exploration that permanently connected the world's continents:\n\n"
            "**Why it Happened**\n"
            "* European powers sought direct sea routes to Asia for spices and silk, bypassing Ottoman-controlled overland routes.\n"
            "* Advances in navigation: the **compass**, **astrolabe**, and **caravel** ships enabled deep-ocean voyaging.\n\n"
            "**Key Voyages**\n"
            "* **1488**: **Bartolomeu Dias** (Portugal) rounds the Cape of Good Hope — first European to do so.\n"
            "* **1492**: **Christopher Columbus** reaches the Caribbean (believing it to be Asia) — opens the Americas to European contact.\n"
            "* **1497–1498**: **Vasco da Gama** sails from Portugal to India, establishing the sea route that would dominate trade for centuries.\n"
            "* **1519–1522**: **Ferdinand Magellan**'s expedition (completed by Elcano) becomes the first to **circumnavigate the globe**.\n"
            "* **1519–1521**: **Hernán Cortés** conquers the Aztec Empire; **Francisco Pizarro** conquers the Inca Empire (1532).\n\n"
            "**The Columbian Exchange**\n"
            "* The transfer of plants, animals, diseases, and people between the Old and New Worlds.\n"
            "* **Crops from Americas to Europe**: potatoes, tomatoes, maize, cacao, tobacco.\n"
            "* **Diseases from Europe to Americas**: smallpox, measles — killed up to **90%** of indigenous populations.\n\n"
            "[HISTORY_CARD: topic: Columbus's First Voyage | value: August–October 1492 | style: amber]"
        )
        thinking = (
            "- **Intent:** Age of Exploration history query.\n"
            "- **Context:** Navigation technology, key voyages, the Columbian Exchange and its consequences."
        )

    # ── Cold War ──────────────────────────────────────────────────────────────
    elif any(w in q for w in ("cold war", "soviet union", "ussr", "nato", "berlin wall", "cuban missile", "iron curtain", "communism", "containment")):
        heading = "The Cold War (1947–1991)"
        body = (
            "The **Cold War** was a geopolitical rivalry between the **United States** and the **Soviet Union** (USSR), fought through proxy wars, arms races, and ideological competition — never direct military conflict between the two superpowers:\n\n"
            "**Origins**\n"
            "* After WWII, the US and USSR emerged as rival superpowers with incompatible ideologies: **liberal democracy/capitalism** vs. **communist totalitarianism**.\n"
            "* Winston Churchill's **'Iron Curtain' speech** (1946) defined the division of Europe.\n"
            "* **Truman Doctrine** (1947): US pledged to contain the spread of communism globally.\n\n"
            "**Key Events**\n"
            "* **1949**: USSR tests its first atomic bomb; China becomes communist.\n"
            "* **1950–1953**: Korean War — first major proxy conflict.\n"
            "* **1957**: USSR launches **Sputnik** — sparks the Space Race.\n"
            "* **1961**: **Berlin Wall** built, dividing East and West Germany.\n"
            "* **1962**: **Cuban Missile Crisis** — 13 days in October brought the world closest to nuclear war. Ended when USSR withdrew missiles from Cuba.\n"
            "* **1965–1975**: Vietnam War — US-backed South Vietnam vs. communist North Vietnam.\n"
            "* **1979–1989**: Soviet-Afghan War — USSR's 'Vietnam'.\n\n"
            "**End of the Cold War**\n"
            "* **Mikhail Gorbachev**'s reforms (glasnost and perestroika) loosened Soviet control.\n"
            "* **Berlin Wall falls**: November 9, **1989**.\n"
            "* **USSR dissolves**: December 25, **1991** — 15 independent states formed.\n\n"
            "[HISTORY_CARD: topic: Cuban Missile Crisis | value: October 16–28, 1962 | style: rose]"
        )
        thinking = (
            "- **Intent:** Cold War history query.\n"
            "- **Context:** US-USSR ideological rivalry, key crises, arms race, eventual dissolution."
        )

    # ── Space Race ────────────────────────────────────────────────────────────
    elif any(w in q for w in ("space race", "sputnik", "apollo", "apollo 11", "moon landing", "yuri gagarin", "neil armstrong", "nasa")):
        heading = "The Space Race: From Sputnik to Apollo 11"
        body = (
            "The **Space Race** (1957–1969) was a Cold War competition between the USA and USSR to achieve supremacy in spaceflight:\n\n"
            "**Early Soviet Leads**\n"
            "* **October 4, 1957**: USSR launches **Sputnik 1** — Earth's first artificial satellite. A beach-ball-sized sphere beeping from orbit shocked the West.\n"
            "* **November 3, 1957**: **Sputnik 2** carries **Laika** — first animal in orbit.\n"
            "* **April 12, 1961**: **Yuri Gagarin** (USSR) completes the first human spaceflight — a 108-minute orbit aboard **Vostok 1**.\n\n"
            "**America Responds**\n"
            "* **May 5, 1961**: **Alan Shepard** becomes the first American in space (15-minute suborbital flight).\n"
            "* **May 25, 1961**: President Kennedy commits to landing a man on the Moon before the decade's end.\n"
            "* **February 20, 1962**: **John Glenn** — first American to orbit Earth.\n\n"
            "**Apollo 11: The Moon Landing**\n"
            "* **July 16, 1969**: Launch from Kennedy Space Center, Florida.\n"
            "* **July 20, 1969 at 20:17 UTC**: **Neil Armstrong** and **Buzz Aldrin** land the Lunar Module *Eagle* in the Sea of Tranquility.\n"
            "* **20:56 UTC**: Armstrong steps onto the Moon — *'That's one small step for [a] man, one giant leap for mankind.'*\n"
            "* **Michael Collins** orbited above in the Command Module.\n"
            "* They collected **21.5 kg** of lunar rock samples and planted a US flag.\n"
            "* Total Apollo programme: **12 astronauts** walked on the Moon across **6 successful landings** (Apollo 11, 12, 14, 15, 16, 17).\n\n"
            "**Legacy**: Demonstrated that human ingenuity could achieve seemingly impossible goals; drove advances in computing, materials science, and telecommunications.\n\n"
            "[HISTORY_CARD: topic: Apollo 11 Moon Landing | value: July 20, 1969, 20:17 UTC | style: indigo]"
        )
        thinking = (
            "- **Intent:** Space Race history query.\n"
            "- **Context:** Cold War context, Sputnik shock, Apollo 11 mission details."
        )

    # ── Invention of the Internet ──────────────────────────────────────────────
    elif any(w in q for w in ("internet", "arpanet", "world wide web", "www", "tim berners-lee", "tcp/ip")):
        heading = "The Invention of the Internet"
        body = (
            "The Internet evolved over decades from a military research network to a global communication system:\n\n"
            "**ARPANET (1969)**\n"
            "* Funded by the US Department of Defense's ARPA (Advanced Research Projects Agency).\n"
            "* **October 29, 1969**: First message sent between UCLA and Stanford — only 'LO' (the system crashed before completing 'LOGIN').\n"
            "* Designed to survive nuclear attack by routing data through multiple paths.\n\n"
            "**TCP/IP Protocol (1983)**\n"
            "* **Vint Cerf** and **Bob Kahn** designed **TCP/IP** (Transmission Control Protocol/Internet Protocol) — the common language allowing different networks to interconnect.\n"
            "* January 1, 1983: ARPANET switched to TCP/IP — often called the internet's official birthday.\n\n"
            "**The World Wide Web (1991)**\n"
            "* **Tim Berners-Lee** (CERN) invented the **WWW** in 1989, publishing the first website on **August 6, 1991**.\n"
            "* The Web uses **HTTP**, **HTML**, and **URLs** — a layer running on top of the Internet.\n"
            "* **Mosaic** (1993): First graphical web browser — made the web accessible to ordinary people.\n\n"
            "**Growth**\n"
            "* **1995**: ~16 million users worldwide.\n"
            "* **2024**: ~**5.4 billion** users (67% of the global population).\n"
            "* Transformed commerce, communication, entertainment, science, and politics.\n\n"
            "[HISTORY_CARD: topic: First Website | value: Tim Berners-Lee, August 6, 1991 | style: sky]"
        )
        thinking = (
            "- **Intent:** Internet history and invention query.\n"
            "- **Context:** ARPANET origins, TCP/IP standardisation, WWW invention by Berners-Lee."
        )

    # ── Manhattan Project ──────────────────────────────────────────────────────
    elif any(w in q for w in ("manhattan project", "atomic bomb", "nuclear bomb", "hiroshima", "nagasaki", "oppenheimer")):
        heading = "The Manhattan Project (1942–1946)"
        body = (
            "The **Manhattan Project** was the US-led wartime programme to develop the world's first nuclear weapons:\n\n"
            "**Origins**\n"
            "* Driven by fear that Nazi Germany was developing its own atomic bomb.\n"
            "* **Einstein-Szilard Letter** (August 2, 1939): Einstein warned President Roosevelt that uranium chain reactions could produce enormously powerful bombs.\n"
            "* Formally launched **December 1941**, following the Pearl Harbor attack.\n\n"
            "**Scale & Secrecy**\n"
            "* Employed over **130,000 people** at peak; costed ~**$2 billion** ($27 billion today).\n"
            "* Sites included Los Alamos (NM), Oak Ridge (TN), and Hanford (WA) — most workers didn't know what they were building.\n"
            "* **J. Robert Oppenheimer** directed the Los Alamos Laboratory and the bomb's design.\n\n"
            "**The Trinity Test**\n"
            "* **July 16, 1945**: First nuclear detonation at Jornada del Muerto desert, New Mexico — a plutonium implosion device ('Gadget') with ~21 kilotons yield.\n"
            "* Oppenheimer recalled the Bhagavad Gita: *'Now I am become Death, the destroyer of worlds.'*\n\n"
            "**Hiroshima & Nagasaki**\n"
            "* **August 6, 1945**: 'Little Boy' (uranium bomb) dropped on **Hiroshima** — ~70,000 killed immediately, ~140,000 by year's end.\n"
            "* **August 9, 1945**: 'Fat Man' (plutonium bomb) dropped on **Nagasaki** — ~40,000 killed immediately.\n"
            "* Japan surrendered **August 15, 1945** — ending WWII.\n\n"
            "**Legacy**: Began the nuclear age, the Cold War arms race, and ongoing debates about nuclear deterrence and disarmament.\n\n"
            "[HISTORY_CARD: topic: Trinity Test | value: July 16, 1945 — First Nuclear Detonation | style: rose]"
        )
        thinking = (
            "- **Intent:** Manhattan Project history query.\n"
            "- **Context:** WWII context, project scale, Trinity test, Hiroshima and Nagasaki."
        )

    # ── Printing Press ────────────────────────────────────────────────────────
    elif any(w in q for w in ("printing press", "gutenberg", "movable type", "printing")):
        heading = "The Printing Press & Its Impact (c. 1440)"
        body = (
            "**Johannes Gutenberg**'s movable-type printing press (~1440) was arguably the most transformative invention in the history of communication:\n\n"
            "**The Invention**\n"
            "* Gutenberg combined:\n"
            "  - **Movable metal type** (individual reusable letter blocks)\n"
            "  - **Oil-based ink** (durable, consistent)\n"
            "  - An adapted **wine/olive press** mechanism\n"
            "* **Gutenberg Bible** (c. 1455): The first major book printed in Europe using this technology — ~180 copies printed.\n\n"
            "**Before the Press**\n"
            "* Books were hand-copied by monks — a Bible took ~1–2 years to produce.\n"
            "* Only wealthy institutions could afford books; literacy was rare.\n\n"
            "**Immediate Impact**\n"
            "* Printing speed: A press could produce **3,600 pages per day** vs. ~4 pages hand-copied.\n"
            "* By 1500, over **20 million books** had been printed across Europe.\n"
            "* Cost of books dropped dramatically — knowledge became accessible to ordinary people.\n\n"
            "**Long-Term Consequences**\n"
            "* **Protestant Reformation** (1517): Martin Luther's 95 Theses spread rapidly in print, challenging the Catholic Church's monopoly on religious interpretation.\n"
            "* **Scientific Revolution**: Researchers could share and build on each other's work universally.\n"
            "* **Rise of literacy**: Growing demand for books drove mass education.\n"
            "* **Standardisation of languages**: Printed books helped standardise national languages.\n"
            "* Some historians argue it was the most significant catalyst for the **modern world**.\n\n"
            "[HISTORY_CARD: topic: Gutenberg's Printing Press | value: c. 1440, Mainz, Germany | style: amber]"
        )
        thinking = (
            "- **Intent:** Printing press historical impact query.\n"
            "- **Context:** Gutenberg's mechanism, Reformation, Scientific Revolution, spread of literacy."
        )

    # ── George Washington / Founding Era ──────────────────────────────────────
    elif any(w in q for w in ("washington", "founding", "hamilton", "jefferson")):
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

    # ── Lincoln / Civil War ────────────────────────────────────────────────────
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

    # ── FDR / Great Depression ────────────────────────────────────────────────
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

    # ── Party Systems ─────────────────────────────────────────────────────────
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
