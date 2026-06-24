// --- DOM Elements Reference Cache ---
const splashScreen = document.getElementById('splash-screen');
const enterBtn = document.getElementById('enter-btn');
const projectsDashboard = document.getElementById('projects-dashboard');
const workspaceContainer = document.getElementById('workspace-container');
const exitToHubHeaderBtn = document.getElementById('exit-to-hub-header-btn');
const exitToSplashBtn = document.getElementById('exit-to-splash-btn');
const editor = document.getElementById('code-editor');
const highlightOverlay = document.getElementById('highlight-overlay');
const lineGutter = document.getElementById('line-gutter');
const editorWrapper = document.getElementById('editor-wrapper');
const currentFileLabel = document.getElementById('current-file-label');
const locDisplay = document.getElementById('loc-display');
const projectTitleBtn = document.getElementById('project-title-btn');
const tabPreview = document.getElementById('tab-preview');
const fileListContainer = document.getElementById('file-list');
const previewFrame = document.getElementById('preview-frame');
const addFileBtn = document.getElementById('add-file-btn');
const addProjectBtnDash = document.getElementById('add-project-btn-dash');
const tabTerminalBtn = document.getElementById('tab-terminal-btn');
const runBtn = document.getElementById('run-btn');
const terminalViewContainer = document.getElementById('terminal-view-container');
const terminalViewBody = document.getElementById('terminal-view-body');
const terminalStatus = document.getElementById('terminal-status');
const terminalInput = document.getElementById('terminal-input');
const languageBtn = document.getElementById('language-btn');
const languageMenu = document.getElementById('language-menu');
const currentLanguageText = document.getElementById('current-language-text');
const languageListDropdown = document.getElementById('language-list-dropdown');
const headerCopyCodeBtn = document.getElementById('header-copy-code-btn');
const toastContainer = document.getElementById('toast-container');
// --- Core State Variables ---
let projects = [];
let currentProjectId = null;
let selectedLanguages = ['Javascript'];
let activeView = 'editor'; // 'editor', 'preview', 'terminal'
class JungleStorage {
    static getProjects() {
        const data = localStorage.getItem('jungle_sandbox_projects');
        if (data) {
            try { return JSON.parse(data); } catch(e) { return this.getDefaultProjects(); }
        }
        return this.getDefaultProjects();
    }
    static saveProjects(list) { localStorage.setItem('jungle_sandbox_projects', JSON.stringify(list)); }
    static getDefaultProjects() { return []; }
}
// --- Smart Code Analysis and Error Diagnostic Modules ---
class JungleScanner {
    static scan(lang, code) {
        let errors = [];
        let stack = [];
        let bracketPairs = { '(': ')', '[': ']', '{': '}' };
        let matchingPairs = { ')': '(', ']': '[', '}': '{' };
        let lines = code.split('\n');
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            let lineNum = i + 1;
            let inQuotes = null;
            for (let j = 0; j < line.length; j++) {
                let char = line[j];
                if ((char === '"' || char === "'") && line[j-1] !== '\\') {
                    if (inQuotes === char) { inQuotes = null; } else if (!inQuotes) { inQuotes = char; }
                }
                if (!inQuotes) {
                    if (bracketPairs[char]) { stack.push({ char: char, line: lineNum }); }
                    else if (matchingPairs[char]) {
                        if (stack.length === 0) { errors.push({ line: lineNum, msg: `Mismatched closing bracket '${char}' without matching opener.` }); }
                        else {
                            let last = stack.pop();
                            if (last.char !== matchingPairs[char]) { errors.push({ line: lineNum, msg: `Mismatched closing bracket '${char}' - expected match for '${last.char}' from line ${last.line}.` }); }
                        }
                    }
                }
            }
        }
        while (stack.length > 0) {
            let unclosed = stack.pop();
            errors.push({ line: unclosed.line, msg: `Unclosed bracket or delimiter '${unclosed.char}' detected.` });
        }
        if (lang === 'HTML') {
            let openTags = (code.match(/<[a-zA-Z0-9:-]+/g) || []).length;
            let closeTags = (code.match(/<\/[a-zA-Z0-9:-]+/g) || []).length;
            if (openTags !== closeTags) { errors.push({ line: 1, msg: `Structural tag count mismatch: Detected ${openTags} opening tags but only ${closeTags} closing tags.` }); }
        }
        return errors;
    }
    static detectLanguage(code) {
        if (!code || code.trim().length < 5) return null;
        let pyScore = 0, jsScore = 0, htmlScore = 0, cppScore = 0, javaScore = 0;
        if (code.includes('def ') && code.includes(':')) pyScore += 15;
        if (code.includes('elif ')) pyScore += 10;
        if (code.includes('import ') && !code.includes('from') && !code.includes('import {')) pyScore += 5;
        if (code.includes('print(') && !code.includes('System.out') && !code.includes('console.log')) pyScore += 5;
        if ((code.match(/(^|\n)\s*#/g) || []).length > 0) pyScore += 10;
        if (code.includes('const ') || code.includes('let ')) jsScore += 12;
        if (code.includes('console.log')) jsScore += 15;
        if (code.includes('function ') && !code.includes('def ')) jsScore += 8;
        if (code.includes('=>') && !code.includes('==>')) jsScore += 10;
        if (code.includes('document.get') || code.includes('window.')) jsScore += 10;
        if (code.toLowerCase().includes('<!doctype html>')) htmlScore += 25;
        if (code.toLowerCase().includes('<html') || code.toLowerCase().includes('<body')) htmlScore += 20;
        if (code.toLowerCase().includes('</div>') || code.toLowerCase().includes('</p>')) htmlScore += 15;
        if (code.includes('#include <')) cppScore += 25;
        if (code.includes('std::cout') || code.includes('cout <<')) cppScore += 20;
        if (code.includes('int main()')) cppScore += 15;
        if (code.includes('public class ') && code.includes('{')) javaScore += 20;
        if (code.includes('public static void main')) javaScore += 25;
        if (code.includes('System.out.print')) javaScore += 20;
        let scores = [
            { lang: 'Python', score: pyScore, ext: '.py' },
            { lang: 'Javascript', score: jsScore, ext: '.js' },
            { lang: 'HTML', score: htmlScore, ext: '.html' },
            { lang: 'C++', score: cppScore, ext: '.cpp' },
            { lang: 'Java', score: javaScore, ext: '.java' }
        ];
        scores.sort((a, b) => b.score - a.score);
        return scores[0].score >= 8 ? scores[0] : null;
    }
}
class JungleRunner {
    static async execute(lang, code, files) {
        try {
            const scanErrors = JungleScanner.scan(lang, code);
            if (scanErrors.length > 0) {
                const errorMsg = scanErrors[0].msg;
                const lineNo = scanErrors[0].line;
                switchView('terminal', false);
                terminalStatus.textContent = "FAILED TO RUN";
                terminalStatus.className = "text-rose-500 font-bold";
                const errorDetails = { file: "main.py", lineNo: lineNo, errorMsg: errorMsg };
                this.printCrashAnalysis(errorDetails, "", "");
                JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => {
                    switchView('terminal', false);
                    this.printCrashAnalysis(errorDetails, "", "");
                });
                return;
            }
            switchView('terminal', false);
            terminalViewBody.textContent = "Connecting to Piston API...";
            terminalStatus.textContent = "RUNNING";
            terminalStatus.className = "text-[#74a896] font-bold animate-pulse";
            const languageMap = { 'Javascript': 'javascript', 'Python': 'python', 'C++': 'cpp', 'Java': 'java', 'TypeScript': 'typescript', 'C': 'c', 'C#': 'csharp', 'Ruby': 'ruby', 'Go': 'go', 'Rust': 'rust', 'PHP': 'php', 'Swift': 'swift', 'Kotlin': 'kotlin', 'Scala': 'scala', 'R': 'r', 'Perl': 'perl', 'Haskell': 'haskell', 'Julia': 'julia', 'Lua': 'lua', 'Clojure': 'clojure', 'Elixir': 'elixir', 'Erlang': 'erlang', 'OCaml': 'ocaml', 'F#': 'fsharp', 'Dart': 'dart', 'Bash': 'bash', 'Fortran': 'fortran', 'COBOL': 'cobol', 'D': 'd', 'Zig': 'zig', 'Nim': 'nim', 'Assembly': 'nasm', 'Lisp': 'commonlisp', 'Prolog': 'prolog', 'Pascal': 'pascal' };
            const pistonLang = languageMap[lang] || 'javascript';
            const p = JungleUI.getCurrentProject();
            if (!p) return;
            const filesArray = [{ name: p.currentFile || 'main.py', content: code }];
            Object.keys(p.files).forEach(filename => {
                if (filename !== p.currentFile) { filesArray.push({ name: filename, content: p.files[filename] }); }
            });
            const payload = { language: pistonLang, version: "*", files: filesArray };
            const endpoints = [
                { name: "EMKC Primary API Hub", url: "https://emkc.org/api/v2/piston/execute" },
                { name: "Purdue University Mirror", url: "https://piston.engineering.purdue.edu/api/v2/piston/execute" },
                { name: "CORS-Proxied EMKC Node", url: "https://corsproxy.io/?https://emkc.org/api/v2/piston/execute" },
                { name: "CORS-Proxied Purdue Node", url: "https://corsproxy.io/?https://piston.engineering.purdue.edu/api/v2/piston/execute" }
            ];
            let responseReceived = false, result = null, errorReports = [];
            for (let i = 0; i < endpoints.length; i++) {
                const currentTarget = endpoints[i];
                if (i > 0) { terminalViewBody.textContent += `\n⚠️ Node [${endpoints[i-1].name}] failed or blocked. Failover: Routing to ${currentTarget.name}...`; }
                try {
                    const response = await fetch(currentTarget.url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    result = await response.json();
                    responseReceived = true;
                    break;
                } catch (err) { errorReports.push(`${currentTarget.name}: ${err.message}`); }
            }
            if (responseReceived && result && result.run) {
                const stdout = result.run.stdout || '';
                const stderr = result.run.stderr || '';
                terminalViewBody.textContent = "";
                if (stderr || result.run.code !== 0) {
                    const errorDetails = this.parseError(stderr, stdout, lang);
                    this.printCrashAnalysis(errorDetails, stdout, stderr);
                    JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => {
                        switchView('terminal', false);
                        this.printCrashAnalysis(errorDetails, stdout, stderr);
                    });
                    terminalStatus.textContent = "FAILED TO RUN";
                    terminalStatus.className = "text-rose-500 font-bold";
                } else {
                    terminalViewBody.textContent = stdout || "Program executed successfully with no output.";
                    terminalStatus.textContent = "SUCCESS";
                    terminalStatus.className = "text-emerald-400 font-bold";
                }
            } else {
                terminalStatus.textContent = "CLUSTER OFFLINE";
                terminalStatus.className = "text-rose-500 font-bold";
                terminalViewBody.textContent = "=========================================================\n❌ JUNGLE COMPILER CLUSTER REJECTION ERROR (CORS BLOCK)\n=========================================================\nFailover routes attempted:\n" + errorReports.map((report, idx) => `  [Node ${idx + 1}] ${report}`).join('\n') + "\n\nDIAGNOSIS:\nStrict Iframe Sandbox Content Security Policies (CSP) blocked the connection streams to the remote container sandbox. Try running inside a separate browser tab or local instance to unlock secure remote compilation API segments.\n=========================================================";
            }
        } catch (globalErr) { this.handleGlobalFailure(globalErr); }
        terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
    }
    static handleGlobalFailure(err) {
        switchView('terminal', false);
        terminalStatus.textContent = "FAILED TO RUN";
        terminalStatus.className = "text-rose-500 font-bold";
        terminalViewBody.textContent = "=========================================================\n❌ JUNGLE CRASH REPORT GENERATOR (ENVIRONMENT FAILURE)\n=========================================================\nFAILED TO COMPILE OR EXECUTE LOGIC STREAMS\nDetails: " + (err.message || err) + "\n=========================================================\n";
        JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => { var_switchView('terminal', false); });
    }
    static parseError(stderr, stdout, lang) {
        let errorMsg = "Execution anomaly detected.", lineNo = "Unknown line", file = "main.py";
        const combined = (stderr || "") + "\n" + (stdout || "");
        if (lang === 'Python') {
            const match = combined.match(/File\s+"([^"]+)",\s+line\s+(\d+)/i);
            if (match) { file = match[1]; lineNo = match[2]; }
            const lines = combined.trim().split('\n');
            for (let i = lines.length - 1; i >= 0; i--) {
                const l = lines[i].trim();
                if (l && (l.includes('Error:') || l.includes('Exception:') || l.match(/^[a-zA-Z0-9_]+Error:/))) { errorMsg = l; break; }
            }
            if (errorMsg === "Execution anomaly detected." && lines.length > 0) { errorMsg = lines[lines.length - 1]; }
        } else if (lang === 'Javascript' || lang === 'TypeScript') {
            const lines = combined.trim().split('\n');
            if (lines[0]) errorMsg = lines[0];
            const match = combined.match(/\/([^/:\s]+):(\d+):(\d+)/) || combined.match(/at\s+.*:(\d+):(\d+)/);
            if (match) {
                if (match.length > 2) { file = match[1] || "main.js"; lineNo = match[2]; } else { lineNo = match[1]; }
            }
        } else if (lang === 'C++' || lang === 'Java') {
            const match = combined.match(/([^:\n]+):(\d+):(?:\d+:)?\s+error:\s+(.+)/i);
            if (match) { file = match[1]; lineNo = match[2]; errorMsg = match[3]; }
        }
        return { errorMsg, lineNo, file };
    }
    static printCrashAnalysis(details, stdout, stderr) {
        terminalViewBody.textContent = "=========================================================\n❌ JUNGLE CRASH REPORT GENERATOR\n=========================================================\nWHAT WENT WRONG: " + details.errorMsg + "\nWHERE IT IS:     File \"" + details.file + "\", Line " + details.lineNo + "\n=========================================================\n";
        terminalViewBody.scrollTop = 0;
    }
}
function executeTerminalCommand(cmdLine) {
    if (activeView !== 'terminal') return;
    terminalViewBody.textContent += `\njungle:~# ${cmdLine}\n`;
    const parts = cmdLine.split(' '), command = parts[0].toLowerCase(), args = parts.slice(1), p = JungleUI.getCurrentProject();
    switch (command) {
        case 'help': terminalViewBody.textContent += "Available shell commands:\n  run          - Compile and run active file inside sandbox\n  ls           - List all project file nodes\n  clear        - Clear console workspace output streams\n  cat [file]   - Output the file text data lines\n  info         - Inspect environment compiler metadata\n"; break;
        case 'clear': terminalViewBody.textContent = "Console output cleared."; break;
        case 'ls':
            if (!p) { terminalViewBody.textContent += "Error: No project open.\n"; } else {
                terminalViewBody.textContent += `Files inside [${p.name}]:\n` + Object.keys(p.files).map(f => `  📄 ${f}`).join('\n') + `\n`;
            }
            break;
        case 'run':
            if (!p) { terminalViewBody.textContent += "Error: Load a project first.\n"; } else { JungleRunner.execute(selectedLanguages[0], p.files[p.currentFile], p.files); }
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
class JungleUI {
    static showToast(message, onClickHandler = null) {
        const toast = document.createElement('div');
        toast.className = 'jungle-toast flex items-center justify-between gap-4 ' + (onClickHandler ? 'cursor-pointer hover:bg-[#1a2320]' : '');
        const textSpan = document.createElement('span');
        textSpan.textContent = message;
        toast.appendChild(textSpan);
        if (onClickHandler) {
            const actionNotice = document.createElement('span');
            actionNotice.className = 'text-[10px] uppercase font-bold text-[#74a896] border-l border-[#2e3c37] pl-3 shrink-0';
            actionNotice.textContent = 'Inspect';
            toast.appendChild(actionNotice);
            toast.onclick = () => { onClickHandler(); toast.remove(); };
        }
        toastContainer.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 5000);
    }
    static getCurrentProject() { return projects.find(p => p.id === currentProjectId); }
    static loadProject(id) {
        currentProjectId = id;
        const p = this.getCurrentProject();
        if (!p) return;
        this.renderFilesList();
        this.switchToFile(p.currentFile || Object.keys(p.files)[0]);
        projectsDashboard.classList.remove('show');
        workspaceContainer.style.display = 'flex';
        this.showToast(`Switched workspace to ${p.name}`);
    }
    static renameProject(id) {
        const project = projects.find(proj => proj.id === id);
        if (!project) return;
        this.showCustomModal({
            title: "Rename Project",
            placeholder: "New project name...",
            description: `Currently: ${project.name}`,
            onConfirm: (newName) => {
                if (!newName) return;
                project.name = newName;
                JungleStorage.saveProjects(projects);
                this.renderProjectsDashboard();
                this.showToast(`Project renamed to ${newName}`);
            }
        });
    }
    static deleteProject(id) {
        const project = projects.find(proj => proj.id === id);
        if (!project) return;
        this.showCustomModal({
            title: "Delete Project",
            placeholder: null,
            description: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
            onConfirm: () => {
                projects = projects.filter(proj => proj.id !== id);
                JungleStorage.saveProjects(projects);
                this.renderProjectsDashboard();
                this.showToast(`Deleted project "${project.name}"`);
            }
        });
    }
    static renderProjectsDashboard() {
        const grid = document.getElementById('dashboard-grid');
        grid.innerHTML = '';
        projects.forEach(p => {
            const card = document.createElement('div');
            card.className = 'project-card';
            card.onclick = () => this.loadProject(p.id);
            card.innerHTML = `
                <div class="project-card-actions">
                    <button class="action-btn rename-proj-btn" title="Rename Project">✏️</button>
                    <button class="action-btn delete-proj-btn" title="Delete Project">🗑️</button>
                </div>
                <div>
                    <h3 class="truncate text-teal-300 font-bold pr-16">📁 ${p.name}</h3>
                    <div class="project-meta mt-2">
                        <span>Total Files: ${Object.keys(p.files).length}</span>
                        <span>Default: ${p.lang || 'General'}</span>
                    </div>
                </div>
            `;
            card.querySelector('.rename-proj-btn').onclick = (e) => {
                e.stopPropagation();
                this.renameProject(p.id);
            };
            card.querySelector('.delete-proj-btn').onclick = (e) => {
                e.stopPropagation();
                this.deleteProject(p.id);
            };
            grid.appendChild(card);
        });
        const createCard = document.createElement('div');
        createCard.className = 'new-project-card';
        createCard.innerHTML = `<div class="plus-icon">+</div><span>New Project</span>`;
        createCard.onclick = () => {
            this.showCustomModal({
                title: "New Project Name",
                placeholder: "e.g., Python math analyzer",
                onConfirm: (name) => {
                    if (!name) return;
                    const newId = 'proj_' + Date.now();
                    const newProj = {
                        id: newId,
                        name: name,
                        files: { 'index.html': '' },
                        currentFile: 'index.html',
                        lang: 'HTML'
                    };
                    projects.push(newProj);
                    JungleStorage.saveProjects(projects);
                    this.renderProjectsDashboard();
                    this.loadProject(newId);
                }
            });
        };
        grid.appendChild(createCard);
    }
    static renderFilesList() {
        fileListContainer.innerHTML = '';
        const p = this.getCurrentProject();
        if (!p) return;
        Object.keys(p.files).forEach(filename => {
            const li = document.createElement('li');
            if (filename === p.currentFile) li.classList.add('active');
            const title = document.createElement('span');
            title.className = "flex-1 overflow-hidden truncate pointer-events-auto cursor-pointer";
            title.textContent = '📄 ' + filename;
            title.onclick = () => this.switchToFile(filename);
            const actions = document.createElement('div');
            actions.className = 'file-item-actions';
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'action-btn delete';
            deleteBtn.innerHTML = '🗑️';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                this.deleteFile(filename);
            };
            actions.appendChild(deleteBtn);
            li.appendChild(title);
            if (filename !== 'index.html' && filename !== 'main.py') {
                li.appendChild(actions);
            }
            fileListContainer.appendChild(li);
        });
    }
    static deleteFile(name) {
        const p = this.getCurrentProject();
        if (!p) return;
        delete p.files[name];
        if (p.currentFile === name) {
            p.currentFile = Object.keys(p.files)[0];
        }
        this.renderFilesList();
        this.switchToFile(p.currentFile);
        JungleStorage.saveProjects(projects);
        this.showToast(`Deleted file ${name}`);
    }
    static switchToFile(filename) {
        const p = this.getCurrentProject();
        if (!p) return;
        p.currentFile = filename;
        currentFileLabel.textContent = filename;
        editor.value = p.files[filename] || '';
        document.querySelectorAll('#file-list li').forEach(item => {
            const cleanName = item.textContent.replace('📄 ', '').replace('🗑️', '').trim();
            if (cleanName === filename) item.classList.add('active');
            else item.classList.remove('active');
        });
        if (filename.endsWith('.py')) {
            selectedLanguages = ['Python'];
        } else if (filename.endsWith('.html') || filename.endsWith('.htm')) {
            selectedLanguages = ['HTML'];
        } else if (filename.endsWith('.cpp')) {
            selectedLanguages = ['C++'];
        } else if (filename.endsWith('.java')) {
            selectedLanguages = ['Java'];
        } else if (filename.endsWith('.ts')) {
            selectedLanguages = ['TypeScript'];
        } else {
            selectedLanguages = ['Javascript'];
        }
        currentLanguageText.textContent = `Language: ${selectedLanguages[0]}`;
        switchView('editor');
        this.updateCodeHighlight();
        this.updateLinesOfCodeCount();
        JungleStorage.saveProjects(projects);
    }
    static updateCodeHighlight() {
        let code = editor.value;
        if (code.endsWith('\n')) code += ' ';
        let escaped = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const lang = selectedLanguages[0];
        if (lang === 'Python') {
            const pyRegex = /(#.*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\b(def|class|return|if|elif|else|while|for|in|import|from|print|try|except|break|continue|and|or|not|True|False|None)\b|\b(\d+)\b/g;
            escaped = escaped.replace(pyRegex, (m, g1, g2, g3, g4) => {
                if (g1) return `<span class="token-comment">${g1}</span>`;
                if (g2) return `<span class="token-string">${g2}</span>`;
                if (g3) return `<span class="token-keyword">${g3}</span>`;
                if (g4) return `<span class="token-number">${g4}</span>`;
                return m;
            });
        } else if (lang === 'HTML') {
            const htmlRegex = /(&lt;!--[\s\S]*?--&gt;)|(&lt;\/?[a-zA-Z0-9:-]+(?:\s+[^&]*)?&gt;)/g;
            escaped = escaped.replace(htmlRegex, (m, g1, g2) => {
                if (g1) return `<span class="token-comment">${g1}</span>`;
                if (g2) {
                    let tagContent = g2;
                    tagContent = tagContent.replace(/(\s+[a-zA-Z0-9:-]+)=/g, '<span class="token-type">$1</span>=');
                    tagContent = tagContent.replace(/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')/g, '<span class="token-string">$1</span>');
                    return `<span class="token-keyword">${tagContent}</span>`;
                }
                return m;
            });
        } else {
            const jsRegex = /(\/\/.*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)|\b(const|let|var|function|return|if|else|while|for|import|export|class|new|this|true|false|null|async|await|void|public|private|protected|static|struct)\b|\b(\d+)\b/g;
            escaped = escaped.replace(jsRegex, (m, g1, g2, g3, g4) => {
                if (g1) return `<span class="token-comment">${g1}</span>`;
                if (g2) return `<span class="token-string">${g2}</span>`;
                if (g3) return `<span class="token-keyword">${g3}</span>`;
                if (g4) return `<span class="token-number">${g4}</span>`;
                return m;
            });
        }
        highlightOverlay.innerHTML = escaped;
        this.updateLineNumbers();
    }
    static updateLineNumbers() {
        const count = editor.value.split('\n').length;
        lineGutter.textContent = Array.from({length: count}, (_, i) => i + 1).join('\n') + '\n';
    }
    static updateLinesOfCodeCount() {
        const code = editor.value;
        locDisplay.textContent = `LOC: ${code.split('\n').length}`;
    }
    static showCustomModal({ title, placeholder, onConfirm, description = "" }) {
        const modal = document.getElementById('custom-modal');
        const mTitle = document.getElementById('modal-title');
        const mInput = document.getElementById('modal-input');
        const mCancel = document.getElementById('modal-cancel');
        const mConfirm = document.getElementById('modal-confirm');
        const mBodyText = document.getElementById('modal-body-text');
        mTitle.textContent = title;
        if (description) {
            mBodyText.textContent = description;
            mBodyText.style.display = 'block';
        } else {
            mBodyText.style.display = 'none';
        }
        if (placeholder === null) {
            mInput.style.display = 'none';
        } else {
            mInput.style.display = 'block';
            mInput.placeholder = placeholder;
            mInput.value = '';
        }
        modal.classList.add('show');
        mConfirm.onclick = () => {
            onConfirm(mInput.value.trim());
            modal.classList.remove('show');
        };
        mCancel.onclick = () => {
            modal.classList.remove('show');
        };
    }
}
enterBtn.onclick = () => { splashScreen.classList.add('fade-out'); setTimeout(() => { splashScreen.style.display = 'none'; splashScreen.style.pointerEvents = 'none'; }, 400); projectsDashboard.classList.add('show'); JungleUI.renderProjectsDashboard(); };
exitToSplashBtn.onclick = () => { splashScreen.style.display = 'flex'; splashScreen.style.pointerEvents = 'auto'; setTimeout(() => splashScreen.classList.remove('fade-out'), 50); projectsDashboard.classList.remove('show'); };
exitToHubHeaderBtn.onclick = () => { workspaceContainer.style.display = 'none'; projectsDashboard.classList.add('show'); JungleUI.renderProjectsDashboard(); };
addFileBtn.onclick = () => {
    JungleUI.showCustomModal({
        title: "Create Project File",
        placeholder: "e.g., helpers.py, styles.css",
        onConfirm: (name) => {
            if (!name) return;
            const p = JungleUI.getCurrentProject();
            if (!p) return;
            p.files[name] = '';
            JungleUI.renderFilesList();
            JungleUI.switchToFile(name);
            JungleStorage.saveProjects(projects);
            JungleUI.showToast(`File ${name} created`);
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
            const newProj = {
                id: newId,
                name: name,
                files: { 'index.html': '' },
                currentFile: 'index.html',
                lang: 'HTML'
            };
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
    terminalViewBody.textContent = '=========================================================\n❌ JUNGLE HTML RUNTIME/SYNTAX EXCEPTION DETECTED\n=========================================================\nERROR MESSAGE: ' + message + '\nWHERE IT IS:   Line ' + lineno + ', Col ' + colno + '\n=========================================================\n';
    JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => {
        switchView('terminal', false);
    });
};
runBtn.onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p) return;
    const isHtml = p.currentFile.endsWith('.html') || p.currentFile.endsWith('.htm');
    if (isHtml) {
        try {
            terminalStatus.textContent = "READY";
            terminalStatus.className = "text-[#74a896]";
            switchView('preview');
            const iframeWin = previewFrame.contentWindow, doc = iframeWin.document;
            let frameCompileError = false;
            iframeWin.onerror = function(message, source, lineno, colno) { frameCompileError = true; window.handleIframeError(message, source, lineno, colno); return true; };
            doc.open();
            const errorBubbleInjectedCode = `<script>window.onerror = function(m, s, l, c) { if (window.parent && window.parent.handleIframeError) { window.parent.handleIframeError(m, s, l, c); } return true; };<\/script>` + p.files[p.currentFile];
            doc.write(errorBubbleInjectedCode);
            doc.close();
            setTimeout(() => { if (!frameCompileError) JungleUI.showToast("Webpage loaded successfully in Preview panel."); }, 150);
        } catch(e) {
            console.error("Frame writing blocked", e);
            switchView('terminal', false);
            terminalStatus.textContent = "FAILED TO RUN";
            terminalStatus.className = "text-rose-500 font-bold";
            terminalViewBody.textContent = `Failed to write preview frame container: ${e.message}`;
            JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => { switchView('terminal', false); });
        }
    } else { JungleRunner.execute(selectedLanguages[0], p.files[p.currentFile], p.files); }
};
tabPreview.onclick = runBtn.onclick;
tabTerminalBtn.onclick = () => { switchView('terminal', true); JungleUI.showToast("Switched output channel to Terminal Console view."); };
projectTitleBtn.onclick = () => { switchView('editor'); };
languageBtn.onclick = (e) => { e.stopPropagation(); languageMenu.classList.toggle('show'); };
window.onclick = () => { languageMenu.classList.remove('show'); };
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
editor.oninput = () => {
    const p = JungleUI.getCurrentProject();
    if (!p || !p.currentFile) return;
    p.files[p.currentFile] = editor.value;
    JungleUI.updateLinesOfCodeCount();
    JungleStorage.saveProjects(projects);
    const code = editor.value, detection = JungleScanner.detectLanguage(code);
    if (detection) {
        const detectedLang = detection.lang;
        if (detectedLang !== selectedLanguages[0]) {
            selectedLanguages = [detectedLang];
            currentLanguageText.textContent = `Language: ${detectedLang}`;
            const filenameNoExt = p.currentFile.split('.')[0] || 'main';
            const newFilename = filenameNoExt + detection.ext;
            if (newFilename !== p.currentFile) {
                const fileContent = p.files[p.currentFile];
                delete p.files[p.currentFile];
                p.files[newFilename] = fileContent;
                p.currentFile = newFilename;
                currentFileLabel.textContent = newFilename;
                JungleUI.renderFilesList();
            }
            JungleUI.showToast(`Auto-detected environment: swapped to ${detectedLang}!`);
        }
    }
    JungleUI.updateCodeHighlight();
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
window.onload = () => {
    projects = JungleStorage.getProjects();
    const langs = ["Assembly","Bash","C","C#","C++","Clojure","COBOL","D","Dart","Elixir","Erlang","F#","Fortran","Go","Haskell","HTML","Java","Javascript","Julia","Kotlin","Lisp","Lua","Nim","OCaml","Pascal","Perl","PHP","Prolog","Python","R","Ruby","Rust","Scala","Swift","TypeScript","Zig"];
    languageListDropdown.innerHTML = langs.map(l => `<li data-lang="${l === 'HTML' ? 'HTML' : l}">${l === 'HTML' ? 'HTML / Webpage' : l}</li>`).join('');
    document.querySelectorAll('#language-list-dropdown li').forEach(item => {
        item.onclick = (e) => {
            const targetLang = item.getAttribute('data-lang');
            selectedLanguages = [targetLang];
            currentLanguageText.textContent = `Language: ${targetLang}`;
            languageMenu.classList.remove('show');
            const p = JungleUI.getCurrentProject();
            if (p) {
                if (targetLang === 'Python' && !p.currentFile.endsWith('.py')) {
                    const firstPy = Object.keys(p.files).find(f => f.endsWith('.py'));
                    if (firstPy) JungleUI.switchToFile(firstPy);
                } else if (targetLang === 'HTML' && !p.currentFile.endsWith('.html')) {
                    const firstHtml = Object.keys(p.files).find(f => f.endsWith('.html'));
                    if (firstHtml) JungleUI.switchToFile(firstHtml);
                }
            }
        };
    });
};
