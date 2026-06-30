// --- DOM Elements Reference Cache ---
var splashScreen = document.getElementById('splash-screen');
var enterBtn = document.getElementById('enter-btn');
var projectsDashboard = document.getElementById('projects-dashboard');
var workspaceContainer = document.getElementById('workspace-container');
var exitToHubHeaderBtn = document.getElementById('exit-to-hub-header-btn');
var exitToSplashBtn = document.getElementById('exit-to-splash-btn');
var editor = document.getElementById('code-editor');
var highlightOverlay = document.getElementById('highlight-overlay');
var lineGutter = document.getElementById('line-gutter');
var editorWrapper = document.getElementById('editor-wrapper');
var currentFileLabel = document.getElementById('current-file-label');
var locDisplay = document.getElementById('loc-display');
var projectTitleBtn = document.getElementById('project-title-btn');
var tabPreview = document.getElementById('tab-preview');
var fileListContainer = document.getElementById('file-list');
var previewFrame = document.getElementById('preview-frame');
var addFileBtn = document.getElementById('add-file-btn');
var addProjectBtnDash = document.getElementById('add-project-btn-dash');
var tabTerminalBtn = document.getElementById('tab-terminal-btn');
var runBtn = document.getElementById('run-btn');
var terminalViewContainer = document.getElementById('terminal-view-container');
var terminalViewBody = document.getElementById('terminal-view-body');
var terminalStatus = document.getElementById('terminal-status');
var terminalInput = document.getElementById('terminal-input');
var languageBtn = document.getElementById('language-btn');
var languageMenu = document.getElementById('language-menu');
var currentLanguageText = document.getElementById('current-language-text');
var languageListDropdown = document.getElementById('language-list-dropdown');
var headerCopyCodeBtn = document.getElementById('header-copy-code-btn');
var toastContainer = document.getElementById('toast-container');
// --- Core State Variables ---
var projects = [];
var currentProjectId = null;
var selectedLanguages = ['Javascript'];
var activeView = 'editor'; // 'editor', 'preview', 'terminal'
var manualLanguageOverride = false;

function executeTerminalCommand(cmdLine) {
    if (activeView !== 'terminal') return;
    terminalViewBody.textContent += `\njungle:~# ${cmdLine}\n`;
    const parts = cmdLine.split(' '), command = parts[0].toLowerCase(), args = parts.slice(1), p = JungleUI.getCurrentProject();
    switch (command) {
        case 'help': terminalViewBody.textContent += "Available shell commands:\n  run           - Compile and run active file inside sandbox\n  analyze       - Run Jungle static checks on the active file\n  ls            - List all project file nodes\n  open [file]   - Switch editor focus to a project file\n  clear         - Clear console workspace output streams\n  cat [file]    - Output the file text data lines\n  info          - Inspect environment compiler metadata\n"; break;
        case 'clear': terminalViewBody.textContent = "Console output cleared."; break;
        case 'ls':
            if (!p) { terminalViewBody.textContent += "Error: No project open.\n"; } else {
                terminalViewBody.textContent += `Files inside [${p.name}]:\n` + Object.keys(p.files).map(f => `  📄 ${f}`).join('\n') + `\n`;
            }
            break;
        case 'run':
            if (!p) { terminalViewBody.textContent += "Error: Load a project first.\n"; } else { JungleRunner.execute(selectedLanguages[0], p.files[p.currentFile], p.files); }
            break;
        case 'analyze':
            if (!p) {
                terminalViewBody.textContent += "Error: Load a project first.\n";
            } else {
                const issues = JungleScanner.scan(selectedLanguages[0], p.files[p.currentFile]);
                if (issues.length === 0) {
                    terminalViewBody.textContent += "No obvious run-stopping issues found.\n";
                } else {
                    terminalViewBody.textContent += JungleRunner.formatSimpleReport({ lineNo: issues[0].line, errorMsg: issues[0].msg }) + "\n";
                }
            }
            break;
        case 'open':
            if (args.length === 0) { terminalViewBody.textContent += "Usage: open [filename]\n"; }
            else if (!p || !p.files[args[0]]) { terminalViewBody.textContent += `Error: File '${args[0]}' not found.\n`; }
            else { JungleUI.switchToFile(args[0]); terminalViewBody.textContent += `Opened ${args[0]}\n`; }
            break;
        case 'cat':
            if (args.length === 0) { terminalViewBody.textContent += "Usage: cat [filename]\n"; }
            else if (!p || !p.files[args[0]]) { terminalViewBody.textContent += `Error: File '${args[0]}' not found.\n`; }
            else { terminalViewBody.textContent += `--- Content: ${args[0]} ---\n${p.files[args[0]]}\n`; }
            break;
        case 'info':
            if (!p) { terminalViewBody.textContent += "Error: Empty workspace metadata.\n"; } else {
                terminalViewBody.textContent += `Project:      ${p.name}\nActive File:  ${p.currentFile}\nLanguage:     ${selectedLanguages[0]}\nSandbox:      Piston Isolation Shell (Linux Containers)\n`;
            }
            break;
        default:
            if (command === 'python' || command === 'node' || command === 'g++' || command === 'javac') {
                if (args.length > 0 && p && p.files[args[0]]) {
                    let lang = command === 'python' ? 'Python' : (command === 'g++' ? 'C++' : (command === 'javac' ? 'Java' : 'Javascript'));
                    JungleRunner.execute(lang, p.files[args[0]], p.files);
                } else { terminalViewBody.textContent += `Error: Usage or file '${args[0]}' not found.\n`; }
            } else { terminalViewBody.textContent += `jungle: command not found: '${command}'. Type 'help' to see active shell features.\n`; }
            break;
    }
    terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
}
terminalViewContainer.onclick = () => { if (activeView === 'terminal') { terminalInput.focus(); } };
terminalInput.addEventListener('keydown', (e) => {
    if (activeView !== 'terminal') { e.preventDefault(); return; }
    if (e.key === 'Enter') {
        const cmd = terminalInput.value.trim();
        terminalInput.value = '';
        if (cmd) executeTerminalCommand(cmd);
    }
});
function switchView(view, showInput = false) {
    activeView = view;
    editorWrapper.style.display = previewFrame.style.display = terminalViewContainer.style.display = 'none';
    const terminalInputRow = document.getElementById('terminal-input-row');
    projectTitleBtn.classList.remove('active');
    tabPreview.classList.remove('active');
    tabTerminalBtn.classList.remove('bg-[#1c2522]', 'text-[#74a896]', 'border-[#528b74]');
    if (view === 'editor') {
        editorWrapper.style.display = 'flex';
        projectTitleBtn.classList.add('active');
        terminalInput.setAttribute('disabled', 'true');
        terminalInputRow.classList.add('hidden');
    } else if (view === 'preview') {
        previewFrame.style.display = 'block';
        tabPreview.classList.add('active');
        terminalInput.setAttribute('disabled', 'true');
        terminalInputRow.classList.add('hidden');
    } else if (view === 'terminal') {
        terminalViewContainer.style.display = 'flex';
        tabTerminalBtn.classList.add('bg-[#1c2522]', 'text-[#74a896]', 'border-[#528b74]');
        if (showInput) {
            terminalInputRow.classList.remove('hidden');
            terminalInput.removeAttribute('disabled');
            setTimeout(() => terminalInput.focus(), 50);
        } else {
            terminalInputRow.classList.add('hidden');
            terminalInput.setAttribute('disabled', 'true');
        }
    }
}

enterBtn.onclick = () => { splashScreen.classList.add('fade-out'); setTimeout(() => { splashScreen.style.display = 'none'; splashScreen.style.pointerEvents = 'none'; }, 400); projectsDashboard.classList.add('show'); JungleUI.renderProjectsDashboard(); };
exitToSplashBtn.onclick = () => { splashScreen.style.display = 'flex'; splashScreen.style.pointerEvents = 'auto'; setTimeout(() => splashScreen.classList.remove('fade-out'), 50); projectsDashboard.classList.remove('show'); };
exitToHubHeaderBtn.onclick = () => { workspaceContainer.style.display = 'none'; projectsDashboard.classList.add('show'); JungleUI.renderProjectsDashboard(); };
addFileBtn.onclick = () => {
    JungleUI.showCustomModal({
        title: "Create Project File",
        placeholder: "e.g., helpers.py, styles.js",
        onConfirm: (name) => {
            if (!name) return;
            const p = JungleUI.getCurrentProject();
            if (!p) return;
            const fileName = JungleIntelligence.sanitizeFileName(name, selectedLanguages[0], p.files);
            p.files[fileName] = '';
            JungleUI.renderFilesList();
            JungleUI.switchToFile(fileName);
            JungleStorage.saveProjects(projects);
            JungleUI.showToast(`File ${fileName} created`);
        }
    });
};
addProjectBtnDash.onclick = () => {
    JungleUI.showCustomModal({
        title: "Create Project",
        placeholder: "e.g., Python Sandbox",
        onConfirm: (name) => {
            if (!name) return;
            const newId = 'proj_' + Date.now();
            const newProj = JungleIntelligence.createStarterProject(newId, name);
            projects.push(newProj);
            JungleStorage.saveProjects(projects);
            JungleUI.renderProjectsDashboard();
            JungleUI.loadProject(newId);
        }
    });
};
// Global callback handler to trap frame runtime and compilation crashes in written HTML files
window.handleIframeError = (message, source, lineno, colno) => {
    switchView('terminal', false);
    terminalStatus.textContent = "FAILED TO RUN";
    terminalStatus.className = "text-rose-500 font-bold";
    const p = JungleUI.getCurrentProject();
    const insight = JungleRunner.explainError(message, 'HTML', message);
    JungleRunner.printCrashAnalysis({
        file: (p && p.currentFile) || "index.html",
        lineNo: lineno,
        column: colno,
        errorMsg: message,
        likelyCause: insight.likelyCause || "A script inside the preview frame crashed.",
        suggestion: insight.suggestion || "Inspect the JavaScript near the reported line in the HTML file.",
        rawOutput: message
    }, "", message);
    JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => {
        switchView('terminal', false);
    });
};
runBtn.onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p) return;
    const isHtml = (p.currentFile.endsWith('.html') || p.currentFile.endsWith('.htm')) && selectedLanguages[0] === 'HTML';
    if (isHtml) {
        try {
            const missingAssets = JungleIntelligence.findMissingHtmlAssets(p.files[p.currentFile], p.files);
            if (missingAssets.length > 0) {
                const missing = missingAssets[0];
                switchView('terminal', false);
                terminalStatus.textContent = "FAILED TO RUN";
                terminalStatus.className = "text-rose-500 font-bold";
                terminalViewBody.textContent = JungleRunner.formatSimpleReport({
                    lineNo: missing.line,
                    errorMsg: `missing file ${missing.file}`
                });
                JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => { switchView('terminal', false); });
                return;
            }
            terminalStatus.textContent = "READY";
            terminalStatus.className = "text-[#74a896]";
            terminalViewBody.textContent = "";
            switchView('preview');
            const iframeWin = previewFrame.contentWindow, doc = iframeWin.document;
            let frameCompileError = false;
            iframeWin.onerror = function(message, source, lineno, colno) { frameCompileError = true; window.handleIframeError(message, source, lineno, colno); return true; };
            doc.open();
            const htmlWithAssets = JungleIntelligence.injectProjectAssetsIntoHtml(p.files[p.currentFile], p.files);
            const errorBubbleInjectedCode = `<script>window.onerror = function(m, s, l, c) { if (window.parent && window.parent.handleIframeError) { window.parent.handleIframeError(m, s, l, c); } return true; };<\/script>` + htmlWithAssets;
            doc.write(errorBubbleInjectedCode);
            doc.close();
            setTimeout(() => { if (!frameCompileError) JungleUI.showToast("Webpage loaded successfully in Preview panel."); }, 150);
        } catch(e) {
            console.error("Frame writing blocked", e);
            switchView('terminal', false);
            terminalStatus.textContent = "FAILED TO RUN";
            terminalStatus.className = "text-rose-500 font-bold";
            terminalViewBody.textContent = JungleRunner.formatSimpleReport({ lineNo: "Unknown", errorMsg: e.message });
            JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => { switchView('terminal', false); });
        }
    } else { JungleRunner.execute(selectedLanguages[0], p.files[p.currentFile], p.files); }
};
tabPreview.onclick = runBtn.onclick;
tabTerminalBtn.onclick = () => { switchView('terminal', true); JungleUI.showToast("Switched output channel to Terminal Console view."); };
projectTitleBtn.onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p || Object.keys(p.files).length === 0) { switchView('editor'); return; }

    // Detect language per file by extension
    function langFromFilename(name) {
        const ext = name.split('.').pop().toLowerCase();
        const map = { js: 'Javascript', ts: 'TypeScript', py: 'Python', html: 'HTML', htm: 'HTML', css: 'CSS',
            java: 'Java', c: 'C', cpp: 'C++', cs: 'C#', go: 'Go', rs: 'Rust', rb: 'Ruby', php: 'PHP',
            lua: 'Lua', sh: 'Bash', bash: 'Bash', r: 'R', swift: 'Swift', kt: 'Kotlin', sql: 'SQL' };
        return map[ext] || 'Javascript';
    }

    const tokenCSS = `.token-keyword{color:#FFB86C}.token-string{color:#06CF7A}.token-comment{color:#6272A4;font-style:italic}.token-number{color:#FF79C6}.token-type{color:#8BE9FD}.token-fn{color:#f1fa8c}.token-builtin{color:#bd93f9}.token-op{color:#FF5555}.token-punct{color:#7f848e}.token-attr{color:#FFB86C}.token-tag{color:#FF79C6}.token-property{color:#FFB86C}.token-decorator{color:#bd93f9;font-style:italic}`;

    const sections = Object.entries(p.files).map(([name, content]) => {
        const lang = langFromFilename(name);
        const hlHtml = JungleUI.highlightCode(lang, content || '');
        return `<div class="file-block">
            <div class="file-header"><span class="file-icon">📄</span><span class="file-name">${name.replace(/</g,'&lt;')}</span><span class="file-lang">${lang}</span></div>
            <pre class="file-code">${hlHtml || '(empty file)'}</pre>
        </div>`;
    }).join('');

    const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0f0d;color:#aed9cb;font-family:'Fira Code',monospace;font-size:13px;padding:20px;line-height:1.6;}
${tokenCSS}
.file-block{margin-bottom:28px;border:1px solid #1e2e28;border-radius:8px;overflow:hidden;}
.file-header{display:flex;align-items:center;gap:10px;background:#111a16;padding:8px 14px;border-bottom:1px solid #1e2e28;}
.file-icon{font-size:14px}
.file-name{color:#aed9cb;font-weight:700;font-size:13px;}
.file-lang{color:#4a6057;font-size:11px;margin-left:auto;}
.file-code{padding:14px 16px;overflow-x:auto;background:#080e0b;white-space:pre;tab-size:4;}
</style></head><body>${sections}</body></html>`;

    const doc = previewFrame.contentDocument || previewFrame.contentWindow.document;
    doc.open(); doc.write(html); doc.close();
    switchView('preview');
    terminalStatus.textContent = "PROJECT VIEW";
    terminalStatus.style.color = "#74a896";
    projectTitleBtn.classList.add('active');
    tabPreview.classList.remove('active');
};
const langPickerScreen = document.getElementById('lang-picker-screen');
const langPickerBack = document.getElementById('lang-picker-back');
const langPickerSearch = document.getElementById('lang-picker-search');
const langPickerGrid = document.getElementById('lang-picker-grid');
languageBtn.onclick = () => { langPickerScreen.classList.add('visible'); langPickerSearch.value = ''; renderLangPickerGrid(''); langPickerSearch.focus(); };
langPickerBack.onclick = () => langPickerScreen.classList.remove('visible');
langPickerSearch.oninput = () => renderLangPickerGrid(langPickerSearch.value.toLowerCase());
const templatePanelToggle = document.getElementById('template-panel-toggle');
const templatePanelBody = document.getElementById('template-panel-body');
const templateToggleArrow = document.getElementById('template-toggle-arrow');
const TEMPLATES = {
    web: {
        lang: 'HTML',
        files: {
            'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Web Page</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .card { text-align: center; padding: 3rem; background: #1e293b; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.4); }
        h1 { font-size: 2.5rem; margin-bottom: 0.75rem; color: #7dd3c0; }
        p { color: #94a3b8; margin-bottom: 2rem; }
        button { background: #2dd4bf; color: #0f172a; border: none; padding: 12px 32px; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: transform 0.15s, background 0.15s; }
        button:hover { background: #5eead4; transform: translateY(-2px); }
        #counter { font-size: 3rem; font-weight: 800; color: #7dd3c0; margin-top: 1.5rem; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Hello World</h1>
        <p>Click the button to count up.</p>
        <button onclick="increment()">Click Me</button>
        <div id="counter">0</div>
    </div>
    <script src="script.js"></script>
</body>
</html>`,
            'script.js': `let count = 0;

function increment() {
    count++;
    document.getElementById('counter').textContent = count;
}`
        },
        currentFile: 'index.html'
    },
    python: {
        lang: 'Python',
        files: {
            'main.py': `def greet(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

def fizzbuzz(n):
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)

def main():
    print(greet("World"))
    print(f"3 + 7 = {add(3, 7)}")
    print("\\nFizzBuzz up to 20:")
    fizzbuzz(20)

main()
`
        },
        currentFile: 'main.py'
    },
    javascript: {
        lang: 'Javascript',
        files: {
            'main.js': `// JavaScript App Starter

function greet(name) {
    return \`Hello, \${name}!\`;
}

function sum(numbers) {
    return numbers.reduce((acc, n) => acc + n, 0);
}

function bubbleSort(arr) {
    const a = [...arr];
    for (let i = 0; i < a.length; i++) {
        for (let j = 0; j < a.length - i - 1; j++) {
            if (a[j] > a[j + 1]) [a[j], a[j + 1]] = [a[j + 1], a[j]];
        }
    }
    return a;
}

async function fetchJoke() {
    try {
        const res = await fetch('https://official-joke-api.appspot.com/random_joke');
        const joke = await res.json();
        console.log(\`Joke: \${joke.setup} ... \${joke.punchline}\`);
    } catch (e) {
        console.log('Could not fetch joke:', e.message);
    }
}

async function main() {
    console.log(greet('World'));
    const nums = [5, 3, 8, 1, 9, 2, 7];
    console.log('Unsorted:', nums.join(', '));
    console.log('Sorted:  ', bubbleSort(nums).join(', '));
    console.log('Sum:', sum(nums));
    await fetchJoke();
}

main();
`
        },
        currentFile: 'main.js'
    }
};
templatePanelToggle.onclick = () => {
    const open = templatePanelBody.classList.toggle('open');
    templateToggleArrow.textContent = open ? '▲' : '▼';
};
function updateTemplateBtnVisibility() {
    const p = JungleUI.getCurrentProject();
    if (!p) return;
    const hasContent = Object.values(p.files).some(c => c && c.trim().length > 0);
    templatePanelToggle.style.display = hasContent ? 'none' : '';
}
document.querySelectorAll('.template-card').forEach(card => {
    card.onclick = () => {
        const p = JungleUI.getCurrentProject();
        if (!p) { JungleUI.showToast('Open a project first to load a template.'); return; }
        const t = TEMPLATES[card.getAttribute('data-template')];
        if (!t) return;
        Object.assign(p.files, t.files);
        p.currentFile = t.currentFile;
        p.lang = t.lang;
        selectedLanguages = [t.lang];
        manualLanguageOverride = true;
        JungleStorage.saveProjects(projects);
        JungleUI.renderFilesList();
        JungleUI.switchToFile(t.currentFile);
        templatePanelBody.classList.remove('open');
        templateToggleArrow.textContent = '▼';
        JungleUI.showToast(`Loaded ${card.querySelector('.template-card-name').textContent} template.`);
    };
});
headerCopyCodeBtn.onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p || !p.currentFile) return;
    const textareaBackup = document.createElement("textarea");
    textareaBackup.value = p.files[p.currentFile];
    document.body.appendChild(textareaBackup);
    textareaBackup.select();
    document.execCommand('copy');
    document.body.removeChild(textareaBackup);
    JungleUI.showToast(`Copied ${p.currentFile} content to clipboard!`);
};
document.getElementById('select-all-code-btn').onclick = () => {
    editor.focus();
    editor.select();
    editor.scrollTop = 0;
};
document.getElementById('download-code-btn').onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p || !p.currentFile) return;
    const blob = new Blob([p.files[p.currentFile]], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = p.currentFile;
    a.click();
    URL.revokeObjectURL(a.href);
    JungleUI.showToast(`Downloaded ${p.currentFile}`);
};
editor.oninput = () => {
    const p = JungleUI.getCurrentProject();
    if (!p || !p.currentFile) return;
    p.files[p.currentFile] = editor.value;
    JungleUI.updateLinesOfCodeCount();
    JungleStorage.saveProjects(projects);
    if (!manualLanguageOverride) {
        const detection = JungleScanner.detectLanguage(editor.value);
        if (detection && detection.lang !== selectedLanguages[0]) {
            const { lang: detectedLang, confidence } = detection;
            selectedLanguages = [detectedLang];
            p.lang = detectedLang;
            currentLanguageText.textContent = `Language: ${detectedLang}`;
            const newFilename = JungleIntelligence.renameFileForLanguage(p.currentFile, detectedLang, p.files);
            if (newFilename !== p.currentFile) {
                const fileContent = p.files[p.currentFile];
                delete p.files[p.currentFile];
                p.files[newFilename] = fileContent;
                p.currentFile = newFilename;
                currentFileLabel.textContent = newFilename;
                JungleUI.renderFilesList();
            }
            JungleStorage.saveProjects(projects);
            if (confidence === 'confirmed') {
                JungleUI.showToast(`Detected ${detectedLang} — tap language button to override.`);
            }
        }
    }
    JungleUI.updateCodeHighlight();
    updateTemplateBtnVisibility();
};
editor.onscroll = () => { highlightOverlay.scrollTop = lineGutter.scrollTop = editor.scrollTop; highlightOverlay.scrollLeft = editor.scrollLeft; };
editor.onkeydown = (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        editor.value = editor.value.substring(0, start) + "    " + editor.value.substring(editor.selectionEnd);
        editor.selectionStart = editor.selectionEnd = start + 4;
        editor.oninput();
    }
};
const LANG_ICONS = {
    'Assembly': '⚙️', 'Bash': '🐚', 'C': '🔵', 'C#': '💜', 'C++': '🔷',
    'Clojure': '🟢', 'COBOL': '🏢', 'D': '🔶', 'Dart': '🎯', 'Elixir': '💧',
    'Erlang': '📡', 'F#': '🟣', 'Fortran': '🧮', 'Go': '🐹', 'Haskell': '🟡',
    'HTML': '🌐', 'Java': '☕', 'Javascript': '⚡', 'Julia': '🔴', 'Kotlin': '🟠',
    'Lisp': '🌀', 'Lua': '🌙', 'Nim': '👑', 'OCaml': '🐪', 'Pascal': '🏛️',
    'Perl': '🐪', 'PHP': '🐘', 'Prolog': '🧠', 'Python': '🐍', 'R': '📊',
    'Ruby': '💎', 'Rust': '🦀', 'Scala': '⚖️', 'Swift': '🕊️', 'TypeScript': '🔷',
    'Zig': '⚡'
};
const ALL_LANGS = ["Assembly","Bash","C","C#","C++","Clojure","COBOL","D","Dart","Elixir","Erlang","F#","Fortran","Go","Haskell","HTML","Java","Javascript","Julia","Kotlin","Lisp","Lua","Nim","OCaml","Pascal","Perl","PHP","Prolog","Python","R","Ruby","Rust","Scala","Swift","TypeScript","Zig"];
function renderLangPickerGrid(filter) {
    const current = selectedLanguages[0] || '';
    const filtered = filter ? ALL_LANGS.filter(l => l.toLowerCase().includes(filter)) : ALL_LANGS;
    langPickerGrid.innerHTML = filtered.map(l => {
        const icon = LANG_ICONS[l] || '📄';
        const label = l === 'HTML' ? 'HTML / Web' : l;
        const sel = l === current ? ' selected' : '';
        return `<div class="lang-picker-card${sel}" data-lang="${l}"><span class="lang-picker-icon">${icon}</span><span class="lang-picker-name">${label}</span></div>`;
    }).join('');
    langPickerGrid.querySelectorAll('.lang-picker-card').forEach(card => {
        card.onclick = () => {
            const targetLang = card.getAttribute('data-lang');
            selectedLanguages = [targetLang];
            manualLanguageOverride = true;
            currentLanguageText.textContent = `Language: ${targetLang}`;
            langPickerScreen.classList.remove('visible');
            const p = JungleUI.getCurrentProject();
            if (p) {
                p.lang = targetLang;
                const firstMatch = Object.keys(p.files).find(f => JungleIntelligence.languageFromFilename(f, '') === targetLang);
                if (firstMatch) {
                    JungleUI.switchToFile(firstMatch);
                } else {
                    const newFilename = JungleIntelligence.renameFileForLanguage(p.currentFile, targetLang, p.files);
                    if (newFilename !== p.currentFile) {
                        p.files[newFilename] = p.files[p.currentFile];
                        delete p.files[p.currentFile];
                        JungleUI.renderFilesList();
                        JungleUI.switchToFile(newFilename);
                    }
                }
                JungleStorage.saveProjects(projects);
            }
        };
    });
}

window.onload = () => {
    projects = JungleStorage.getProjects();
};

// ── Drag-and-drop file import ─────────────────────────────────────────────────
(function setupDragDrop() {
    const zones = [
        document.getElementById('editor-wrapper'),
        document.getElementById('file-list'),
        document.getElementById('preview-frame'),
    ];

    function isZip(file) {
        return file.name.toLowerCase().endsWith('.zip') ||
               file.type === 'application/zip' ||
               file.type === 'application/x-zip-compressed';
    }

    function handleFiles(fileList) {
        const files = Array.from(fileList);
        const zips = files.filter(isZip);
        const valid = files.filter(f => !isZip(f));

        if (zips.length > 0) {
            JungleUI.showToast('⛔ This editor does not allow ZIP files. Please drag or create a normal file.', null, 'error');
        }

        valid.forEach(file => {
            const reader = new FileReader();
            reader.onload = e => {
                const content = e.target.result;
                const p = JungleUI.getCurrentProject();
                if (!p) return;
                const safeName = JungleIntelligence.sanitizeFileName(file.name, p.lang, p.files);
                p.files[safeName] = content;
                JungleStorage.saveProjects(projects);
                JungleUI.renderFilesList();
                JungleUI.switchToFile(safeName);
                JungleUI.showToast(`✓ Imported ${safeName}`, null, 'success');
            };
            reader.readAsText(file);
        });
    }

    zones.forEach(zone => {
        if (!zone) return;
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            e.stopPropagation();
            zone.style.outline = '2px dashed #528b74';
            zone.style.outlineOffset = '-4px';
        });
        zone.addEventListener('dragleave', e => {
            zone.style.outline = '';
            zone.style.outlineOffset = '';
        });
        zone.addEventListener('drop', e => {
            e.preventDefault();
            e.stopPropagation();
            zone.style.outline = '';
            zone.style.outlineOffset = '';
            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                handleFiles(e.dataTransfer.files);
            }
        });
    });
})();
