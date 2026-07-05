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
var tabConsoleBtn = document.getElementById('tab-console');
var consoleViewContainer = document.getElementById('console-view-container');
var consoleViewBody = document.getElementById('console-view-body');
var consoleStatus = document.getElementById('console-status');
// --- Core State Variables ---
var projects = [];
var currentProjectId = null;
var selectedLanguages = ['Javascript'];
var activeView = 'editor'; // 'editor', 'preview', 'terminal', 'console'
var manualLanguageOverride = false;
var terminalHistory = [];
var terminalHistoryIdx = -1;

function showConsoleIssues(issues, filename) {
    if (!issues || issues.length === 0) {
        consoleViewBody.innerHTML = `<span style="color:#74a896">✓ No issues detected in ${filename || 'current file'}.</span>`;
        consoleStatus.textContent = 'CLEAR';
        consoleStatus.style.color = '#74a896';
        return;
    }
    const errors = issues.filter(i => i.severity === 'error');
    const warnings = issues.filter(i => i.severity === 'warning');
    const infos = issues.filter(i => i.severity === 'info');
    consoleStatus.textContent = errors.length ? `${errors.length} ERROR${errors.length > 1 ? 'S' : ''}` : `${warnings.length} WARN`;
    consoleStatus.style.color = errors.length ? '#FF5555' : '#FFB86C';
    const rows = issues.map(i => {
        const color = i.severity === 'error' ? '#FF5555' : i.severity === 'warning' ? '#FFB86C' : '#74a896';
        const icon = i.severity === 'error' ? '✗' : i.severity === 'warning' ? '⚠' : 'ℹ';
        const hint = i.hint ? `\n       💡 ${i.hint}` : '';
        return `<span style="color:${color}">${icon} Line ${i.line || '?'}  [${i.kind || i.severity}]  ${i.msg}${hint}</span>`;
    }).join('\n');
    consoleViewBody.innerHTML = `<span style="color:#4a6057">${filename || 'file'} — ${issues.length} issue${issues.length > 1 ? 's' : ''}</span>\n${'─'.repeat(44)}\n${rows}`;
}
function terminalPrint(text) {
    terminalViewBody.textContent += text;
    terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
}
function executeTerminalCommand(cmdLine) {
    const raw = cmdLine.trim();
    if (!raw) return;
    terminalHistory.unshift(raw);
    terminalHistoryIdx = -1;
    terminalPrint(`\njungle:~$ ${raw}\n`);
    // Handle pipes: cmd1 | cmd2 (basic: only passes stdout of first as stdin to second)
    const parts = raw.split(/\s+/);
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);
    const p = JungleUI.getCurrentProject();
    const files = p ? Object.keys(p.files) : [];
    const now = new Date();

    switch (command) {
        case 'help':
            terminalPrint(
`Jungle Terminal — available commands:

  FILE SYSTEM
    ls [path]          List project files
    cat <file>         Print file contents
    head <file>        First 10 lines of a file
    tail <file>        Last 10 lines of a file
    wc <file>          Word/line/char count
    grep <pat> <file>  Search for pattern in file
    touch <file>       Create an empty file
    rm <file>          Delete a file
    mv <old> <new>     Rename a file
    cp <src> <dst>     Copy a file
    pwd                Print working directory
    mkdir <name>       Create a directory (virtual)
    stat <file>        File info

  CODE
    run                Compile & run current file
    run <file>         Compile & run a specific file
    node <file>        Run JS file with Node.js
    python <file>      Run Python file
    python3 <file>     Run Python file
    g++ <file>         Compile & run C++ file
    gcc <file>         Compile & run C file
    javac <file>       Compile & run Java file
    tsc <file>         Compile TypeScript file
    analyze            Run static analysis on current file
    lint               Alias for analyze
    fmt                Format active file (auto-indent)

  ENVIRONMENT
    env                Show environment variables
    echo <text>        Print text
    date               Print current date/time
    whoami             Print current user
    hostname           Print hostname
    uname              System info
    uptime             Session uptime

  TERMINAL
    history            Show command history
    clear              Clear terminal
    open <file>        Switch editor to file
    info               Show project info
    exit               Return to editor view
`);
            break;

        case 'clear':
            terminalViewBody.textContent = 'Jungle Terminal — type \'help\' for commands.\n';
            break;

        case 'pwd':
            terminalPrint(`/workspace/${p ? p.name.replace(/\s+/g, '-').toLowerCase() : 'project'}\n`);
            break;

        case 'whoami':
            terminalPrint(`jungle-user\n`);
            break;

        case 'hostname':
            terminalPrint(`jungle-sandbox\n`);
            break;

        case 'uname':
            terminalPrint(`Linux jungle-sandbox 6.1.0 #1 SMP x86_64 GNU/Linux\n`);
            break;

        case 'date':
            terminalPrint(`${now.toDateString()} ${now.toTimeString().split(' ')[0]}\n`);
            break;

        case 'uptime':
            terminalPrint(`up 0 days, session active — jungle sandbox\n`);
            break;

        case 'env':
            terminalPrint(`SHELL=/bin/bash\nLANG=en_US.UTF-8\nTERM=xterm-256color\nUSER=jungle-user\nHOME=/workspace\nPATH=/usr/local/bin:/usr/bin:/bin\nEDITOR=jungle\nJUNGLE_VERSION=1.0.0\n`);
            break;

        case 'echo':
            terminalPrint(args.join(' ').replace(/^["']|["']$/g, '') + '\n');
            break;

        case 'ls':
            if (!p) { terminalPrint(`ls: no project open\n`); break; }
            if (files.length === 0) { terminalPrint(`(empty project)\n`); break; }
            terminalPrint(files.map(f => {
                const lines = (p.files[f] || '').split('\n').length;
                const ext = f.split('.').pop();
                return `${f.padEnd(28)} ${String(lines).padStart(4)} lines`;
            }).join('\n') + '\n');
            break;

        case 'cat':
            if (!args[0]) { terminalPrint(`cat: missing operand\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`cat: ${args[0]}: No such file\n`); break; }
            terminalPrint((p.files[args[0]] || '(empty)') + '\n');
            break;

        case 'head': {
            if (!args[0]) { terminalPrint(`head: missing operand\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`head: ${args[0]}: No such file\n`); break; }
            const headLines = (p.files[args[0]] || '').split('\n').slice(0, 10).join('\n');
            terminalPrint(headLines + '\n');
            break;
        }

        case 'tail': {
            if (!args[0]) { terminalPrint(`tail: missing operand\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`tail: ${args[0]}: No such file\n`); break; }
            const tailLines = (p.files[args[0]] || '').split('\n').slice(-10).join('\n');
            terminalPrint(tailLines + '\n');
            break;
        }

        case 'wc': {
            if (!args[0]) { terminalPrint(`wc: missing operand\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`wc: ${args[0]}: No such file\n`); break; }
            const content = p.files[args[0]] || '';
            const lineCount = content.split('\n').length;
            const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
            const charCount = content.length;
            terminalPrint(`${String(lineCount).padStart(6)} ${String(wordCount).padStart(7)} ${String(charCount).padStart(7)} ${args[0]}\n`);
            break;
        }

        case 'grep': {
            if (args.length < 2) { terminalPrint(`Usage: grep <pattern> <file>\n`); break; }
            if (!p || p.files[args[1]] === undefined) { terminalPrint(`grep: ${args[1]}: No such file\n`); break; }
            const pattern = args[0].replace(/^\/|\/[gimsuy]*$/g, '');
            let re;
            try { re = new RegExp(pattern, 'i'); } catch { terminalPrint(`grep: invalid pattern\n`); break; }
            const matched = (p.files[args[1]] || '').split('\n')
                .map((l, i) => re.test(l) ? `${String(i+1).padStart(4)}: ${l}` : null)
                .filter(Boolean);
            terminalPrint(matched.length ? matched.join('\n') + '\n' : `(no matches)\n`);
            break;
        }

        case 'touch':
            if (!args[0]) { terminalPrint(`touch: missing file operand\n`); break; }
            if (!p) { terminalPrint(`touch: no project open\n`); break; }
            if (p.files[args[0]] !== undefined) { terminalPrint(`touch: ${args[0]}: already exists\n`); break; }
            p.files[args[0]] = '';
            JungleStor.save(projects);
            JungleUI.renderFileList();
            terminalPrint(`Created: ${args[0]}\n`);
            break;

        case 'rm':
            if (!args[0]) { terminalPrint(`rm: missing operand\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`rm: ${args[0]}: No such file\n`); break; }
            if (Object.keys(p.files).length <= 1) { terminalPrint(`rm: cannot remove last file\n`); break; }
            delete p.files[args[0]];
            if (p.currentFile === args[0]) p.currentFile = Object.keys(p.files)[0];
            JungleStor.save(projects);
            JungleUI.renderFileList();
            JungleUI.loadFile(p.currentFile);
            terminalPrint(`removed '${args[0]}'\n`);
            break;

        case 'mv':
            if (args.length < 2) { terminalPrint(`Usage: mv <old> <new>\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`mv: ${args[0]}: No such file\n`); break; }
            if (p.files[args[1]] !== undefined) { terminalPrint(`mv: ${args[1]}: already exists\n`); break; }
            p.files[args[1]] = p.files[args[0]];
            delete p.files[args[0]];
            if (p.currentFile === args[0]) p.currentFile = args[1];
            JungleStor.save(projects);
            JungleUI.renderFileList();
            terminalPrint(`'${args[0]}' -> '${args[1]}'\n`);
            break;

        case 'cp':
            if (args.length < 2) { terminalPrint(`Usage: cp <src> <dst>\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`cp: ${args[0]}: No such file\n`); break; }
            p.files[args[1]] = p.files[args[0]];
            JungleStor.save(projects);
            JungleUI.renderFileList();
            terminalPrint(`'${args[0]}' -> '${args[1]}'\n`);
            break;

        case 'mkdir':
            terminalPrint(`mkdir: directories are virtual in Jungle — use touch to create files\n`);
            break;

        case 'stat':
            if (!args[0]) { terminalPrint(`stat: missing operand\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`stat: ${args[0]}: No such file\n`); break; }
            { const c = p.files[args[0]] || ''; terminalPrint(`  File: ${args[0]}\n  Size: ${c.length} bytes\n Lines: ${c.split('\n').length}\n`); }
            break;

        case 'open':
            if (!args[0]) { terminalPrint(`Usage: open <filename>\n`); break; }
            if (!p || p.files[args[0]] === undefined) { terminalPrint(`open: ${args[0]}: No such file\n`); break; }
            JungleUI.switchToFile(args[0]);
            terminalPrint(`Opened ${args[0]}\n`);
            break;

        case 'info':
            if (!p) { terminalPrint(`No project open.\n`); break; }
            terminalPrint(`Project:     ${p.name}\nFile:        ${p.currentFile}\nLanguage:    ${selectedLanguages[0]}\nFiles:       ${files.length}\nTotal LOC:   ${files.reduce((n, f) => n + (p.files[f] || '').split('\n').length, 0)}\nRuntime:     Jungle Sandbox (Judge0 / Piston / WASM)\n`);
            break;

        case 'history':
            terminalPrint(terminalHistory.slice().reverse().map((c, i) => `  ${String(i+1).padStart(3)}  ${c}`).join('\n') + '\n');
            break;

        case 'analyze':
        case 'lint':
            if (!p) { terminalPrint(`No project open.\n`); break; }
            { const issues = JungleScanner.scan(selectedLanguages[0], p.files[p.currentFile] || '');
              if (issues.length === 0) { terminalPrint(`✓ No issues found in ${p.currentFile}\n`); }
              else { terminalPrint(issues.map(i => `  ${i.severity === 'error' ? '✗' : '⚠'} Line ${i.line}: [${i.kind}] ${i.msg}`).join('\n') + '\n'); }
            }
            break;

        case 'fmt':
        case 'format':
            terminalPrint(`fmt: auto-format not yet implemented\n`);
            break;

        case 'exit':
            switchView('editor');
            break;

        case 'run':
            if (!p) { terminalPrint(`No project open.\n`); break; }
            if (args[0]) {
                if (p.files[args[0]] === undefined) { terminalPrint(`run: ${args[0]}: No such file\n`); break; }
                JungleUI.switchToFile(args[0]);
            }
            JungleRunner.execute(selectedLanguages[0], p.files[p.currentFile], p.files);
            break;

        case 'node':
        case 'python':
        case 'python3':
        case 'g++':
        case 'gcc':
        case 'javac':
        case 'tsc': {
            if (!p) { terminalPrint(`No project open.\n`); break; }
            const langMap = { node: 'Javascript', python: 'Python', python3: 'Python', 'g++': 'C++', gcc: 'C', javac: 'Java', tsc: 'TypeScript' };
            const targetFile = args[0] || p.currentFile;
            if (p.files[targetFile] === undefined) { terminalPrint(`${command}: ${targetFile}: No such file\n`); break; }
            JungleRunner.execute(langMap[command], p.files[targetFile], p.files);
            break;
        }

        default:
            terminalPrint(`${command}: command not found — type 'help' for a list of commands\n`);
    }
}
terminalViewContainer.onclick = () => {
    if (activeView === 'terminal') {
        const row = document.getElementById('terminal-input-row');
        row.classList.remove('hidden');
        terminalInput.removeAttribute('disabled');
        terminalInput.focus();
    }
};
terminalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const cmd = terminalInput.value.trim();
        terminalInput.value = '';
        if (cmd) executeTerminalCommand(cmd);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (terminalHistoryIdx < terminalHistory.length - 1) terminalHistoryIdx++;
        terminalInput.value = terminalHistory[terminalHistoryIdx] || '';
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (terminalHistoryIdx > 0) terminalHistoryIdx--;
        else { terminalHistoryIdx = -1; terminalInput.value = ''; return; }
        terminalInput.value = terminalHistory[terminalHistoryIdx] || '';
    } else if (e.key === 'Tab') {
        e.preventDefault();
        const val = terminalInput.value;
        const p = JungleUI.getCurrentProject();
        if (!p) return;
        const candidates = Object.keys(p.files).filter(f => f.startsWith(val.split(' ').pop()));
        if (candidates.length === 1) {
            const parts2 = val.split(' '); parts2[parts2.length - 1] = candidates[0];
            terminalInput.value = parts2.join(' ');
        } else if (candidates.length > 1) {
            terminalPrint('\n' + candidates.join('  ') + '\n');
        }
    }
});
function highlightActiveFile() {
    const p = JungleUI.getCurrentProject();
    if (!p) return;
    document.querySelectorAll('#file-list li[data-file]').forEach(item => {
        if (item.dataset.file === p.currentFile) item.classList.add('active');
        else item.classList.remove('active');
    });
}
function switchView(view, showInput = false) {
    activeView = view;
    editorWrapper.style.display = previewFrame.style.display = terminalViewContainer.style.display = consoleViewContainer.style.display = 'none';
    projectTitleBtn.classList.remove('active');
    tabPreview.classList.remove('active');
    tabConsoleBtn.classList.remove('active');
    tabTerminalBtn.classList.remove('bg-[#1c2522]', 'text-[#74a896]', 'border-[#528b74]');
    terminalInput.setAttribute('disabled', 'true');
    const terminalInputRow = document.getElementById('terminal-input-row');
    terminalInputRow.classList.add('hidden');
    if (view === 'editor') {
        editorWrapper.style.display = 'flex';
    } else if (view === 'preview') {
        previewFrame.style.display = 'block';
        tabPreview.classList.add('active');
    } else if (view === 'terminal') {
        terminalViewContainer.style.display = 'flex';
        tabTerminalBtn.classList.add('bg-[#1c2522]', 'text-[#74a896]', 'border-[#528b74]');
        // Only show interactive input when explicitly opened via the Terminal button
        if (showInput !== false) {
            terminalInputRow.classList.remove('hidden');
            terminalInput.removeAttribute('disabled');
            setTimeout(() => terminalInput.focus(), 50);
        }
    } else if (view === 'console') {
        consoleViewContainer.style.display = 'flex';
        tabConsoleBtn.classList.add('active');
    }
    // Always keep the active file highlighted in the file list
    highlightActiveFile();
}

enterBtn.onclick = () => { splashScreen.classList.add('fade-out'); setTimeout(() => { splashScreen.style.display = 'none'; splashScreen.style.pointerEvents = 'none'; }, 400); projectsDashboard.classList.add('show'); JungleUI.renderProjectsDashboard(); };
exitToSplashBtn.onclick = () => { splashScreen.style.display = 'flex'; splashScreen.style.pointerEvents = 'auto'; setTimeout(() => splashScreen.classList.remove('fade-out'), 50); projectsDashboard.classList.remove('show'); };
exitToHubHeaderBtn.onclick = () => { workspaceContainer.style.display = 'none'; projectsDashboard.classList.add('show'); JungleUI.renderProjectsDashboard(); };
const addItemMenu = document.getElementById('add-item-menu');
function closeAddItemMenu() { addItemMenu.classList.remove('show'); addItemMenu.innerHTML = ''; }
function showPopupMenu(items) {
    addItemMenu.innerHTML = '';
    items.forEach(item => {
        if (item.divider) {
            const div = document.createElement('div');
            div.className = 'popup-menu-divider';
            addItemMenu.appendChild(div);
            return;
        }
        if (item.label && !item.onClick) {
            const lbl = document.createElement('div');
            lbl.className = 'popup-menu-label';
            lbl.textContent = item.label;
            addItemMenu.appendChild(lbl);
            return;
        }
        const el = document.createElement('div');
        el.className = 'popup-menu-item';
        el.textContent = item.text;
        el.onclick = (e) => { e.stopPropagation(); closeAddItemMenu(); item.onClick(); };
        addItemMenu.appendChild(el);
    });
    addItemMenu.classList.add('show');
}
function getExistingFolders(p) {
    const folders = new Set(p.folders || []);
    Object.keys(p.files).forEach(f => { const i = f.indexOf('/'); if (i !== -1) folders.add(f.slice(0, i)); });
    return Array.from(folders).sort();
}
function promptCreateFile(folderPrefix) {
    JungleUI.showCustomModal({
        title: folderPrefix ? `Create File in ${folderPrefix}/` : "Create File",
        placeholder: "e.g., helpers.py",
        onConfirm: (name) => {
            if (!name) return;
            const p = JungleUI.getCurrentProject();
            if (!p) return;
            const fullName = folderPrefix ? `${folderPrefix}/${name}` : name;
            const fileName = JungleIntelligence.sanitizeFileName(fullName, selectedLanguages[0], p.files);
            p.files[fileName] = '';
            JungleUI.renderFilesList();
            JungleUI.switchToFile(fileName);
            JungleStorage.saveProjects(projects);
            JungleUI.showToast(`File ${fileName} created`);
        }
    });
}
function promptCreateFolder(parentPrefix) {
    JungleUI.showCustomModal({
        title: parentPrefix ? `Create Folder in ${parentPrefix}/` : "Create Folder",
        placeholder: "e.g., src, lib, utils",
        onConfirm: (name) => {
            if (!name) return;
            const p = JungleUI.getCurrentProject();
            if (!p) return;
            const clean = name.trim().replace(/[\\/:*?"<>|]+/g, '-').replace(/\s+/g, '-').replace(/^-+|-+$/g, '');
            if (!clean) return;
            const folderName = parentPrefix ? `${parentPrefix}/${clean}` : clean;
            if (!p.folders) p.folders = [];
            if (p.folders.includes(folderName) || Object.keys(p.files).some(f => f.startsWith(folderName + '/'))) {
                JungleUI.showToast(`Folder "${folderName}" already exists`);
                return;
            }
            p.folders.push(folderName);
            JungleUI.collapsedFolders.add(folderName);
            JungleStorage.saveProjects(projects);
            JungleUI.renderFilesList();
            JungleUI.showToast(`Folder ${folderName}/ created`);
        }
    });
}
function promptLocation(kind) {
    const p = JungleUI.getCurrentProject();
    if (!p) return;
    const folders = getExistingFolders(p);
    const items = [
        { label: 'Where?' },
        { text: '🌲 File Tree (root)', onClick: () => kind === 'file' ? promptCreateFile(null) : promptCreateFolder(null) },
    ];
    if (folders.length > 0) {
        items.push({ divider: true });
        folders.forEach(f => items.push({
            text: `📁 ${f}/`,
            onClick: () => kind === 'file' ? promptCreateFile(f) : promptCreateFolder(f)
        }));
    }
    showPopupMenu(items);
}
addFileBtn.onclick = (e) => {
    e.stopPropagation();
    if (addItemMenu.classList.contains('show')) { closeAddItemMenu(); return; }
    showPopupMenu([
        { text: '📄 New File', onClick: () => promptLocation('file') },
        { text: '📁 New Folder', onClick: () => promptLocation('folder') },
    ]);
};
document.addEventListener('click', (e) => {
    if (!addItemMenu.contains(e.target) && e.target !== addFileBtn) closeAddItemMenu();
});
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
    const p = JungleUI.getCurrentProject();
    showConsoleIssues([{ severity: 'error', line: lineno, kind: 'RuntimeError', msg: message, hint: 'Inspect JavaScript near the reported line.' }], (p && p.currentFile) || 'index.html');
    switchView('console');
    JungleUI.showToast("❌ Runtime error — see Console.", () => switchView('console'));
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
tabTerminalBtn.onclick = () => { switchView('terminal', true); };
tabConsoleBtn.onclick = () => { switchView('console'); };
projectTitleBtn.onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p || Object.keys(p.files).length === 0) { switchView('editor'); return; }

    // Detect language per file by extension
    function langFromFilename(name) {
        const ext = name.split('.').pop().toLowerCase();
        const map = { js: 'Javascript', ts: 'TypeScript', py: 'Python', html: 'HTML', htm: 'HTML', css: 'CSS',
            java: 'Java', c: 'C', cpp: 'C++', cs: 'C#', go: 'Go', rs: 'Rust', rb: 'Ruby', php: 'PHP',
            lua: 'Lua', sh: 'Bash', bash: 'Bash', r: 'R', swift: 'Swift', kt: 'Kotlin', sql: 'SQL',
            groovy: 'Groovy', gvy: 'Groovy', cls: 'Apex', apex: 'Apex', trigger: 'Apex',
            gd: 'GDScript', sol: 'Solidity', nix: 'Nix', tf: 'HCL', hcl: 'HCL', tfvars: 'HCL' };
        return map[ext] || 'Javascript';
    }

    const tokenCSS = `.token-keyword{color:#FFB86C}.token-string{color:#06CF7A}.token-comment{color:#6272A4;font-style:italic}.token-number{color:#FF79C6}.token-type{color:#8BE9FD}.token-fn{color:#f1fa8c}.token-builtin{color:#4d9de0}.token-op{color:#FF5555}.token-punct{color:#7f848e}.token-attr{color:#FFB86C}.token-tag{color:#FF79C6}.token-property{color:#FFB86C}.token-decorator{color:#bd93f9;font-style:italic}`;

    const sections = Object.entries(p.files).map(([name, content]) => {
        const lang = langFromFilename(name);
        const hlHtml = JungleUI.highlightCode(lang, content || '');
        return `<div class="file-block"><div class="file-sep">--- ${name.replace(/</g,'&lt;')} ---</div><pre class="file-code">${hlHtml || ''}</pre></div>`;
    }).join('');

    const html = `<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0f0d;color:#aed9cb;font-family:'Fira Code',monospace;font-size:13.5px;padding:24px 20px;line-height:1.6;}
${tokenCSS}
.file-block{margin-bottom:32px;}
.file-sep{color:#528b74;margin-bottom:10px;font-size:13px;}
.file-code{overflow-x:auto;white-space:pre;tab-size:4;font-family:'Fira Code',monospace;font-size:13.5px;line-height:1.6;}
</style></head><body>${sections}</body></html>`;

    const doc = previewFrame.contentDocument || previewFrame.contentWindow.document;
    doc.open(); doc.write(html); doc.close();
    switchView('preview');
    tabPreview.classList.remove('active');
    projectTitleBtn.classList.add('active');
    terminalStatus.textContent = "PROJECT VIEW";
    terminalStatus.style.color = "#74a896";
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
    if (!p) return;
    let text, label;
    if (activeView === 'preview' && projectTitleBtn.classList.contains('active')) {
        // Whole Project view — copy all files
        text = Object.entries(p.files).map(([name, content]) =>
            `${'='.repeat(52)}\n// ${name}\n${'='.repeat(52)}\n${content || ''}`
        ).join('\n\n');
        label = `all files in ${p.name}`;
    } else {
        text = p.files[p.currentFile] || '';
        label = p.currentFile;
    }
    navigator.clipboard ? navigator.clipboard.writeText(text) : (() => {
        const ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
    })();
    JungleUI.showToast(`Copied ${label} to clipboard!`);
};
document.getElementById('select-all-code-btn').onclick = () => {
    if (activeView === 'preview' && projectTitleBtn.classList.contains('active')) {
        // Select all text inside whole project iframe
        const iwin = previewFrame.contentWindow;
        if (iwin) { iwin.focus(); iwin.document.execCommand('selectAll'); }
    } else {
        editor.focus(); editor.select(); editor.scrollTop = 0;
    }
};
document.getElementById('download-code-btn').onclick = () => {
    const p = JungleUI.getCurrentProject();
    if (!p) return;
    let text, filename;
    if (activeView === 'preview' && projectTitleBtn.classList.contains('active')) {
        text = Object.entries(p.files).map(([name, content]) =>
            `${'='.repeat(52)}\n// ${name}\n${'='.repeat(52)}\n${content || ''}`
        ).join('\n\n');
        filename = p.name.replace(/\s+/g, '_') + '_all_files.txt';
    } else {
        if (!p.currentFile) return;
        text = p.files[p.currentFile] || '';
        filename = p.currentFile;
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
    a.download = filename; a.click(); URL.revokeObjectURL(a.href);
    JungleUI.showToast(`Downloaded ${filename}`);
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
    'Zig': '⚡', 'Groovy': '🎵', 'Apex': '☁️', 'GDScript': '🎮', 'Solidity': '🪙', 'Nix': '❄️', 'HCL': '🏗️'
};
const ALL_LANGS = ["Apex","Assembly","Bash","C","C#","C++","Clojure","COBOL","D","Dart","Elixir","Erlang","F#","Fortran","GDScript","Go","Groovy","HCL","Haskell","HTML","Java","Javascript","Julia","Kotlin","Lisp","Lua","Nim","Nix","OCaml","Pascal","Perl","PHP","Prolog","Python","R","Ruby","Rust","Scala","Solidity","SQL","Swift","TypeScript","Zig"];
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
