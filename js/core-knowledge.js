// Massive representative offline vocabulary compiled directly inside the app
const RAW_DICTIONARY_DATA = "the and of to in is you that it he was for on are as with his they i at be this have from or one had by word but not what all were we when your can said there use an each which she do how their if will up other about out many then them these so some her would make like him into time has look more write go see number no way could people my than first water been call who oil its now find long down day did get come made may part over new sound take only little work know place year live me back give most very after thing our just name good sentence man think say great where help through much before line right too mean old any same tell boy follow came want show also around form three small set put end does another well large must big even such because turn here why ask went kind off need house picture try us again change play spell air away land different home science physics chemistry biology astronomy geology mathematics calculus trigonometry geometry algebra arithmetic logic computing programming algorithms hardware software network database server client cloud web browser compiler terminal editor system process thread processor memory disk drive folder file document image photo audio video music signal wave frequency electricity current voltage resistance power energy force gravity velocity acceleration momentum inertia mass density volume area length width height depth weight scale temperature heat cold pressure flow fluid liquid gas solid plasma ice rain snow wind storm cloud sky sun moon star planet asteroid comet meteor galaxy nebula universe space cosmic vacuum orbit trajectory satellite rocket engine oxygen nitrogen hydrogen carbon helium lithium beryllium boron fluorine sodium magnesium aluminum silicon phosphorus sulfur chlorine potassium calcium iron copper zinc silver gold mercury lead uranium history president election constitution democracy congress senate house government governor mayor law court judge freedom liberty justice rights amendment treaty war peace military dynamic matrix cognitive reasoning local assistant welcome screen core initializing workspace math calculations spelling corrections fuzzy search edit distance levenshtein volcano lithosphere rock mineral stone basalt granite obsidian sediment metamorphic sandstone shale marble slate composite stratovolcano eruption caldera ring of fire subduction mariana trench challenger deep hydrothermal vent black smoker chemosynthesis crust mantle core asthenosphere magnetic field seismic wave";

const VOCABULARY = [
    ...Object.keys(LANG_HISTORY),
    ...Object.keys(GAME_TEMPLATES),
    ...spaceKeywords,
    ...earthKeywords,
    ...advancedScienceKeywords,
    ...politicalKeywords,
    "concurrency", "datastructure", "memory", "designpattern", "derivative", "integral", "limit", "calculus", "trigonometry"
];

const SYSTEM_DICTIONARY = [];
const BUCKETED_DICTIONARY = {};

function compileDictionaryMatrix() {
    const words = RAW_DICTIONARY_DATA.toLowerCase().split(/\s+/);
    for (const word of words) {
        const clean = word.replace(/[^a-z]/g, '').trim();
        if (clean.length > 0 && !SYSTEM_DICTIONARY.includes(clean)) {
            SYSTEM_DICTIONARY.push(clean);
        }
    }

    VOCABULARY.forEach(word => {
        const clean = word.toLowerCase().trim();
        if (!SYSTEM_DICTIONARY.includes(clean)) {
            SYSTEM_DICTIONARY.push(clean);
        }
    });

    for (let i = 97; i <= 122; i++) {
        BUCKETED_DICTIONARY[String.fromCharCode(i)] = [];
    }

    SYSTEM_DICTIONARY.forEach(word => {
        const firstChar = word.charAt(0);
        if (BUCKETED_DICTIONARY[firstChar]) {
            BUCKETED_DICTIONARY[firstChar].push(word);
        }
    });
}

compileDictionaryMatrix();

function getEditDistance(a, b) {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;
    const matrix = Array.from({ length: b.length + 1 }, () => []);
    for (let i = 0; i <= b.length; i++) matrix[i][0] = i;
    for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            matrix[i][j] = b.charAt(i - 1) === a.charAt(j - 1) 
                ? matrix[i - 1][j - 1] 
                : Math.min(matrix[i - 1][j - 1] + 1, Math.min(matrix[i][j - 1] + 1, matrix[i - 1][j] + 1));
        }
    }
    return matrix[b.length][a.length];
}

// Standard English prepositions and short words to protect from fuzzy calculations
const PROTECTED_ENGLISH_WORDS = [
    "when", "what", "with", "where", "which", "while", "make", "game", "play", "from", "about", 
    "your", "then", "than", "them", "they", "this", "that", "there", "have", "some", "more", 
    "like", "will", "would", "could", "should", "tell", "show", "find", "solve", "how", "who", 
    "whom", "whose", "why", "want", "went", "well", "were", "been", "does", "done", "once"
];

// Specific high confidence vocabulary keywords that spell checker corrects to
const HIGH_CONFIDENCE_SYSTEM_KEYWORDS = [
    "volcano", "volcanoes", "caldera", "subduction", "trench", "mariana", "ocean", 
    "hydrothermal", "vent", "chemosynthesis", "lithosphere", "basalt", "granite",
    "calculus", "trigonometry", "derivative", "integral", "differentiation", "integration",
    "quantum", "physics", "planck", "boltzmann", "electronegativity", "transcription",
    "washington", "president", "lincoln", "roosevelt", "constitution", "federalist", "whig",
    "python", "javascript", "typescript", "golang", "kotlin", "rust", "rarest", "fastest", "rocks", "stone"
];

function spellCorrectQuery(query) {
    const words = query.toLowerCase().split(/[\s,?.!]+/);
    const corrected = [];
    const detections = [];
    
    for (const word of words) {
        if (word.length <= 4 || PROTECTED_ENGLISH_WORDS.includes(word) || SYSTEM_DICTIONARY.includes(word)) {
            corrected.push(word);
            continue;
        }
        
        const firstChar = word.charAt(0);
        const bucket = BUCKETED_DICTIONARY[firstChar];
        
        if (!bucket) {
            corrected.push(word);
            continue;
        }

        let bestMatch = null;
        let minDistance = 3; 
        
        for (const vocab of bucket) {
            // Only fuzzy correct to highly important system domains to prevent normal English speech corruptions
            if (!HIGH_CONFIDENCE_SYSTEM_KEYWORDS.includes(vocab)) continue;
            if (Math.abs(word.length - vocab.length) >= minDistance) continue;

            const dist = getEditDistance(word, vocab);
            if (dist < minDistance) {
                minDistance = dist;
                bestMatch = vocab;
            }
        }

        if (bestMatch && minDistance < 3) {
            detections.push({ original: word, corrected: bestMatch });
            corrected.push(bestMatch);
        } else {
            corrected.push(word);
        }
    }
    return { text: corrected.join(" "), corrections: detections };
}

function isMathematicalExpression(str) {
    const clean = str.trim().toLowerCase()
        .replace(/^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+/i, '')
        .replace(/\?+$/, '');
    const mathRegex = /^[0-9+\-*/().\s^%÷x]+$/i;
    const testStr = clean.replace(/sin|cos|tan|csc|sec|cot|log|ln|sqrt|abs|pi/g, '');
    return mathRegex.test(testStr) && /[0-9]/.test(testStr) && /[+\-*/^%÷x]/.test(testStr);
}

function generateSpaceKnowledgeResponse(query, mode) {
    const queryLower = query.toLowerCase().trim();
    let heading = "Space Mechanics Observation", body = "", thinkingProcess = "";
    let cardFormula = "", cardResult = "", cardStyle = "indigo";

    if (queryLower.includes("sun") && (queryLower.includes("earth") || queryLower.includes("distance") || queryLower.includes("apart") || queryLower.includes("far"))) {
        heading = "Earth-to-Sun Orbit Distance";
        body = "The distance between the Earth and the Sun is not perfectly static because our orbit is elliptical rather than a perfect circle. On average, the Earth is about **93 million miles** away from the Sun.\n\nThis astronomical distance is mathematically represented as **1 Astronomical Unit (AU)**. Sunlight, traveling at the ultimate cosmic speed limit ($186,282\\text{ miles per second}$), takes approximately **8 minutes and 20 seconds** to reach us here on Earth.";
        cardFormula = "Average Earth-Sun Distance (1 AU)";
        cardResult = "93,000,000 Miles";
        thinkingProcess = "- **Intent:** Astronomy constant query (Earth-Sun distance).\n- **Parameters:** Elliptical orbit variance, AU coordinate translation.\n- **Speed Integration:** Sunlight travel delta $\\approx 500\\text{ seconds}$.";
    }
    else if (queryLower.includes("moon") && (queryLower.includes("earth") || queryLower.includes("distance") || queryLower.includes("far") || queryLower.includes("apart"))) {
        heading = "Earth-to-Moon Orbit Distance";
        body = "Our natural satellite, the Moon, orbits the Earth in an elliptical path. Its average distance from us is **238,855 miles** ($384,400\\text{ km}$).\n\nAt its closest point (perigee), it is about $225,623\\text{ miles}$ away, and at its furthest point (apogee), it stretches to $252,088\\text{ miles}$. This distance is roughly equivalent to wrapping 30 Earths in a row!";
        cardFormula = "Average Earth-Moon Distance";
        cardResult = "238,855 Miles";
        thinkingProcess = "- **Intent:** Moon orbit constant query.\n- **Math Check:** Translating metric apogee/perigee scale limits to statute miles.";
    }
    else if (queryLower.includes("speed of light")) {
        heading = "Universal Speed Limit (c)";
        body = "According to Einstein's Theory of Special Relativity, the speed of light in a vacuum ($c$) is the absolute cosmic speed limit. It travels at exactly **186,282 miles per second** ($299,792\\text{ km/s}$).\n\nTo put this in perspective, if you could travel at the speed of light, you could circle the Earth's equator about **7.5 times in a single second**!";
        cardFormula = "Speed of Light in Vacuum (c)";
        cardResult = "186,282 mi/s";
        cardStyle = "emerald";
        thinkingProcess = "- **Intent:** Universal constant query (c).\n- **Reference Framework:** Einstein's Special Relativity model boundaries.";
    }
    else {
        heading = "Astronomical Analysis";
        body = `Based on my internal offline cosmological database, I have processed your inquiry regarding **"${query}"**.\n\n1. **Cosmic Scaling Boundaries:** Outer space operates on scales that transcend standard human perception, shifting from the $1.5\\text{ AU}$ neighborhood of Mars to the billions of parsecs separating galactic superclusters.\n2. **The Vacuum Medium:** Space is a nearly perfect vacuum where light can travel unimpeded, which is why we are able to observe ancient stars from the early universe.\n3. **Universal Physics Constants:** The behavior of every star, black hole, and nebula is governed by a small, beautiful set of invariant physical constants: $c$ (speed of light), $G$ (gravitation), and $\\hbar$ (Planck's constant).\n\nLet me know if you would like me to retrieve specific facts, orbital periods, or map an equation for your space topic!`;
        thinkingProcess = `- **Intent:** Open space topic query.\n- **Formulating Output:** Providing a comprehensive, structured cosmic mechanics overview.`;
    }

    let response = cardResult ? `${body}\n\n[COSMIC_CARD: formula: ${cardFormula} | result: ${cardResult} | style: ${cardStyle}]` : body;
    if (mode === 'forge_thinking') return `### <i class="fa-solid fa-user-astronaut text-indigo-500 mr-2"></i> Thinking Process\n${thinkingProcess}\n\n---\n\n### ${heading}\n${response}`;
    if (mode === 'forge_instant') return `### ${heading}\n\n${response.split('\n\n')[0]}`;
    return `### ${heading}\n${response}`;
}

function generateEarthScienceResponse(query, mode) {
    const queryLower = query.toLowerCase().trim();
    let heading = "Lithospheric & Earth Science Telemetry", body = "", thinkingProcess = "";
    let cardTopic = "Geological Parameter", cardValue = "", cardStyle = "emerald";

    if (queryLower.includes("rarest") || queryLower.includes("rare") || queryLower.includes("rastest")) {
        heading = "Rarest Minerals on Earth";
        body = "The rarest types of minerals and rocks on Earth are dictated by precise geological compositions and high-pressure subduction parameters:\n\n" +
               "1. **Kyawthuite**: This is officially the single rarest mineral in the world. Only a single specimen has ever been found in Myanmar. It is an exceptionally rare, orange-hued bismuth-antimony oxide ($Bi^{3+}Sb^{5+}O_4$).\n" +
               "2. **Painite**: Once recognized as the world's rarest mineral, Painite is a complex calcium zirconium borate ($CaZrBAl_9O_{18}$) that features trace chromium impurities, resulting in deep, reddish-brown crystal lattices.\n" +
               "3. **Lonsdaleite**: An extremely rare hexagonal allotrope of carbon, found primarily in meteorites, which is theoretically 58% harder than diamond under absolute cubic crystalline parameters.";
        cardTopic = "World's Rarest Specimen";
        cardValue = "Kyawthuite (1 Verified Crystal)";
        cardStyle = "amber";
        thinkingProcess = "- **Intent:** Geologic mineral metrics (rarest rocks).\n- **Data Points:** Kyawthuite bismuth stoichiometry, Painite discovery parameters.";
    } else if (queryLower.includes("rock") || queryLower.includes("stone") || queryLower.includes("mineral") || queryLower.includes("petrolog") || queryLower.includes("granite") || queryLower.includes("basalt") || queryLower.includes("sediment") || queryLower.includes("metamorph")) {
        heading = "Petrological Foundations & Rock Cycles";
        body = "Rocks are the solid building blocks of Earth's crust, divided scientifically into three primary families:\n\n1. **Igneous Rocks**: Formed from the cooling and solidification of molten rock.\n2. **Sedimentary Rocks**: Formed by accumulation, compaction, and cementation of mineral and organic particles.\n3. **Metamorphic Rocks**: Pre-existing rocks altered by extreme heat and pressure without melting.";
        cardTopic = "Crustal Rock Cycle Interplay";
        cardValue = "Igneous, Sedimentary & Metamorphic";
        thinkingProcess = "- **Intent:** Petrologic classification query.\n- **Taxonomy:** Intrusive vs extrusive igneous, lithification of sediments, recrystallization parameters.";
    } else {
        heading = "Interior Structure of the Earth";
        body = "The Earth is divided into distinct geological layers, mapped continuously by measuring seismic wave velocities:\n\n1. **Crust**: The outermost solid shell.\n2. **Mantle**: A vast zone of solid silicate rock with the ductile asthenosphere.\n3. **Outer Core**: A churning pool of liquid iron and nickel that generates our magnetic field.\n4. **Inner Core**: A solid crystalline sphere of iron-nickel alloy.";
        cardTopic = "Outer Core Magnetic Field Dynamo";
        cardValue = "Churning Liquid Iron-Nickel";
        cardStyle = "indigo";
        thinkingProcess = "- **Intent:** Planet core and interior geophysics.\n- **Seismic Modeling:** P-wave shadow boundaries.";
    }

    let response = `${body}\n\n[EARTH_CARD: topic: ${cardTopic} | value: ${cardValue} | style: ${cardStyle}]`;
    if (mode === 'forge_thinking') return `### <i class="fa-solid fa-mountain-sun text-emerald-500 mr-2"></i> Thinking Process\n${thinkingProcess}\n\n---\n\n### ${heading}\n${response}`;
    if (mode === 'forge_instant') return `### ${heading}\n\n${response.split('\n\n')[0]}`;
    return `### ${heading}\n${response}`;
}

function generateScienceKnowledgeResponse(query, mode) {
    let heading = "Advanced Telemetry Analytics";
    let body = `Based on my internal offline scientific database, I have processed your inquiry regarding "${query}".\n\n1. **Dynamic Energy Quanta**: Microscopic systems are dictated by invariant Planck metrics.\n2. **Molecular Bond Mechanics**: Atoms interact based on electronegativity gradients and covalent coordinates.\n3. **Biological Information Transcription**: Natural genetic codes utilize hydrogen bonds to store and replicate complex operational blueprints.`;
    let response = `${body}\n\n[SCIENCE_CARD: topic: Cognitive Database Sync | value: Active & Calibrated | style: violet]`;
    if (mode === 'forge_thinking') return `### <i class="fa-solid fa-atom text-violet-500 mr-2"></i> Thinking Process\n- **Intent:** Generic science query fallbacks.\n\n---\n\n### ${heading}\n${response}`;
    if (mode === 'forge_instant') return `### ${heading}\n\n${response.split('\n\n')[0]}`;
    return `### ${heading}\n${response}`;
}

function generateHistoricalKnowledgeResponse(query, mode) {
    let heading = "Constitutional & Presidential Heritage";
    let body = `Based on my internal historical database, I have processed your inquiry regarding "${query}".\n\n1. **Precedential Foundations**: The office of the president depends on foundational actions laid out by George Washington.\n2. **Constitutional Preservation**: During critical conflicts, presidential powers have expanded to safeguard stability and rights.\n3. **Institutional Evolution**: The executive branch has evolved into a modern administrative state.`;
    let response = `${body}\n\n[HISTORY_CARD: topic: Historical Database Sync | value: Active & Synchronized | style: amber]`;
    if (mode === 'forge_thinking') return `### <i class="fa-solid fa-scroll text-amber-600 mr-2"></i> Thinking Process\n- **Intent:** Generic history fallbacks.\n\n---\n\n### ${heading}\n${response}`;
    if (mode === 'forge_instant') return `### ${heading}\n\n${response.split('\n\n')[0]}`;
    return `### ${heading}\n${response}`;
}

function generateAdvancedMathResponse(query, mode) {
    const queryLower = query.toLowerCase().trim()
        .replace(/^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+/i, '')
        .replace(/\?+$/, '');
    let heading = "Advanced Mathematics Processor", body = "", thinkingProcess = "";
    let cardFormula = "", cardResult = "", cardStyle = "violet";

    if (queryLower.includes("derivative") || queryLower.includes("d/dx")) {
        let expression = queryLower.replace(/derivative of|d\/dx/gi, '').trim();
        heading = "Symbolic Derivative Calculus Solver";
        if (expression.includes("x")) {
            let termExpr = expression.replace(/\s+/g, '');
            let terms = termExpr.match(/([+-]?[0-9]*x(?:\^[0-9]+)?|[+-]?[0-9]+)/gi) || [];
            let dTerms = [];
            let steps = [];
            terms.forEach(term => {
                let matches = term.match(/([+-]?)([0-9]*)x(?:\^([0-9]+))?/i);
                if (matches) {
                    let sign = matches[1] === '-' ? -1 : 1;
                    let coeff = matches[2] === '' ? 1 : parseInt(matches[2]);
                    let valCoeff = sign * coeff;
                    let power = matches[3] === undefined ? 1 : parseInt(matches[3]);
                    if (power === 1) {
                        dTerms.push(`${valCoeff >= 0 ? '+' : ''}${valCoeff}`);
                        steps.push(`$\\frac{d}{dx}[${term}] = ${valCoeff}$`);
                    } else {
                        let newCoeff = valCoeff * power;
                        let newPower = power - 1;
                        let powerStr = newPower === 1 ? 'x' : `x^${newPower}`;
                        dTerms.push(`${newCoeff >= 0 ? '+' : ''}${newCoeff}${powerStr}`);
                        steps.push(`$\\frac{d}{dx}[${term}] = (${valCoeff} \\cdot ${power})x^{${power} - 1} = ${newCoeff}${powerStr}$`);
                    }
                } else if (!isNaN(term)) {
                    steps.push(`$\\frac{d}{dx}[${term}] = 0$ (constant derivative is zero)`);
                }
            });
            let finalResult = dTerms.join(" ").replace(/^\+\s*/, '').trim() || "0";
            body = `To find the derivative of the polynomial expression **$f(x) = ${expression}$** with respect to $x$, we apply the derivative Power Rule:\n\n$$\\frac{d}{dx}[x^n] = n \\cdot x^{n-1}$$\n\n**Step-by-step differentiation breakdown:**\n${steps.map((s, idx) => `${idx + 1}. ${s}`).join("\n")}\n\nCombining these differentiated segments gives the final derivative:\n\n$$\\frac{d}{dx}[${expression}] = ${finalResult}$$`;
            cardFormula = `d/dx [ ${expression} ]`;
            cardResult = finalResult;
        } else {
            body = `Could not symbolically differentiate the non-polynomial target expression **"${expression}"** offline. Please input a valid algebraic polynomial expression such as \`3x^3 + 5x^2 - 4x\`.`;
        }
        thinkingProcess = "- **Intent:** Symbolic Differentiation.\n- **Method:** Polynomial Power Rule mapping.";
    } else if (/(sin|cos|tan|csc|sec|cot)\s*/i.test(queryLower)) {
        let match = queryLower.match(/(sin|cos|tan|csc|sec|cot)\s*(?:\()?(\d+(?:\.\d+)?)(?:\s*(deg|rad|degree|radian|°))?/i);
        heading = "Trigonometric Ratio Evaluator";
        if (match) {
            let ratio = match[1].toLowerCase();
            let val = parseFloat(match[2]);
            let unit = match[3] || 'deg';
            unit = unit.startsWith('deg') || unit === '°' ? 'deg' : 'rad';
            let radVal = unit === 'deg' ? (val * Math.PI) / 180 : val;
            let computed = { sin: Math.sin, cos: Math.cos, tan: Math.tan }[ratio]?.(radVal);
            if (ratio === 'csc') computed = 1 / Math.sin(radVal);
            if (ratio === 'sec') computed = 1 / Math.cos(radVal);
            if (ratio === 'cot') computed = 1 / Math.tan(radVal);
            computed = Math.round(computed * 100000) / 100000;
            body = `Evaluating the trigonometric ratio **$\\${ratio}(${val}\\text{ ${unit === 'deg' ? 'degrees' : 'radians'}})$**:\n\n1. **Input Angle**: $${val}${unit === 'deg' ? '^\\circ' : '\\text{ rad}'}$\n2. **Radian Conversion**: $${val}${unit === 'deg' ? ' \\cdot \\frac{\\pi}{180}' : ''} = ${radVal.toFixed(5)}\\text{ rad}$\n3. **Numerical Reduction**: $\\${ratio}(${radVal.toFixed(5)}) \\approx ${computed}$`;
            cardFormula = `${ratio}(${val} ${unit === 'deg' ? '°' : 'rad'})`;
            cardResult = computed.toString();
        } else {
            body = `Could not resolve trigonometric arguments from expression **"${queryLower}"**. Try inputting ratios like \`sin(45 deg)\` or \`cos(1.047 rad)\`.`;
        }
        thinkingProcess = "- **Intent:** Trigonometry Evaluation.\n- **Input Metrics:** Parsed angular constraints.";
    } else {
        try {
            let mathClean = queryLower.replace(/plus/g, '+').replace(/minus/g, '-').replace(/times|x/g, '*').replace(/divided by|divide|÷/g, '/').replace(/[^0-9+\-*/().\s^%]/g, '');
            let val = new Function(`return (${mathClean.replace(/\^/g, '**')});`)();
            if (typeof val === 'number' && !isNaN(val) && isFinite(val)) {
                heading = "Arithmetic Evaluator";
                body = `Evaluating the arithmetic expression **$${mathClean}$**:\n\n1. **Expression**: $${mathClean}$\n2. **Computed Value**: $${val}$`;
                cardFormula = mathClean;
                cardResult = val.toString();
            } else {
                heading = "Mathematical Processor";
                body = `Could not resolve the mathematical expression **"${queryLower}"** offline. Please input a valid algebraic or arithmetic expression.`;
            }
        } catch (e) {
            heading = "Mathematical Error";
            body = `Could not safely parse or evaluate the arithmetic query **"${queryLower}"** offline.`;
        }
        thinkingProcess = "- **Intent:** Arithmetic Reduction.\n- **Method:** Evaluated Function mapping.";
    }

    let response = cardResult ? `${body}\n\n[MATH_CARD: formula: ${cardFormula} | result: ${cardResult} | style: ${cardStyle}]` : body;
    if (mode === 'forge_thinking') return `### <i class="fa-solid fa-infinity text-violet-500 mr-2"></i> Thinking Process\n${thinkingProcess}\n\n---\n\n### ${heading}\n${response}`;
    if (mode === 'forge_instant') return `### ${heading}\n\n${response.split('\n\n')[0]}`;
    return `### ${heading}\n${response}`;
}
