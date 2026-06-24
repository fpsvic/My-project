LANG_HISTORY: dict[str, str] = {
    "python": "Python was conceived in the late 1980s by Guido van Rossum in the Netherlands as an ABC successor. Officially released in 1991, it was named after Monty Python's Flying Circus. It emphasizes code readability ('Zen of Python') and dominates data science and ML.",
    "java": "Java was developed by James Gosling and team at Sun Microsystems in 1995. Originally called Oak, it was retargeted for the Web under the slogan 'Write Once, Run Anywhere' (WORA) using JVM bytecode execution. It dominates enterprise systems.",
    "javascript": "JavaScript was designed in 1995 by Brendan Eich at Netscape in just 10 days under the codename Mocha. Rebranded to piggyback on Java's popularity, it was standardized under ECMAScript and became the ubiquitous engine of the modern web.",
    "typescript": "TypeScript was designed by Anders Hejlsberg at Microsoft in 2012 to solve JavaScript scalability challenges. It is a typed superset compiling directly to JS, adding static typings without any runtime overhead.",
    "golang": "Go (Golang) was designed at Google in 2007 by Robert Griesemer, Rob Pike, and Ken Thompson. Released in 2009, it addresses slow compilations and systems complexity with goroutines, channels, and zero-overhead binary builds.",
    "cpp": "C++ was created by Bjarne Stroustrup in 1979 at Bell Laboratories. Originally 'C with Classes', it added Simula's abstractions to C's bare-metal speed. Standardized in 1983, it runs low-latency systems and game engines.",
    "c": "C was designed by Dennis Ritchie at Bell Labs between 1969 and 1973 to rewrite Unix. It provided structured paradigms with a direct mapping to assembly, making it the most influential foundation for OS kernels and firmware.",
    "csharp": "C# was designed by Anders Hejlsberg at Microsoft in 2000 as part of .NET. Designed as a modern object-oriented competitor to Java, it runs enterprise backends, desktop apps, and Unity games today.",
    "rust": "Rust began as a personal research project by Graydon Hoare in 2006, sponsored by Mozilla in 2009 to replace C++ browser engines. Officially released in 2015, it guarantees memory and thread safety at compile-time without a GC.",
    "swift": "Swift was developed at Apple by Chris Lattner beginning in 2010. Released in 2014 as a modern successor to Objective-C, it delivers compiled systems-level speed with a clean script-like syntax.",
    "kotlin": "Kotlin was designed by JetBrains in 2010 and named after Kotlin Island. Built to solve Java pain points while remaining 100% interoperable, it became Google's preferred language for Android in 2017.",
    "lua": "Lua was created in 1993 by Roberto Ierusalimschy and team in Brazil. Designed as a lightweight, embeddable C-compatible scripting language, its tiny memory footprint made it an industry standard for games and IoT.",
    "luau": "Luau is Roblox's statically typed derivative of Lua 5.1. It adds a robust type system, aggressive compiler optimizations, and specialized vector instructions to safely run millions of concurrent game scripts.",
    "matlab": "MATLAB was designed by Cleve Moler in the late 1970s to give students easy, interactive access to LINPACK/EISPACK. Commercialized by MathWorks in 1984, it is the global standard for matrix computation and scientific analysis.",
    "r": "R was created by Ross Ihaka and Robert Gentleman in 1993 in New Zealand. As an open-source dialect of S, it is specifically engineered for statistical computing, data analysis, and advanced graphics.",
    "ruby": "Ruby was designed by Yukihiro Matsumoto in 1995. Focused on developer happiness and human readability, it gained global adoption in the mid-2000s through the Ruby on Rails web framework.",
    "php": "PHP (PHP: Hypertext Preprocessor) was created by Rasmus Lerdorf in 1994 as a set of CGI scripts. It evolved into one of the most widely deployed server-side web languages, powering WordPress and Facebook's early stack.",
    "sql": "SQL (Structured Query Language) was developed by IBM researchers Donald Chamberlin and Raymond Boyce in the early 1970s. Standardized in 1987, it remains the universal language for relational databases.",
    "html": "HTML was invented by Tim Berners-Lee in 1991 at CERN to share hypertext documents. Standardized by the W3C, HTML5 (2014) introduced native video, canvas, local storage, and WebSocket APIs.",
    "css": "CSS was proposed by Håkon Wium Lie in 1994 and standardized in 1996. It separates document presentation from content, enabling responsive layouts, animations, and theming across the web.",
    "haskell": "Haskell was defined by an academic committee in 1990 as a purely functional lazy language. Named after logician Haskell Curry, it pioneered type classes, monads, and has deeply influenced modern language design.",
    "scala": "Scala was created by Martin Odersky at EPFL in 2003. It unifies object-oriented and functional programming on the JVM, famously powering Twitter's back-end infrastructure.",
    "elixir": "Elixir was created by José Valim in 2012, built on the Erlang VM (BEAM). It inherits Erlang's legendary fault tolerance and massive concurrency while offering a friendly Ruby-like syntax.",
}

LANG_HELLO_WORLD: dict[str, str] = {
    "javascript": 'console.log("Hello, World!");',
    "typescript": 'const greeting: string = "Hello, World!";\nconsole.log(greeting);',
    "java": 'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
    "golang": 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}',
    "cpp": '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
    "c": '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
    "csharp": 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}',
    "kotlin": 'fun main() {\n    println("Hello, World!")\n}',
    "lua": 'print("Hello, World!")',
    "luau": 'print("Hello, World!")',
    "matlab": "disp('Hello, World!');",
    "python": 'print("Hello, World!")',
    "r": 'print("Hello, World!")',
    "ruby": 'puts "Hello, World!"',
    "rust": 'fn main() {\n    println!("Hello, World!");\n}',
    "swift": 'print("Hello, World!")',
    "php": '<?php\necho "Hello, World!";\n?>',
    "sql": "SELECT 'Hello, World!' AS greeting;",
    "html": '<!DOCTYPE html>\n<html>\n<body>\n  <h1>Hello, World!</h1>\n</body>\n</html>',
    "haskell": 'main :: IO ()\nmain = putStrLn "Hello, World!"',
    "scala": 'object HelloWorld extends App {\n  println("Hello, World!")\n}',
    "elixir": 'IO.puts("Hello, World!")',
}

SPACE_KEYWORDS: list[str] = [
    "sun", "earth", "moon", "mars", "space", "astronom", "galaxy", "universe",
    "distance", "miles", "gravity", "orbit", "planet", "speed of light",
    "cosmic", "sol", "luna", "star", "solar", "venus", "saturn", "jupiter",
    "neptune", "uranus", "mercury", "milky way", "black hole", "nebula",
    "supernova", "neutron star", "dark matter", "dark energy", "big bang",
    "light year", "parsec", "hubble", "telescope", "asteroid", "comet",
    "meteor", "atmosphere", "exoplanet", "wormhole",
]

EARTH_KEYWORDS: list[str] = [
    "rock", "mineral", "stone", "geolog", "petrolog", "basalt", "granite",
    "sediment", "metamorph", "igneous", "volcano", "lava", "magma", "magmatic",
    "caldera", "tectonic", "plate", "ring of fire", "subduction", "trench",
    "mariana", "ocean", "underwater", "hydrothermal", "vent", "black smoker",
    "seafloor", "crust", "mantle", "mohs", "earthquake", "seismic", "richter",
    "fossil", "erosion", "glacier", "ice age", "carbon dating",
]

ADVANCED_SCIENCE_KEYWORDS: list[str] = [
    "quantum", "physics", "planck", "boltzmann", "chemistry", "element",
    "carbon", "noble", "electroneg", "dna", "gene", "cell", "transcription",
    "biology", "golden ratio", "phi", "euler", "irrational",
    "einstein", "relativity", "e=mc", "photon", "electron", "proton", "neutron",
    "atom", "molecule", "compound", "periodic", "mendeleev", "entropy",
    "thermodynamics", "maxwell", "faraday", "newton", "gravity constant",
    "avogadro", "mole", "bohr", "schrodinger", "heisenberg", "uncertainty",
]

POLITICAL_KEYWORDS: list[str] = [
    "washington", "president", "lincoln", "fdr", "new deal", "civil war",
    "party", "whig", "federalist", "constitution", "politic", "align",
    "congress", "senate", "amendment", "declaration", "jefferson", "adams",
    "hamilton", "madison", "jackson", "grant", "wilson", "eisenhower",
    "kennedy", "reagan", "clinton", "obama", "trump", "biden",
]

PROTECTED_ENGLISH_WORDS: list[str] = [
    "when", "what", "with", "where", "which", "while", "make", "game", "play",
    "from", "about", "your", "then", "than", "them", "they", "this", "that",
    "there", "have", "some", "more", "like", "will", "would", "could", "should",
    "tell", "show", "find", "solve", "how", "who", "whom", "whose", "why",
    "want", "went", "well", "were", "been", "does", "done", "once",
]

HIGH_CONFIDENCE_KEYWORDS: list[str] = [
    "volcano", "volcanoes", "caldera", "subduction", "trench", "mariana",
    "ocean", "hydrothermal", "vent", "chemosynthesis", "lithosphere", "basalt",
    "granite", "calculus", "trigonometry", "derivative", "integral",
    "differentiation", "integration", "quantum", "physics", "planck",
    "boltzmann", "electronegativity", "transcription", "washington", "president",
    "lincoln", "roosevelt", "constitution", "federalist", "whig", "python",
    "javascript", "typescript", "golang", "kotlin", "rust", "rarest",
    "fastest", "rocks", "stone",
]

# ─── General knowledge ────────────────────────────────────────────────────────

GENERAL_KNOWLEDGE: dict[str, str] = {
    # Biology
    "how many bones": "### Human Skeleton\n\nAn adult human body has **206 bones**. Babies are born with about **270 bones** — many fuse together during childhood and adolescence.\n\n**Major bone groups:**\n- Skull: 22 bones\n- Vertebral column (spine): 33 vertebrae\n- Ribcage: 24 ribs + sternum\n- Upper limbs: 64 bones\n- Lower limbs: 62 bones\n- Pelvis: 4 bones",

    "how many chromosomes": "### Human Chromosomes\n\nHumans have **46 chromosomes** arranged in **23 pairs**. Pair 23 determines biological sex: **XX** (female) or **XY** (male).\n\nChromosomes carry DNA genes that encode proteins and traits. Abnormal counts (aneuploidy) cause conditions such as Down syndrome (trisomy 21 = 47 chromosomes).",

    "how many cells": "### Cells in the Human Body\n\nThe human body contains approximately **37.2 trillion cells** (3.72 × 10¹³). The most abundant cells are **red blood cells** (~70% of all cells). Neurons, while only ~86 billion, are among the largest and most complex.",

    # Geography
    "largest country": "### World's Largest Countries by Area\n\n1. 🇷🇺 **Russia** — 17.1 million km²\n2. 🇨🇦 **Canada** — 10.0 million km²\n3. 🇺🇸 **United States** — 9.8 million km²\n4. 🇨🇳 **China** — 9.6 million km²\n5. 🇧🇷 **Brazil** — 8.5 million km²",

    "tallest mountain": "### World's Highest Mountains\n\n1. **Mount Everest** (Nepal/Tibet) — **8,848.86 m** (29,031.7 ft) — highest point above sea level\n2. **K2** (Pakistan/China) — 8,611 m\n3. **Kangchenjunga** (Nepal/India) — 8,586 m\n\nIf measured from Earth's center, **Chimborazo** (Ecuador) wins at 6,384 km from Earth's core due to equatorial bulge.",

    "deepest ocean": "### Deepest Points in the Ocean\n\n**Challenger Deep** in the **Mariana Trench** (Pacific Ocean) is the deepest known point: **10,935 meters (35,876 ft)** below sea level.\n\n[EARTH_CARD: topic: Challenger Deep, Mariana Trench | value: 10,935 m depth | style: sky]",

    "longest river": "### World's Longest Rivers\n\n1. **Nile River** (Africa) — **6,650 km** (4,130 mi)\n2. **Amazon River** (South America) — 6,400 km\n3. **Yangtze River** (China) — 6,300 km\n\nNote: The Amazon vs Nile debate is ongoing — some measurements give the Amazon the edge depending on headwater definitions.",

    "capital of": "I can help with world capitals! Here are some:\n\n- 🇫🇷 France → **Paris**\n- 🇩🇪 Germany → **Berlin**\n- 🇯🇵 Japan → **Tokyo**\n- 🇦🇺 Australia → **Canberra**\n- 🇧🇷 Brazil → **Brasília**\n- 🇨🇦 Canada → **Ottawa**\n- 🇲🇽 Mexico → **Mexico City**\n- 🇨🇳 China → **Beijing**\n- 🇮🇳 India → **New Delhi**\n- 🇷🇺 Russia → **Moscow**",

    # Animals
    "fastest animal": "### World's Fastest Animals\n\n**Air:** 🦅 **Peregrine Falcon** — **389 km/h (242 mph)** in a dive (fastest animal alive)\n**Land:** 🐆 **Cheetah** — **112 km/h (70 mph)** over short bursts\n**Water:** 🐬 **Black Marlin** — **129 km/h (80 mph)**\n**Insect:** **Dragonfly** — ~97 km/h",

    "largest animal": "### World's Largest Animals\n\n**Living:** 🐋 **Blue Whale** — up to **33 meters (110 ft)** long, weighing **180 metric tons** — the largest animal ever known to exist.\n\n**Land animal:** African Bush Elephant — up to 6,000 kg\n**Largest reptile:** Saltwater Crocodile — up to 1,000 kg",

    "smartest animal": "### Most Intelligent Animals\n\n1. **Great Apes** (chimpanzees, bonobos, gorillas, orangutans) — closest cognitive relatives to humans\n2. **Dolphins** — self-aware, complex language, tool use\n3. **Elephants** — grief, empathy, mirror self-recognition\n4. **Crows & Ravens** — use tools, plan for the future, solve multi-step puzzles\n5. **Octopuses** — remarkable problem solving despite a distributed nervous system",

    # Technology
    "what is ai": "### Artificial Intelligence\n\n**AI** is the simulation of human intelligence processes by machines. Key branches:\n\n- **Machine Learning (ML)** — systems that learn from data without explicit programming\n- **Deep Learning** — neural networks with many layers (powers image recognition, LLMs)\n- **Natural Language Processing (NLP)** — understanding and generating human language\n- **Computer Vision** — teaching machines to interpret visual input\n- **Reinforcement Learning** — agents that learn by trial-and-error with reward signals\n\nModern LLMs like GPT-4 and Claude use transformer architectures trained on massive text datasets.",

    "what is machine learning": "### Machine Learning\n\nMachine Learning is a subset of AI where models learn patterns from data.\n\n**3 main types:**\n- **Supervised learning** — trained on labeled examples (e.g. spam detection)\n- **Unsupervised learning** — finds hidden patterns in unlabeled data (e.g. clustering)\n- **Reinforcement learning** — agents maximize rewards through environment interaction\n\n**Popular algorithms:** Linear Regression, Decision Trees, Random Forests, SVMs, Neural Networks.",

    "what is blockchain": "### Blockchain\n\nA **blockchain** is a distributed, immutable ledger where data is stored in chronologically linked blocks. Each block contains:\n- Transaction data\n- A cryptographic hash of the previous block\n- A timestamp\n\n**Key properties:** Decentralized, transparent, tamper-resistant.\n**Use cases:** Cryptocurrencies (Bitcoin, Ethereum), smart contracts, supply chain tracking, NFTs.",

    "what is http": "### HTTP / HTTPS\n\n**HTTP** (HyperText Transfer Protocol) is the foundation of web communication — a request-response protocol between clients and servers.\n\n**HTTPS** = HTTP + **TLS/SSL encryption**.\n\n**Common methods:**\n```\nGET    — retrieve data\nPOST   — submit data\nPUT    — update resource\nDELETE — remove resource\nPATCH  — partial update\n```",

    "what is an api": "### API (Application Programming Interface)\n\nAn **API** is a contract that defines how software components communicate.\n\n**REST API** — uses HTTP methods, returns JSON/XML, stateless\n**GraphQL** — single endpoint, client specifies exact data shape\n**WebSocket** — persistent bidirectional connection\n**gRPC** — high-performance binary protocol by Google\n\n```python\nimport requests\nres = requests.get('https://api.example.com/data')\nprint(res.json())\n```",

    "what is the internet": "### The Internet\n\nThe Internet is a **global network of interconnected computers** communicating via the **TCP/IP protocol suite**.\n\n**Key layers:**\n1. **Physical** — fiber optic cables, copper, wireless radio\n2. **IP layer** — routing packets between networks\n3. **TCP layer** — reliable ordered delivery\n4. **Application** — HTTP, DNS, SMTP, FTP\n\nThe **Web** (WWW) is just one application running on the Internet — others include email, VoIP, and peer-to-peer file sharing.",

    # Math facts
    "what is pi": "### π (Pi)\n\n**π ≈ 3.14159265358979...**\n\nPi is the ratio of a circle's circumference to its diameter — an **irrational and transcendental** number.\n\n[MATH_CARD: formula: C = 2πr | result: π ≈ 3.14159265... | style: indigo]\n\n**Fun facts:**\n- Pi has been computed to over **100 trillion digits**\n- It appears in probability (Buffon's needle), Fourier analysis, and quantum mechanics\n- March 14 (3/14) is celebrated as Pi Day",

    "what is euler": "### Euler's Number (e)\n\n**e ≈ 2.71828182845904...**\n\nEuler's number is the base of the **natural logarithm** and defines continuous exponential growth.\n\n[MATH_CARD: formula: e = lim(1 + 1/n)ⁿ as n→∞ | result: e ≈ 2.71828... | style: indigo]\n\n**Euler's Identity:** e^(iπ) + 1 = 0 — often called the most beautiful equation in mathematics.",

    "fibonacci": "### Fibonacci Sequence\n\n**0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89...**\n\nEach number is the sum of the two preceding numbers. Named after Italian mathematician **Leonardo Fibonacci** (c. 1202).\n\nThe ratio of consecutive Fibonacci numbers converges to the **Golden Ratio φ ≈ 1.6180339887...**\n\n```python\ndef fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n```",

    "pythagorean": "### Pythagorean Theorem\n\nFor a right triangle with legs **a** and **b** and hypotenuse **c**:\n\n[MATH_CARD: formula: a² + b² = c² | result: c = √(a² + b²) | style: indigo]\n\n**Example:** a=3, b=4 → c = √(9+16) = √25 = **5**\n\nProved by Euclid (~300 BC) but known to Babylonians 1,000 years earlier. There are over **370 known proofs**.",

    # Health / body
    "normal body temperature": "### Normal Body Temperature\n\n**98.6°F (37°C)** is the classic average, but healthy temperatures range from **97°F to 99°F (36.1–37.2°C)**.\n\n- **Fever:** ≥100.4°F (38°C)\n- **Hypothermia:** <95°F (35°C)\n- Temperature varies by time of day (lowest ~6 AM, highest ~4–6 PM)",

    "blood type": "### ABO Blood Types\n\n| Type | Antigen | Can donate to | Can receive from |\n|------|---------|--------------|------------------|\n| A | A | A, AB | A, O |\n| B | B | B, AB | B, O |\n| AB | A+B | AB only | All types (universal recipient) |\n| O | None | All types (universal donor) | O only |\n\n**Rh factor** (+/-) adds another dimension (e.g. O+ is the most common type).",

    # Universe / physics
    "age of universe": "### Age of the Universe\n\nThe universe is approximately **13.8 billion years old** (13.787 ± 0.020 Gyr), estimated from the cosmic microwave background radiation (CMB) measured by the Planck satellite.\n\n[COSMIC_CARD: formula: t₀ = 1/H₀ × correction factor | result: ~13.8 billion years | style: indigo]",

    "how many stars": "### Stars in the Universe\n\n- **Milky Way galaxy:** ~**200–400 billion** stars\n- **Observable universe:** estimated **10²⁴ stars** (1 septillion)\n- That's more stars than grains of sand on all of Earth's beaches combined.",

    # Famous people
    "who is einstein": "### Albert Einstein (1879–1955)\n\nGerman-born theoretical physicist who developed the **Theory of Relativity**.\n\n**Key contributions:**\n- **Special Relativity** (1905): E = mc² — mass-energy equivalence\n- **General Relativity** (1915): gravity curves spacetime\n- **Photoelectric Effect** — foundation of quantum mechanics (Nobel Prize 1921)\n- **Brownian Motion** — evidence for atoms\n\nBorn in Ulm, Germany, he emigrated to the US in 1933 and worked at Princeton's Institute for Advanced Study.",

    "who is newton": "### Isaac Newton (1643–1727)\n\nEnglish mathematician and physicist who laid foundations for classical mechanics.\n\n**Key contributions:**\n- **Laws of Motion** (3 laws describing force, mass, acceleration)\n- **Universal Gravitation** — F = Gm₁m₂/r²\n- **Calculus** (co-invented with Leibniz)\n- **Optics** — light prism decomposition\n\nHis *Principia Mathematica* (1687) is considered one of the most influential scientific works ever written.",

    "who is tesla": "### Nikola Tesla (1856–1943)\n\nSerbian-American inventor and electrical engineer.\n\n**Key contributions:**\n- **AC (Alternating Current)** electrical system — now the global standard\n- **Tesla Coil** — high-voltage resonant transformer\n- **Induction Motor** — drives modern industrial equipment\n- **Radio** — disputed priority with Marconi\n- **X-ray** research, fluorescent lighting, wireless power transmission\n\nWorked for Edison before famously feuding in the 'War of Currents'.",

    # World records
    "fastest computer": "### World's Fastest Supercomputers (2024)\n\n1. **Frontier** (Oak Ridge, USA) — **1.194 ExaFLOPS** (10¹⁸ floating-point ops/sec)\n2. **Aurora** (Argonne, USA) — ~1.012 ExaFLOPS\n3. **Eagle** (Microsoft Azure) — 561.2 PetaFLOPS\n\n1 ExaFLOP = 1 quintillion calculations per second.",

    "oldest language": "### World's Oldest Languages\n\n- **Tamil** — ~5,000 years old, still widely spoken (75M+ speakers)\n- **Sanskrit** — ~3,500 years, ancestor of many Indo-European languages\n- **Hebrew** — ~3,000 years, revived as a modern language\n- **Greek** — continuous written record since ~800 BC\n- **Sumerian** — oldest *written* language (~3,100 BC), now extinct\n\nProto-languages like Proto-Indo-European are estimated to be 6,000–8,000 years old but were never written.",

    "world population": "### World Population\n\nAs of 2024, the world population is approximately **8.1 billion people**.\n\n**Top 5 most populous countries:**\n1. 🇮🇳 India — ~1.44 billion\n2. 🇨🇳 China — ~1.41 billion\n3. 🇺🇸 USA — ~340 million\n4. 🇮🇩 Indonesia — ~280 million\n5. 🇵🇰 Pakistan — ~240 million",

    # Food / cooking
    "how to boil an egg": "### How to Boil an Egg\n\n1. Place egg(s) in a pot, cover with cold water (1 inch above)\n2. Bring to a **full rolling boil** over high heat\n3. Reduce to medium, set timer:\n   - **Soft boiled** (runny yolk): **6–7 minutes**\n   - **Medium** (jammy yolk): **9–10 minutes**\n   - **Hard boiled** (firm yolk): **12–13 minutes**\n4. Transfer immediately to an ice bath for 5 min to stop cooking\n5. Peel under running water\n\n**Altitude note:** Water boils below 100°C at altitude — add 1 minute per 1,000m above sea level.",
}


# ─── Coding help ──────────────────────────────────────────────────────────────

CODING_HELP: dict[str, str] = {
    "what is a variable": "### Variables in Programming\n\nA **variable** is a named container that stores a value in memory.\n\n```python\n# Python\nname = \"Alice\"\nage = 30\npi = 3.14159\n```\n```javascript\n// JavaScript\nlet name = 'Alice';\nconst age = 30;\nvar pi = 3.14159;\n```\n\n**Types:** integer, float, string, boolean, list/array, object/dict.",

    "what is a function": "### Functions in Programming\n\nA **function** is a reusable block of code that performs a specific task.\n\n```python\n# Python\ndef greet(name: str) -> str:\n    return f'Hello, {name}!'\n\nprint(greet('World'))  # → Hello, World!\n```\n```javascript\n// JavaScript\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\nconsole.log(greet('World')); // → Hello, World!\n```",

    "what is a loop": "### Loops in Programming\n\nLoops repeat a block of code.\n\n```python\n# Python — for loop\nfor i in range(5):\n    print(i)  # 0 1 2 3 4\n\n# While loop\nn = 10\nwhile n > 0:\n    n -= 3\n```\n```javascript\n// JavaScript — for loop\nfor (let i = 0; i < 5; i++) {\n    console.log(i);\n}\n```",

    "what is recursion": "### Recursion\n\nRecursion is when a function calls itself.\n\n```python\ndef factorial(n: int) -> int:\n    if n <= 1:  # base case\n        return 1\n    return n * factorial(n - 1)  # recursive call\n\nprint(factorial(5))  # → 120\n```\n\n**Key rule:** Every recursive function needs a **base case** to stop the infinite loop.\n\n**Classic uses:** tree traversal, quicksort, Fibonacci, fractal rendering.",

    "what is object oriented": "### Object-Oriented Programming (OOP)\n\nOOP organizes code around **objects** — bundles of data (attributes) and behavior (methods).\n\n```python\nclass Dog:\n    def __init__(self, name: str, breed: str):\n        self.name = name\n        self.breed = breed\n\n    def bark(self) -> str:\n        return f'{self.name} says: Woof!'\n\nrex = Dog('Rex', 'Labrador')\nprint(rex.bark())  # → Rex says: Woof!\n```\n\n**4 pillars:** Encapsulation, Inheritance, Polymorphism, Abstraction.",

    "what is a api": "### APIs\n\nAn **API** (Application Programming Interface) is a set of rules for how software components communicate.\n\n```python\nimport requests\n\nres = requests.get('https://api.github.com/users/torvalds')\ndata = res.json()\nprint(data['public_repos'])  # Linus Torvalds's public repos\n```\n\n**REST API conventions:**\n- `GET /users` — list all\n- `GET /users/1` — get one\n- `POST /users` — create\n- `PUT /users/1` — replace\n- `DELETE /users/1` — delete",

    "what is git": "### Git\n\nGit is a **distributed version control system** created by Linus Torvalds in 2005.\n\n```bash\ngit init                    # start a repo\ngit add .                   # stage all changes\ngit commit -m 'message'     # save snapshot\ngit push origin main        # upload to remote\ngit pull origin main        # download updates\ngit branch feature-x        # new branch\ngit checkout feature-x      # switch branch\ngit merge feature-x         # merge into current\n```",

    "what is docker": "### Docker\n\nDocker packages applications and their dependencies into **containers** — lightweight, portable, isolated environments.\n\n```dockerfile\n# Dockerfile\nFROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\"]\n```\n\n```bash\ndocker build -t myapp .\ndocker run -p 8000:8000 myapp\n```",

    "what is sql": "### SQL (Structured Query Language)\n\nSQL queries relational databases.\n\n```sql\n-- Create a table\nCREATE TABLE users (\n    id   INTEGER PRIMARY KEY,\n    name TEXT    NOT NULL,\n    age  INTEGER\n);\n\n-- Insert\nINSERT INTO users (name, age) VALUES ('Alice', 30);\n\n-- Query\nSELECT name, age FROM users WHERE age > 25 ORDER BY name;\n\n-- Join\nSELECT u.name, o.product\nFROM users u\nJOIN orders o ON u.id = o.user_id;\n```",

    "what is async": "### Async / Await Programming\n\n**Asynchronous** code allows a program to start a task and move on before it finishes — crucial for I/O-bound work.\n\n```python\nimport asyncio\nimport aiohttp\n\nasync def fetch(url: str) -> dict:\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as resp:\n            return await resp.json()\n\nasync def main():\n    data = await fetch('https://api.github.com')\n    print(data)\n\nasyncio.run(main())\n```\n\n```javascript\nasync function fetchData(url) {\n    const res = await fetch(url);\n    return res.json();\n}\n```",

    "what is big o": "### Big O Notation\n\nBig O describes **algorithm complexity** — how runtime or space grows with input size n.\n\n| Notation | Name | Example |\n|----------|------|--------|\n| O(1) | Constant | Array index lookup |\n| O(log n) | Logarithmic | Binary search |\n| O(n) | Linear | Simple loop |\n| O(n log n) | Log-linear | Merge sort |\n| O(n²) | Quadratic | Bubble sort |\n| O(2ⁿ) | Exponential | Recursive Fibonacci |\n\nAlways aim for **O(n log n)** or better for sorting/searching problems.",

    "sorting algorithm": "### Common Sorting Algorithms\n\n```python\n# Bubble sort — O(n²)\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(n - i - 1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n\n# Merge sort — O(n log n)\ndef merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\n# Python built-in (Timsort — O(n log n))\nsorted_arr = sorted([5, 2, 8, 1, 9])\n```",

    "binary search": "### Binary Search\n\nBinary search finds a target in a **sorted** array in **O(log n)** time.\n\n```python\ndef binary_search(arr: list, target: int) -> int:\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1  # not found\n\nprint(binary_search([1,3,5,7,9,11], 7))  # → 3\n```",

    "linked list": "### Linked List\n\nA linked list is a chain of **nodes** where each node holds data and a pointer to the next node.\n\n```python\nclass Node:\n    def __init__(self, val):\n        self.val = val\n        self.next = None\n\nclass LinkedList:\n    def __init__(self):\n        self.head = None\n\n    def append(self, val):\n        new = Node(val)\n        if not self.head:\n            self.head = new; return\n        cur = self.head\n        while cur.next:\n            cur = cur.next\n        cur.next = new\n\n    def to_list(self):\n        result, cur = [], self.head\n        while cur:\n            result.append(cur.val)\n            cur = cur.next\n        return result\n```\n\n**O(1) prepend, O(n) search, O(n) append without tail pointer.**",
}
