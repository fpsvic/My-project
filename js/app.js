const modeConfigs = {
    forge_code: { text: "Forge code 2.5", icon: "fa-code", color: "text-indigo-500", bg: "bg-indigo-50/40" },
    forge_thinking: { text: "Forge thinking 2.6", icon: "fa-brain", color: "text-amber-500", bg: "bg-amber-50/40" },
    forge_instant: { text: "Forge instant 2.5", icon: "fa-bolt", color: "text-emerald-500", bg: "bg-emerald-50/40" }
};

const state = {
    sessions: [],
    currentSessionId: null,
    activeLanguage: "javascript",
    activeMode: "forge_code"
};

function generateGeneralKnowledgeResponse(query, mode) {
    const queryLower = query.toLowerCase().trim();
    const languageKey = Object.keys(LANG_HISTORY).find(lang => queryLower.includes(lang));

    if (languageKey) {
        const history = LANG_HISTORY[languageKey];
        const hello = LANG_HELLO_WORLD[languageKey] || LANG_HELLO_WORLD.javascript;
        const response = `### ${languageKey.toUpperCase()} Knowledge Archive\n${history}\n\n\`\`\`${languageKey}\n${hello}\n\`\`\``;
        if (mode === 'forge_thinking') {
            return `### <i class="fa-solid fa-brain text-amber-500 mr-2"></i> Thinking Process\n- **Intent:** Programming language knowledge lookup.\n- **Detected Language:** ${languageKey}.\n\n---\n\n${response}`;
        }
        return response;
    }

    const topicKey = queryLower.includes("concurrency") ? "concurrency" : queryLower.includes("cache") || queryLower.includes("data") ? "datastructure" : "default";
    const sample = OFFLINE_KNOWLEDGE_BASE.javascript[topicKey];
    const response = `### ${sample.title}\n${sample.desc}\n\n\`\`\`javascript\n${sample.code}\n\`\`\``;
    if (mode === 'forge_instant') {
        return `### ${sample.title}\n\n${sample.desc}`;
    }
    return response;
}

// DOM Declarations to ensure absolute reference safety and avoid window scoping clashes
const sidebarPanel = document.getElementById("sidebarPanel");
const btnMobileSidebarClose = document.getElementById("btnMobileSidebarClose");
const btnNewSession = document.getElementById("btnNewSession");
const sessionListContainer = document.getElementById("sessionListContainer");
const chatFeed = document.getElementById("chatFeed");
const userInput = document.getElementById("userInput");
const chatForm = document.getElementById("chatForm");
const btnSubmit = document.getElementById("btnSubmit");
const btnModeSelector = document.getElementById("btnModeSelector");
const modeMenu = document.getElementById("modeMenu");
const currentModeText = document.getElementById("currentModeText");
const sidebarBackdrop = document.getElementById("sidebarBackdrop");
const btnMobileSidebarToggle = document.getElementById("btnMobileSidebarToggle");
const toastNotification = document.getElementById("toastNotification");
const toastMessage = document.getElementById("toastMessage");

// Global showToast definition correctly defined inside global script block
function showToast(message, isWarning = false) {
    if (!toastNotification || !toastMessage) return;
    toastMessage.innerText = message;
    const icon = toastNotification.querySelector('i');
    if (icon) {
        icon.className = isWarning ? "fa-solid fa-circle-exclamation text-rose-500 text-xs" : "fa-solid fa-circle-check text-emerald-500 text-xs";
    }
    toastNotification.classList.remove("translate-y-12", "opacity-0");
    toastNotification.classList.add("translate-y-0", "opacity-100");
    setTimeout(() => {
        toastNotification.classList.remove("translate-y-0", "opacity-100");
        toastNotification.classList.add("translate-y-12", "opacity-0");
    }, 2500);
}

// Play game iframe modal trigger logic
window.openSandboxFromCode = function(btn) {
    const preCode = btn.closest(".my-4").querySelector("pre code");
    if (!preCode) return;
    const codeText = preCode.innerText;
    const modal = document.getElementById("sandboxModal");
    const frame = document.getElementById("sandboxFrame");
    if (modal && frame) {
        modal.classList.remove("hidden");
        frame.srcdoc = codeText;
    }
};

window.closeSandbox = function() {
    const modal = document.getElementById("sandboxModal");
    const frame = document.getElementById("sandboxFrame");
    if (modal && frame) {
        modal.classList.add("hidden");
        frame.srcdoc = ""; // completely purge frame memory
    }
};

// Offline Main Router & Cognitive Director
function generateLocalAIResponse(query, history = []) {
    const queryLower = query.toLowerCase().trim();
    const activeConfig = modeConfigs[state.activeMode];

    // 1. General Greeting check
    const greetings = ["hello", "hi", "how are you", "who are you", "hey", "sup", "greetings", "whats up", "good morning", "good afternoon"];
    if (greetings.some(g => queryLower === g || queryLower.startsWith(g + " ") || queryLower.startsWith(g + "?") || queryLower.startsWith(g + "!"))) {
        return `Hello! I am **ForgeAI**, your cognitive local assistant. Currently running in **${activeConfig.text}** mode.\n\nI can assist you with a wide range of tasks, including answering general knowledge questions, solving mathematical expressions, exploring programming language history, and designing software architecture. How can I help you today?`;
    }

    // 2. Dynamic Custom Procedural Game Compiler Integration (Analyzes user prompt and generates corresponding styled code!)
    const isGameRequest = /(make|create|play|build|programming|code)\s+.*game/i.test(queryLower) || /(pong|snake|tictactoe|flappy|arcade|brick|clicker|shooter)/i.test(queryLower);
    if (isGameRequest) {
        const gameMeta = compileCustomGame(query);
        const introText = `I have analyzed your parameters and procedural request. Compiling **${gameMeta.title}** module based entirely on your custom parameters. Click **"Play Game"** inside the code box to run your custom game instantly!`;

        if (state.activeMode === 'forge_thinking') {
            return `### <i class="fa-solid fa-brain text-amber-500 mr-2"></i> Thinking Process\n- **Target Compilation**: ${gameMeta.title} Dynamic Procedural Module.\n- **Keywords Analyzed**: theme, speed, genre, obstacles configurations.\n- **Code Space Layout**: Generating embedded dynamic Canvas frame with variables injected.\n\n---\n\n${introText}\n\n\`\`\`html\n${gameMeta.code}\n\`\`\``;
        }
        return `${introText}\n\n\`\`\`html\n${gameMeta.code}\n\`\`\``;
    }

    // 3. Presidential & US Political History check
    const isHistoryQuery = politicalKeywords.some(keyword => queryLower.includes(keyword));
    if (isHistoryQuery) {
        return generateHistoricalKnowledgeResponse(query, state.activeMode);
    }

    // 4. Advanced Math, Calculus & Trigonometry check
    const advancedMathKeywords = ["derivative", "integral", "integrate", "antiderivative", "sin", "cos", "tan", "csc", "sec", "cot"];
    const isAdvancedMathQuery = advancedMathKeywords.some(keyword => queryLower.includes(keyword)) || isMathematicalExpression(query);
    if (isAdvancedMathQuery) {
        return generateAdvancedMathResponse(query, state.activeMode);
    }

    // 5. Space cosmology telemetry check
    const isSpaceQuery = spaceKeywords.some(keyword => queryLower.includes(keyword));
    if (isSpaceQuery) {
        return generateSpaceKnowledgeResponse(query, state.activeMode);
    }

    // 6. Earth science geophysics check
    const isEarthQuery = earthKeywords.some(keyword => queryLower.includes(keyword));
    if (isEarthQuery) {
        return generateEarthScienceResponse(query, state.activeMode);
    }

    // 7. Quantum & Chemistry science check
    const isScienceQuery = advancedScienceKeywords.some(keyword => queryLower.includes(keyword));
    if (isScienceQuery) {
        return generateScienceKnowledgeResponse(query, state.activeMode);
    }

    // 8. General knowledge fallback
    return generateGeneralKnowledgeResponse(query, state.activeMode);
}

// Local Storage Session Management
function loadSessionsFromLocalStorage() {
    try {
        const stored = localStorage.getItem("forgeai_sessions");
        state.sessions = stored ? JSON.parse(stored) : [];
        const storedMode = localStorage.getItem("forgeai_active_mode");
        if (storedMode && modeConfigs[storedMode]) {
            state.activeMode = storedMode;
            updateModeSelectorUI(storedMode);
        }
    } catch (err) { state.sessions = []; }

    if (state.sessions.length === 0) createNewSession();
    else { state.currentSessionId = state.sessions[0].id; renderSessionList(); renderCurrentSessionChat(); }
}

function saveSessionsToLocalStorage() {
    try { localStorage.setItem("forgeai_sessions", JSON.stringify(state.sessions)); } catch (err) {}
}

function createNewSession() {
    const newId = "session_" + Date.now();
    state.sessions.unshift({ id: newId, title: "New Code Session", language: "javascript", messages: [] });
    state.currentSessionId = newId; state.activeLanguage = "javascript";
    saveSessionsToLocalStorage(); renderSessionList(); renderCurrentSessionChat();
    showToast("Created a new code session!");
}

function deleteSession(sessionId, event) {
    if (event) event.stopPropagation();
    state.sessions = state.sessions.filter(s => s.id !== sessionId);
    if (state.currentSessionId === sessionId) {
        if (state.sessions.length > 0) {
            state.currentSessionId = state.sessions[0].id; state.activeLanguage = state.sessions[0].language;
        } else { createNewSession(); return; }
    }
    saveSessionsToLocalStorage(); renderSessionList(); renderCurrentSessionChat();
    showToast("Session removed", true);
}

function selectSession(sessionId) {
    const session = state.sessions.find(s => s.id === sessionId);
    if (!session) return;
    state.currentSessionId = sessionId; state.activeLanguage = session.language;
    renderCurrentSessionChat(); renderSessionList();
    sidebarPanel.classList.remove("open"); sidebarBackdrop.classList.add("hidden");
}

// Language Icon Markup Generator Helper Function
function getLanguageIconHTML(lang) {
    const icons = {
        javascript: 'fa-brands fa-js text-yellow-500',
        typescript: 'fa-solid fa-code text-blue-500',
        java: 'fa-brands fa-java text-orange-500',
        golang: 'fa-brands fa-golang text-cyan-500',
        cpp: 'fa-solid fa-cube text-indigo-500',
        c: 'fa-solid fa-microchip text-slate-500',
        csharp: 'fa-solid fa-hashtag text-purple-500',
        kotlin: 'fa-solid fa-terminal text-purple-600',
        lua: 'fa-solid fa-moon text-blue-600',
        luau: 'fa-solid fa-star text-indigo-400',
        matlab: 'fa-solid fa-calculator text-red-600',
        python: 'fa-brands fa-python text-sky-500',
        r: 'fa-solid fa-chart-line text-blue-700',
        ruby: 'fa-solid fa-gem text-rose-500',
        rust: 'fa-solid fa-gear text-orange-600',
        swift: 'fa-brands fa-swift text-orange-500'
    };
    return `<i class="${icons[lang] || 'fa-regular fa-message text-slate-400'} shrink-0 text-sm"></i>`;
}

function renderSessionList() {
    sessionListContainer.innerHTML = '';
    state.sessions.forEach(session => {
        const card = document.createElement("div");
        const isActive = session.id === state.currentSessionId;
        card.className = `group relative flex items-center justify-between mx-1.5 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 cursor-pointer ${
            isActive ? "bg-slate-200/60 text-slate-900 border border-slate-200/80 shadow-sm" : "hover:bg-slate-100 text-slate-600 hover:text-slate-900"
        }`;

        const textContainer = document.createElement("div");
        textContainer.className = "flex items-center space-x-2.5 truncate w-full pr-12";
        textContainer.innerHTML = `${getLanguageIconHTML(session.language)}<span class="truncate text-slate-800 font-medium">${session.title}</span>`;
        card.appendChild(textContainer);

        const actionGroup = document.createElement("div");
        actionGroup.className = "absolute right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity duration-150";
        actionGroup.innerHTML = `
            <button class="rename-btn text-slate-400 hover:text-slate-700 p-1 rounded-md hover:bg-white/80 border border-transparent hover:border-slate-200/40 transition-colors duration-150"><i class="fa-solid fa-pen text-[9px]"></i></button>
            <button class="delete-btn text-slate-400 hover:text-rose-500 p-1 rounded-md hover:bg-white/80 border border-transparent hover:border-slate-200/40 transition-colors duration-150"><i class="fa-solid fa-trash-can text-[9px]"></i></button>
        `;
        card.appendChild(actionGroup);

        let isRenaming = false;
        const titleSpan = textContainer.querySelector("span");

        actionGroup.querySelector(".rename-btn").addEventListener('click', (e) => {
            e.stopPropagation(); if (isRenaming) return; isRenaming = true;
            const input = document.createElement("input");
            input.type = "text"; input.value = session.title;
            input.className = "w-full bg-white border border-slate-300 focus:border-slate-400 focus:outline-none rounded px-1.5 py-0.5 text-xs text-slate-800 font-medium font-sans";
            textContainer.replaceChild(input, titleSpan); input.focus(); input.select();
            actionGroup.classList.add("hidden");

            const submitRename = () => {
                const newTitle = input.value.trim();
                if (newTitle && newTitle !== session.title) { session.title = newTitle; saveSessionsToLocalStorage(); showToast("Session renamed!"); }
                isRenaming = false; renderSessionList();
            };
            input.addEventListener('keydown', (evt) => {
                if (evt.key === 'Enter') { evt.preventDefault(); submitRename(); }
                else if (evt.key === 'Escape') { evt.preventDefault(); isRenaming = false; renderSessionList(); }
            });
            input.addEventListener('blur', submitRename);
            input.addEventListener('click', (evt) => evt.stopPropagation());
        });

        actionGroup.querySelector(".delete-btn").addEventListener('click', (e) => { e.stopPropagation(); deleteSession(session.id, e); });
        card.addEventListener('click', () => { if (!isRenaming) selectSession(session.id); });
        sessionListContainer.appendChild(card);
    });
}

window.prefillPrompt = function(promptText) {
    userInput.value = promptText;
    userInput.focus();
    setTimeout(() => { btnSubmit.click(); }, 100);
};

function renderCurrentSessionChat() {
    chatFeed.innerHTML = '';
    const currentSession = state.sessions.find(s => s.id === state.currentSessionId);
    if (!currentSession) return;

    if (currentSession.messages.length === 0) {
        chatFeed.innerHTML = `
            <div class="flex flex-col items-center justify-center text-center py-12 px-4 max-w-2xl mx-auto space-y-8 animate-fadeIn select-none">
                
                <div class="space-y-1.5">
                    <p class="text-[10px] text-indigo-500 font-mono uppercase tracking-widest font-semibold">Local Cognitive Core Initialized</p>
                    <p class="text-slate-500 text-xs">Select a workspace suggestion below or type a query directly to begin.</p>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg text-left animate-fadeIn">
                    <button onclick="prefillPrompt('Whats derivative of 3x^3 + 5x^2 - 4x?')" class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1 group">
                        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
                            <i class="fa-solid fa-infinity text-indigo-500"></i>
                            <span>Calculus & Trigonometry</span>
                        </div>
                        <p class="text-[10px] text-slate-400">Differentiate polynomials, solve integrals, or compute trig ratios.</p>
                    </button>

                    <button onclick="prefillPrompt('what is the distance between the earth and the sun?')" class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1 group">
                        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
                            <i class="fa-solid fa-user-astronaut text-indigo-500"></i>
                            <span>Explore Space Telemetry</span>
                        </div>
                        <p class="text-[10px] text-slate-400 mt-1">Check light travel times, orbital distances, and cosmological scopes.</p>
                    </button>

                    <button onclick="prefillPrompt('make a flappy bird game')" class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1 group">
                        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
                            <i class="fa-solid fa-gamepad text-indigo-500"></i>
                            <span>Build Playable Games</span>
                        </div>
                        <p class="text-[10px] text-slate-400 mt-1">Generate complete copyable HTML5 Flappy, Pong, or Snake arcade codes.</p>
                    </button>

                    <button onclick="prefillPrompt('tell me about underwater hydrothermal vents and ocean trenches')" class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1 group">
                        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
                            <i class="fa-solid fa-mountain-sun text-indigo-500"></i>
                            <span>Underwater Earth Science</span>
                        </div>
                        <p class="text-[10px] text-slate-400 mt-1">Analyze Challenger Deep, mid-ocean rifts, and black smoker vents.</p>
                    </button>
                </div>
            </div>`;
    } else {
        currentSession.messages.forEach(msg => {
            if (msg.role === 'user') addUserMessageUI(msg.text);
            else addAIStreamUI(msg.text, false);
        });
    }
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

// Markdown formatter tokenizing standard and glowing cosmic/lithosphere components
function formatMarkdown(text) {
    let formattedText = escapeHTML(text);
    const placeholders = [];
    
    // Extract and secure code blocks
    formattedText = formattedText.replace(/```(\w*)\n([\s\S]*?)```/g, (match, language, codeContent) => {
        const placeholder = `__CODE_BLOCK_PLACEHOLDER_${placeholders.length}__`;
        const cleanCode = codeContent.trim();
        const displayLang = language ? language.toUpperCase() : "SOURCE CODE";
        
        // Add Sandbox Launch button next to "Copy Code" for playable games
        const isPlayableGame = displayLang === "HTML" && (cleanCode.includes("gameCanvas") || cleanCode.includes("arcadeCanvas") || cleanCode.includes("cell") || cleanCode.includes("ballDX") || cleanCode.includes("birdY"));
        const playBtnHtml = isPlayableGame 
            ? `<button type="button" onclick="openSandboxFromCode(this)" class="hover:text-white text-indigo-400 font-semibold transition flex items-center space-x-1.5 border border-indigo-500/30 hover:border-indigo-400/50 bg-indigo-950/20 px-2.5 py-1 rounded-md">
                   <i class="fa-solid fa-gamepad text-[10px]"></i><span class="text-[9px]">Play Game</span>
               </button>` 
            : "";

        const customCodeHtml = `
            <div class="my-4 bg-slate-900 rounded-xl border border-slate-950 overflow-hidden font-mono text-[11px] shadow-md text-left">
                <div class="bg-slate-950/40 px-4 py-2.5 border-b border-slate-950/50 flex justify-between items-center text-slate-400">
                    <span class="text-[10px] font-bold tracking-wider text-slate-500">${displayLang}</span>
                    <div class="flex items-center space-x-2">
                        ${playBtnHtml}
                        <button type="button" onclick="copyCodeSnippet(this)" class="hover:text-white transition flex items-center space-x-1 border border-slate-800 bg-slate-950/40 px-2 py-1 rounded">
                            <i class="fa-regular fa-copy text-[10px]"></i><span class="text-[9px]">Copy Code</span>
                        </button>
                    </div>
                </div>
                <pre class="p-4 overflow-x-auto text-slate-200 leading-normal"><code>${cleanCode}</code></pre>
            </div>`;
        placeholders.push(customCodeHtml);
        return placeholder;
    });

    // Restore structured blocks
    placeholders.forEach((html, idx) => { formattedText = formattedText.replace(`__CODE_BLOCK_PLACEHOLDER_${idx}__`, html); });
    
    // Format inline code
    formattedText = formattedText.replace(/`([^`\n]+)`/g, '<code class="bg-slate-100 border border-slate-200/80 px-1.5 py-0.5 rounded text-indigo-600 font-mono text-xs">$1</code>')
                                 .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-slate-900">$1</strong>')
                                 .replace(/^\s*-\s+(.+)$/gm, '<li class="ml-4 list-disc text-slate-600">$1</li>');

    // Secure Spell-Corrector alert notification template
    formattedText = formattedText.replace(/\[TYPO_ALERT:\s*(.*?)\s*\|\s*(.*?)\s*\]/g, (match, original, corrected) => {
        return `
            <div class="bg-amber-50 border border-amber-200/60 rounded-xl p-3 mb-3 flex items-center space-x-2.5 text-xs text-amber-800 animate-fadeIn shadow-sm">
                <i class="fa-solid fa-wand-magic-sparkles text-amber-500 text-xs shrink-0"></i>
                <span>Auto-corrected typo: interpreted <span class="font-semibold font-mono underline decoration-wavy decoration-amber-500">${original}</span> as <span class="font-semibold font-mono text-indigo-600">${corrected}</span>.</span>
            </div>`;
    });

    const cardMarkup = (label, topic, value, style = "indigo", icon = "fa-satellite-dish") => `
        <div class="bg-${style}-50/60 border border-${style}-100/50 rounded-xl p-5 my-4 text-center shadow-sm max-w-md mx-auto animate-fadeIn">
            <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1 flex items-center justify-center space-x-1.5">
                <i class="fa-solid ${icon} animate-pulse"></i>
                <span>${label}</span>
            </div>
            <div class="text-xs font-mono text-slate-500 mb-3">${topic}</div>
            <div class="text-2xl font-bold text-${style}-600 font-mono tracking-tight">${value}</div>
        </div>`;

    formattedText = formattedText.replace(/\[MATH_CARD:\s*(.*?)\s*\]/g, (match, content) => {
        const parts = parseCardParts(content);
        return cardMarkup("Formula Result", parts.formula || "", parts.result || "", parts.style || "indigo", "fa-infinity");
    });
    formattedText = formattedText.replace(/\[COSMIC_CARD:\s*(.*?)\s*\]/g, (match, content) => {
        const parts = parseCardParts(content);
        return cardMarkup("Telemetry constant", parts.formula || "", parts.result || "", parts.style || "indigo", "fa-satellite-dish");
    });
    formattedText = formattedText.replace(/\[EARTH_CARD:\s*(.*?)\s*\]/g, (match, content) => {
        const parts = parseCardParts(content);
        return cardMarkup("Geological Lithosphere Log", parts.topic || "Geological Record", parts.value || "", parts.style || "emerald", "fa-earth-americas");
    });
    formattedText = formattedText.replace(/\[SCIENCE_CARD:\s*(.*?)\s*\]/g, (match, content) => {
        const parts = parseCardParts(content);
        return cardMarkup("Quantum & Fundamental Telemetry", parts.topic || "Scientific Log", parts.value || "", parts.style || "violet", "fa-atom");
    });
    formattedText = formattedText.replace(/\[HISTORY_CARD:\s*(.*?)\s*\]/g, (match, content) => {
        const parts = parseCardParts(content);
        return cardMarkup("Presidential & Constitutional Archives", parts.topic || "Historical Milestone", parts.value || "", "amber", "fa-scroll");
    });

    return formattedText.replace(/\n/g, "<br>");
}

function parseCardParts(content) {
    return content.split('|').reduce((acc, part) => {
        const [key, ...val] = part.split(':');
        if (key && val) acc[key.trim()] = val.join(':').trim();
        return acc;
    }, {});
}

function escapeHTML(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

window.copyCodeSnippet = function(btn) {
    const preElement = btn.closest(".my-4").querySelector("pre code");
    if (!preElement) return;
    const textarea = document.createElement("textarea");
    textarea.value = preElement.innerText; textarea.style.position = "absolute"; textarea.style.left = "-9999px";
    document.body.appendChild(textarea); textarea.select();
    try { document.execCommand('copy'); showToast("Code copied to clipboard!"); } catch (err) { showToast("Clipboard write failed", true); }
    document.body.removeChild(textarea);
};

function addUserMessageUI(msgText) {
    const row = document.createElement("div");
    row.className = "flex items-start justify-end space-x-3 max-w-[85%] ml-auto text-left animate-fadeIn";
    row.innerHTML = `<div class="bg-slate-100 border border-slate-200/60 text-slate-800 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm text-sm leading-relaxed">${escapeHTML(msgText).replace(/\n/g, "<br>")}</div>`;
    chatFeed.appendChild(row); chatFeed.scrollTop = chatFeed.scrollHeight;
}

function addThinkingIndicatorUI(isSearching = false) {
    const row = document.createElement("div");
    row.className = "flex items-start space-x-4 max-w-[95%] text-left animate-fadeIn";
    row.innerHTML = `
        <div class="h-8 w-8 bg-slate-100 border border-slate-200 rounded-lg flex items-center justify-center shrink-0 shadow-sm"><i class="fa-solid fa-circle-notch text-slate-600 text-xs animate-spin"></i></div>
        <div class="bg-slate-50 border border-slate-200/60 p-5 rounded-2xl rounded-tl-none w-full space-y-2">
            <div class="flex items-center space-x-2 text-slate-500 text-xs font-medium">
                <i class="fa-solid ${isSearching ? 'fa-magnifying-glass animate-pulse text-indigo-500' : 'fa-brain text-slate-400'}"></i>
                <span>${isSearching ? 'Searching Google & compiling real-time facts...' : 'Formulating system response...'}</span>
            </div>
            <div class="h-3 shimmer-bg rounded w-3/4"></div><div class="h-3 shimmer-bg rounded w-1/2"></div>
        </div>`;
    chatFeed.appendChild(row); chatFeed.scrollTop = chatFeed.scrollHeight;
    return row;
}

function addAIStreamUI(fullText, streamActive = true) {
    const row = document.createElement("div");
    row.className = "flex items-start space-x-4 max-w-[95%] text-left animate-fadeIn";
    row.innerHTML = `
        <div class="h-8 w-8 bg-slate-900 rounded-lg flex items-center justify-center shrink-0 shadow-sm"><i class="fa-solid fa-wand-magic-sparkles text-white text-xs"></i></div>
        <div class="bg-slate-50 border border-slate-200/40 p-5 rounded-2xl rounded-tl-none text-slate-700 leading-relaxed text-sm w-full shadow-sm">
            <div class="response-body font-normal text-slate-800"></div>
        </div>`;
    chatFeed.appendChild(row);
    const responseContainer = row.querySelector(".response-body");

    const checkScrollPosition = () => {
        const threshold = 120;
        return (chatFeed.scrollHeight - chatFeed.scrollTop - chatFeed.clientHeight) < threshold;
    };

    if (!streamActive) {
        responseContainer.innerHTML = formatMarkdown(fullText);
        chatFeed.scrollTop = chatFeed.scrollHeight; 
        return row;
    }

    return new Promise((resolve) => {
        const words = fullText.split(" "); 
        let i = 0; 
        const tempArr = [];
        
        const timer = setInterval(() => {
            if (i < words.length) {
                tempArr.push(words[i++]);
                const isAtBottom = checkScrollPosition();
                const textChunk = tempArr.join(" ");
                responseContainer.innerHTML = formatMarkdown(textChunk);
                if (isAtBottom) {
                    chatFeed.scrollTop = chatFeed.scrollHeight;
                }
            } else { 
                clearInterval(timer); 
                resolve(row); 
            }
        }, 8);
    });
}

btnModeSelector.addEventListener("click", (e) => { e.stopPropagation(); modeMenu.classList.toggle("hidden"); });
document.addEventListener("click", () => modeMenu.classList.add("hidden"));

function updateModeSelectorUI(selectedMode) {
    const config = modeConfigs[selectedMode];
    currentModeText.innerText = config.text;
    btnModeSelector.querySelector("i.fa-solid").className = `fa-solid ${config.icon} text-[10px] ${config.color}`;

    modeMenu.querySelectorAll("button").forEach(btn => {
        const modeKey = btn.getAttribute("data-mode");
        btn.className = modeKey === selectedMode 
            ? `w-full px-3 py-2 text-xs ${modeConfigs[modeKey].color} ${modeConfigs[modeKey].bg} flex items-center space-x-2.5 transition font-semibold`
            : "w-full px-3 py-2 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-50 flex items-center space-x-2.5 transition font-medium";
    });
}

modeMenu.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const selectedMode = btn.getAttribute("data-mode");
        state.activeMode = selectedMode;
        try { localStorage.setItem("forgeai_active_mode", selectedMode); } catch(err) {}
        updateModeSelectorUI(selectedMode);
        modeMenu.classList.add("hidden");
        showToast(`Switched workspace to ${modeConfigs[selectedMode].text}`);
    });
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Stop a raw newline from being inserted
        btnSubmit.click();  // Click submit to trigger the chat flow
    }
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault(); const text = userInput.value.trim(); if (!text) return;
    const currentSession = state.sessions.find(s => s.id === state.currentSessionId); if (!currentSession) return;

    if (currentSession.messages.length === 0) { currentSession.title = text.length > 24 ? text.substring(0, 22) + "..." : text; }

    currentSession.messages.push({ role: 'user', text: text }); addUserMessageUI(text);
    userInput.value = "";

    const thinkingRow = addThinkingIndicatorUI(false);
    await new Promise(r => setTimeout(r, 400)); thinkingRow.remove();

    // Run offline spell corrector prior to routing query
    const spellCheck = spellCorrectQuery(text);
    let processedQuery = spellCheck.text;
    let typoAlertsPrefix = "";
    if (spellCheck.corrections.length > 0) {
        spellCheck.corrections.forEach(c => {
            typoAlertsPrefix += `[TYPO_ALERT: ${c.original} | ${c.corrected}]\n`;
        });
    }

    const aiResponseRaw = generateLocalAIResponse(processedQuery, currentSession.messages);
    const aiResponseText = typoAlertsPrefix + aiResponseRaw;

    currentSession.messages.push({ role: 'assistant', text: aiResponseText });
    saveSessionsToLocalStorage(); renderSessionList(); await addAIStreamUI(aiResponseText, true);
});

btnNewSession.addEventListener('click', createNewSession);
btnMobileSidebarToggle.addEventListener('click', () => { sidebarPanel.classList.add("open"); sidebarBackdrop.classList.remove("hidden"); });
btnMobileSidebarClose.addEventListener('click', () => { sidebarPanel.classList.remove("open"); sidebarBackdrop.classList.add("hidden"); });
sidebarBackdrop.addEventListener('click', () => { sidebarPanel.classList.remove("open"); sidebarBackdrop.classList.add("hidden"); });

window.onload = function() {
    loadSessionsFromLocalStorage();

    const splashScreen = document.getElementById("splashScreen");
    const splashProgressBar = document.getElementById("splashProgressBar");
    const btnEnterStudio = document.getElementById("btnEnterStudio");
    const splashBtnIcon = document.getElementById("splashBtnIcon");
    const splashBtnText = document.getElementById("splashBtnText");
    const btnReturnToSplash = document.getElementById("btnReturnToSplash");

    // Complete the progress instantly on mount
    if (splashProgressBar) {
        splashProgressBar.style.width = "100%";
    }

    // Enable button instantly with no delay
    if (btnEnterStudio) {
        btnEnterStudio.disabled = false;
        btnEnterStudio.classList.remove("cursor-not-allowed", "opacity-50", "bg-slate-100", "text-slate-400", "border-slate-200");
        btnEnterStudio.classList.add("bg-indigo-600", "hover:bg-indigo-500", "text-white", "border-indigo-500", "scale-[1.01]", "shadow-[0_0_20px_rgba(99,102,241,0.3)]");
        if (splashBtnIcon) splashBtnIcon.className = "fa-solid fa-right-to-bracket";
        if (splashBtnText) splashBtnText.innerText = "Enter Workspace";
    }

    if (btnEnterStudio) {
        btnEnterStudio.onclick = function() {
            if (splashScreen) {
                splashScreen.classList.add("translate-y-full", "opacity-0", "pointer-events-none");
            }
            showToast("Welcome to ForgeAI Studio!");
        }
    }

    if (btnReturnToSplash) {
        btnReturnToSplash.onclick = function() {
            if (splashScreen) {
                splashScreen.classList.remove("translate-y-full", "opacity-0", "pointer-events-none");
            }
        }
    }
};
