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
let manualLanguageOverride = false;
class JungleStorage {
    static getProjects() {
        const data = localStorage.getItem('jungle_sandbox_projects');
        if (data) {
            try { return this.normalizeProjects(JSON.parse(data)); } catch(e) { return this.getDefaultProjects(); }
        }
        return this.getDefaultProjects();
    }
    static saveProjects(list) { localStorage.setItem('jungle_sandbox_projects', JSON.stringify(list)); }
    static getDefaultProjects() { return []; }
    static normalizeProjects(list) {
        if (!Array.isArray(list)) return [];
        return list.map((project, index) => {
            const files = project && project.files && typeof project.files === 'object' ? project.files : { 'index.html': '' };
            if (Object.keys(files).length === 0) files['index.html'] = '';
            const fileNames = Object.keys(files);
            const currentFile = project && files[project.currentFile] !== undefined ? project.currentFile : fileNames[0];
            const lang = (project && project.lang) || JungleIntelligence.languageFromFilename(currentFile, 'HTML');
            return {
                id: (project && project.id) || `proj_${Date.now()}_${index}`,
                name: (project && project.name) || `Project ${index + 1}`,
                files,
                currentFile,
                lang
            };
        });
    }
}
class JungleIntelligence {
    static languageExtensions = {
        'HTML': '.html',
        'Javascript': '.js',
        'TypeScript': '.ts',
        'Python': '.py',
        'C++': '.cpp',
        'C': '.c',
        'Java': '.java',
        'C#': '.cs',
        'Ruby': '.rb',
        'Go': '.go',
        'Rust': '.rs',
        'PHP': '.php',
        'Swift': '.swift',
        'Kotlin': '.kt',
        'Scala': '.scala',
        'R': '.r',
        'Perl': '.pl',
        'Haskell': '.hs',
        'Julia': '.jl',
        'Lua': '.lua',
        'Clojure': '.clj',
        'Elixir': '.ex',
        'Erlang': '.erl',
        'OCaml': '.ml',
        'F#': '.fs',
        'Dart': '.dart',
        'Bash': '.sh',
        'Fortran': '.f90',
        'COBOL': '.cob',
        'D': '.d',
        'Zig': '.zig',
        'Nim': '.nim',
        'Assembly': '.asm',
        'Lisp': '.lisp',
        'Prolog': '.pl',
        'Pascal': '.pas'
    };
    static extensionLanguages = {
        '.html': 'HTML',
        '.htm': 'HTML',
        '.js': 'Javascript',
        '.mjs': 'Javascript',
        '.cjs': 'Javascript',
        '.ts': 'TypeScript',
        '.py': 'Python',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.c': 'C',
        '.java': 'Java',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.pl': 'Perl',
        '.hs': 'Haskell',
        '.jl': 'Julia',
        '.lua': 'Lua',
        '.clj': 'Clojure',
        '.ex': 'Elixir',
        '.erl': 'Erlang',
        '.ml': 'OCaml',
        '.fs': 'F#',
        '.dart': 'Dart',
        '.sh': 'Bash',
        '.bash': 'Bash',
        '.f90': 'Fortran',
        '.cob': 'COBOL',
        '.d': 'D',
        '.zig': 'Zig',
        '.nim': 'Nim',
        '.asm': 'Assembly',
        '.s': 'Assembly',
        '.lisp': 'Lisp',
        '.pas': 'Pascal'
    };
    static getExtension(name) {
        const match = String(name || '').toLowerCase().match(/(\.[a-z0-9+#]+)$/);
        return match ? match[1] : "";
    }
    static getDefaultExtension(lang) {
        return this.languageExtensions[lang] || '.txt';
    }
    static languageFromFilename(filename, fallback = 'Javascript') {
        return this.extensionLanguages[this.getExtension(filename)] || fallback;
    }
    static sanitizeFileName(input, lang = 'Javascript', existingFiles = {}) {
        let name = String(input || '').trim().replace(/[\\/:*?"<>|]+/g, '-').replace(/\s+/g, '-');
        name = name.replace(/^-+|-+$/g, '');
        if (!name) name = 'main';
        if (!this.getExtension(name)) name += this.getDefaultExtension(lang);
        const base = name.replace(/(\.[^.]+)$/, '');
        const ext = this.getExtension(name);
        let candidate = name;
        let counter = 2;
        while (Object.prototype.hasOwnProperty.call(existingFiles, candidate)) {
            candidate = `${base}-${counter}${ext}`;
            counter++;
        }
        return candidate;
    }
    static guessProjectLanguage(name) {
        const text = String(name || '').toLowerCase();
        if (/python|py|data|math|ai|ml/.test(text)) return 'Python';
        if (/type|ts|typescript/.test(text)) return 'TypeScript';
        if (/html|web|site|page|frontend|browser/.test(text)) return 'HTML';
        if (/java\b|android/.test(text)) return 'Java';
        if (/c\+\+|cpp|game|engine/.test(text)) return 'C++';
        if (/\bc\b|clang/.test(text)) return 'C';
        if (/go|golang/.test(text)) return 'Go';
        if (/rust|rs/.test(text)) return 'Rust';
        return 'HTML';
    }
    static createStarterProject(id, name) {
        const lang = this.guessProjectLanguage(name);
        const defaultFile = JungleIntelligence.getDefaultExtension(lang)
            ? `main${JungleIntelligence.getDefaultExtension(lang)}`
            : (lang === 'HTML' ? 'index.html' : 'main.txt');
        return { id, name, files: { [defaultFile]: '' }, currentFile: defaultFile, lang };
    }
    static renameFileForLanguage(filename, lang, files) {
        const desiredExt = this.getDefaultExtension(lang);
        if (!desiredExt || filename.toLowerCase().endsWith(desiredExt)) return filename;
        const next = filename.replace(/(\.[^.]+)?$/, desiredExt);
        if (!Object.prototype.hasOwnProperty.call(files, next)) return next;
        return filename;
    }
    static injectProjectAssetsIntoHtml(html, files) {
        let output = html;
        Object.keys(files).forEach(filename => {
            const lower = filename.toLowerCase();
            if (lower.endsWith('.css')) {
                const linkPattern = new RegExp(`<link[^>]+href=["']${this.escapeRegExp(filename)}["'][^>]*>`, 'i');
                output = output.replace(linkPattern, `<style data-jungle-file="${filename}">\n${files[filename]}\n</style>`);
            } else if (lower.endsWith('.js')) {
                const scriptPattern = new RegExp(`<script[^>]+src=["']${this.escapeRegExp(filename)}["'][^>]*>\\s*<\\/script>`, 'i');
                output = output.replace(scriptPattern, `<script data-jungle-file="${filename}">\n${files[filename]}\n<\\/script>`);
            }
        });
        return output;
    }
    static findMissingHtmlAssets(html, files) {
        const missing = [];
        const assetRegex = /<(script|link)[^>]+(?:src|href)=["']([^"']+)["'][^>]*>/gi;
        let match;
        while ((match = assetRegex.exec(html)) !== null) {
            const assetPath = match[2];
            if (/^(https?:)?\/\//i.test(assetPath) || assetPath.startsWith('data:') || assetPath.startsWith('#')) continue;
            const cleanPath = assetPath.replace(/^\.\//, '').split(/[?#]/)[0];
            if (!Object.prototype.hasOwnProperty.call(files, cleanPath)) {
                const line = html.slice(0, match.index).split('\n').length;
                missing.push({ file: cleanPath, line });
            }
        }
        return missing;
    }
    static escapeRegExp(value) {
        return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}
// --- Smart Code Analysis and Error Diagnostic Modules ---
class JungleScanner {
    static scan(lang, code) {
        const lines = code.split('\n');
        const issues = [
            ...this.scanDelimiters(lines),
            ...this.scanLanguagePatterns(lang, lines)
        ];
        if (lang === 'HTML') issues.push(...this.scanHtmlTags(lines));
        if (lang === 'Python') issues.push(...this.scanPythonIndentation(lines));
        const order = { error: 0, warning: 1, info: 2 };
        issues.sort((a, b) => (order[a.severity] ?? 1) - (order[b.severity] ?? 1) || a.line - b.line);
        return issues;
    }
    static scanPythonIndentation(lines) {
        const issues = [];
        const indentStack = [0];
        let prevIndent = 0;
        let expectIndent = false;
        for (let i = 0; i < lines.length; i++) {
            const raw = lines[i];
            const trimmed = raw.trim();
            if (!trimmed || trimmed.startsWith('#')) continue;
            const indent = raw.match(/^(\s*)/)[1].length;
            const hasTabs = raw.match(/^\t+/);
            const hasSpaces = raw.match(/^ +/);
            if (hasTabs && hasSpaces) {
                issues.push(this.makeIssue(i + 1, "Mixed tabs and spaces for indentation.", "Use only spaces (PEP 8 recommends 4 spaces per level).", "Python indentation", 1, "error"));
            }
            if (expectIndent && indent <= prevIndent) {
                issues.push(this.makeIssue(i + 1, "Expected an indented block after ':'.", "Indent the next line with 4 spaces to begin the block body.", "Python indentation", 1, "error"));
            }
            expectIndent = /:\s*(#.*)?$/.test(trimmed) && !/^#/.test(trimmed);
            prevIndent = indent;
        }
        return issues;
    }
    static makeIssue(line, msg, hint = "", kind = "Static analysis", column = null, severity = "error") {
        return { line, msg, hint, kind, column, severity };
    }
    static scanDelimiters(lines) {
        const errors = [];
        const stack = [];
        const bracketPairs = { '(': ')', '[': ']', '{': '}' };
        const matchingPairs = { ')': '(', ']': '[', '}': '{' };
        let inBlockComment = false;
        let inString = null;
        let blockCommentStart = null;
        let stringStart = null;
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNum = i + 1;
            for (let j = 0; j < line.length; j++) {
                const char = line[j];
                const next = line[j + 1];
                const prev = line[j - 1];
                if (inBlockComment) {
                    if (char === '*' && next === '/') { inBlockComment = false; j++; }
                    continue;
                }
                if (inString) {
                    if (char === inString && prev !== '\\') inString = null;
                    continue;
                }
                if (char === '/' && next === '/') break;
                if (char === '/' && next === '*') { inBlockComment = true; blockCommentStart = { line: lineNum, column: j + 1 }; j++; continue; }
                if ((char === '"' || char === "'") && line.slice(j, j + 3) === char.repeat(3)) { j += 2; continue; }
                if (char === '"' || char === "'" || char === '`') { inString = char; stringStart = { line: lineNum, column: j + 1 }; continue; }
                if (bracketPairs[char]) {
                    stack.push({ char, line: lineNum, column: j + 1 });
                } else if (matchingPairs[char]) {
                    if (stack.length === 0) {
                        errors.push(this.makeIssue(lineNum, `Mismatched closing bracket '${char}' without matching opener.`, `Remove this '${char}' or add the matching '${matchingPairs[char]}' before it.`, "Delimiter check", j + 1));
                    } else {
                        const last = stack.pop();
                        if (last.char !== matchingPairs[char]) {
                            errors.push(this.makeIssue(lineNum, `Mismatched closing bracket '${char}' - expected '${bracketPairs[last.char]}' for '${last.char}' from line ${last.line}.`, `Close '${last.char}' with '${bracketPairs[last.char]}' before using '${char}'.`, "Delimiter check", j + 1));
                        }
                    }
                }
            }
            if (inString && inString !== '`' && !line.trimEnd().endsWith('\\')) {
                errors.push(this.makeIssue(stringStart.line, `Unclosed string literal starting with ${inString}.`, `Add a closing ${inString} before the end of the line.`, "String check", stringStart.column));
                inString = null;
                stringStart = null;
            }
        }
        if (inBlockComment && blockCommentStart) {
            errors.push(this.makeIssue(blockCommentStart.line, "Unclosed block comment detected.", "Add */ to close this block comment.", "Comment check", blockCommentStart.column));
        }
        if (inString && stringStart) {
            errors.push(this.makeIssue(stringStart.line, `Unclosed string literal starting with ${inString}.`, `Add a closing ${inString}.`, "String check", stringStart.column));
        }
        while (stack.length > 0) {
            const unclosed = stack.pop();
            errors.push(this.makeIssue(unclosed.line, `Unclosed bracket or delimiter '${unclosed.char}' detected.`, `Add '${bracketPairs[unclosed.char]}' to close the block opened here.`, "Delimiter check", unclosed.column));
        }
        return errors;
    }
    static scanHtmlTags(lines) {
        const errors = [];
        const stack = [];
        const voidTags = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
        const tagRegex = /<!--[\s\S]*?-->|<!doctype[^>]*>|<\/?([a-zA-Z0-9:-]+)(?:\s[^>]*)?>/gi;
        const code = lines.join('\n');
        let match;
        while ((match = tagRegex.exec(code)) !== null) {
            const raw = match[0];
            const tagName = match[1] ? match[1].toLowerCase() : null;
            if (!tagName || raw.startsWith('<!--') || raw.toLowerCase().startsWith('<!doctype')) continue;
            const before = code.slice(0, match.index);
            const line = before.split('\n').length;
            const column = match.index - before.lastIndexOf('\n');
            const isClosing = raw.startsWith('</');
            const isSelfClosing = raw.endsWith('/>') || voidTags.has(tagName);
            if (isClosing) {
                const last = stack.pop();
                if (!last) {
                    errors.push(this.makeIssue(line, `Closing tag </${tagName}> has no matching opening tag.`, `Remove </${tagName}> or add <${tagName}> before it.`, "HTML structure", column));
                } else if (last.tag !== tagName) {
                    errors.push(this.makeIssue(line, `Closing tag </${tagName}> does not match <${last.tag}> from line ${last.line}.`, `Change this to </${last.tag}> or close <${last.tag}> before </${tagName}>.`, "HTML structure", column));
                }
            } else if (!isSelfClosing) {
                stack.push({ tag: tagName, line, column });
            }
        }
        while (stack.length > 0) {
            const unclosed = stack.pop();
            errors.push(this.makeIssue(unclosed.line, `Unclosed HTML tag <${unclosed.tag}> detected.`, `Add </${unclosed.tag}> after this element's content.`, "HTML structure", unclosed.column));
        }
        return errors;
    }
    static scanLanguagePatterns(lang, lines) {
        const issues = [];
        const fullCode = lines.join('\n');
        const e = (ln, msg, hint, kind, sev = "error") => issues.push(this.makeIssue(ln, msg, hint, kind, null, sev));
        lines.forEach((line, idx) => {
            const lineNum = idx + 1;
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('#')) return;
            if (lang === 'Python') {
                if (/^(if|elif|else|for|while|def|class|try|except|finally|with)\b/.test(trimmed) && !trimmed.endsWith(':') && !trimmed.endsWith('\\') && !trimmed.includes('#')) {
                    e(lineNum, "Python block statement is missing a trailing colon.", "Add ':' at the end of the line.", "Python syntax");
                }
                if (/^print\s+[^(\s]/.test(trimmed)) {
                    e(lineNum, "print statement is missing parentheses (Python 3).", "Use print(...) with parentheses.", "Python syntax");
                }
                if (/\bxrange\s*\(/.test(trimmed)) {
                    e(lineNum, "'xrange' does not exist in Python 3.", "Replace xrange(...) with range(...).", "Python syntax");
                }
                if (/\b===/.test(trimmed)) {
                    e(lineNum, "Python does not use '===' for comparison.", "Use '==' for equality in Python.", "Language mismatch");
                }
                if (/\b(console\.log|let\s+\w+\s*=|const\s+\w+\s*=|var\s+\w+\s*=)\b/.test(trimmed)) {
                    e(lineNum, "This looks like JavaScript syntax inside a Python file.", "Switch to JavaScript or rewrite using Python syntax.", "Language mismatch");
                }
                if (/^\s*def\s+\w+\s*\([^)]*\)\s*$/.test(line)) {
                    e(lineNum, "Python function definition is missing a colon.", "Add ':' after the closing parenthesis.", "Python syntax");
                }
                if (/^except\s+\w+\s*,\s*\w+/.test(trimmed)) {
                    e(lineNum, "Python 2 'except X, e:' syntax is not valid in Python 3.", "Use 'except X as e:' instead.", "Python syntax");
                }
                if (/\bexec\s+["']/.test(trimmed)) {
                    e(lineNum, "'exec' is a function in Python 3, not a statement.", "Use exec(...) with parentheses.", "Python syntax");
                }
                if (/[=+\-*/%&|]$/.test(trimmed) && !/\\$/.test(trimmed)) {
                    e(lineNum, "Line ends with an operator — expression appears incomplete.", "Finish the expression or use a backslash to continue on the next line.", "Python syntax", "warning");
                }
                if (/\beval\s*\(/.test(trimmed)) {
                    e(lineNum, "eval() can execute arbitrary code and is a security risk.", "Avoid eval(); parse data explicitly instead.", "Python security", "warning");
                }
                if (/\btype\s*\(\s*\w+\s*\)\s*==/.test(trimmed)) {
                    e(lineNum, "Comparing types with type() == is fragile.", "Use isinstance(obj, Type) for type checking.", "Python style", "info");
                }
            } else if (lang === 'Javascript' || lang === 'TypeScript') {
                const condMatch = trimmed.match(/\b(if|while)\s*\((.*)\)/);
                if (condMatch && /(^|[^=!<>])=([^=>]|$)/.test(condMatch[2])) {
                    e(lineNum, "Possible assignment '=' inside a condition — did you mean '==='?", "Use '===' for comparison, or wrap '(x = val)' in extra parens if intentional.", "JavaScript logic", "warning");
                }
                if (/\b(const|let|var)\s+[A-Za-z_$][\w$]*\s*=$/.test(trimmed)) {
                    e(lineNum, "Variable declaration is missing a value after '='.", "Add the assigned value or remove the '='.", "JavaScript syntax");
                }
                if (/^\s*(if|while|for)\s+[^(\s]/.test(line)) {
                    e(lineNum, "Control statement condition must be wrapped in parentheses.", "Add ( ) around the condition.", "JavaScript syntax");
                }
                if (/^\s*(def|elif)\b/.test(line)) {
                    e(lineNum, "This looks like Python syntax inside a JavaScript file.", "Switch to Python or rewrite using JavaScript syntax.", "Language mismatch");
                }
                if (/\bawait\b/.test(trimmed) && !/\basync\b/.test(fullCode.slice(0, fullCode.indexOf(trimmed)).slice(-600))) {
                    e(lineNum, "'await' used outside an async function.", "Mark the enclosing function with 'async'.", "JavaScript async", "warning");
                }
                if (/(?<![=!<>])={1}(?![=>])/.test(trimmed.replace(/"[^"]*"|'[^']*'|`[^`]*`/g, '')) && /==[^=]/.test(trimmed)) {
                    e(lineNum, "Loose equality '==' can cause unexpected type coercion.", "Prefer '===' for strict comparison.", "JavaScript logic", "warning");
                }
                if (/\bvar\b/.test(trimmed)) {
                    e(lineNum, "'var' is function-scoped and hoisted — can cause subtle bugs.", "Use 'const' or 'let' instead.", "JavaScript style", "warning");
                }
                if (/\bdocument\.write\s*\(/.test(trimmed)) {
                    e(lineNum, "document.write() can erase the whole page when called after load.", "Use DOM methods like appendChild or innerHTML instead.", "JavaScript security", "warning");
                }
                if (/\beval\s*\(/.test(trimmed)) {
                    e(lineNum, "eval() executes arbitrary code and is a security risk.", "Find a safer alternative — JSON.parse, Function constructor, or a proper parser.", "JavaScript security", "warning");
                }
                if (/\bnew\s+Array\s*\(\d+\)/.test(trimmed)) {
                    e(lineNum, "new Array(n) creates a sparse array, not n copies of a value.", "Use Array.from({length: n}, () => val) or Array(n).fill(val) for filled arrays.", "JavaScript style", "info");
                }
                if (lang === 'TypeScript' && /\binterface\s+[A-Za-z_$][\w$]*\s*$/.test(trimmed)) {
                    e(lineNum, "TypeScript interface declaration is missing a body.", "Add { ... } after the interface name.", "TypeScript syntax");
                }
                if (lang === 'TypeScript' && /:\s*any\b/.test(trimmed)) {
                    e(lineNum, "Type 'any' disables type checking for this value.", "Replace 'any' with a specific type.", "TypeScript style", "warning");
                }
                if (lang === 'TypeScript' && /\bas\s+any\b/.test(trimmed)) {
                    e(lineNum, "'as any' type assertion bypasses TypeScript safety.", "Use a more specific type assertion or narrow the type properly.", "TypeScript style", "warning");
                }
            } else if (lang === 'Java') {
                if (/public\s+class\s+[A-Za-z_]\w*/.test(trimmed) && !/[{;]/.test(trimmed)) {
                    e(lineNum, "Java class declaration is missing an opening brace.", "Add '{' after the class name.", "Java syntax");
                }
                if (/System\.out\.print(?:ln)?\s+["']/.test(trimmed)) {
                    e(lineNum, "Java print call is missing parentheses.", "Use System.out.println(...).", "Java syntax");
                }
                if (/\bString\s+\w+\s*==\s*["']/.test(trimmed) || /["']\s*==\s*\w+/.test(trimmed)) {
                    e(lineNum, "String comparison with '==' compares references, not content.", "Use .equals() or .equalsIgnoreCase() to compare String values.", "Java logic", "warning");
                }
                if (/\bcatch\s*\(\s*Exception\s+\w+\s*\)/.test(trimmed)) {
                    e(lineNum, "Catching 'Exception' is too broad and hides real errors.", "Catch the specific exception type your code can throw.", "Java style", "info");
                }
                if (/\bnew\s+\w+\s*\(\s*\)\s*$/.test(trimmed) && !/^\s*(return|=)/.test(trimmed)) {
                    e(lineNum, "Object created with 'new' but result is not used.", "Assign the object to a variable or remove the statement.", "Java logic", "warning");
                }
            } else if (lang === 'C++' || lang === 'C') {
                if (/^\s*#include\s+[A-Za-z0-9_./]+\s*$/.test(line) && !/</.test(line) && !/"/.test(line)) {
                    e(lineNum, "Include directive is missing angle brackets or quotes.", "Use #include <header> for system headers or #include \"file.h\" for local files.", "C/C++ syntax");
                }
                if (/\b(int|float|double|char|bool|long|short|void)\s+\w+\s*\([^)]*\)\s*$/.test(trimmed)) {
                    e(lineNum, "Function declaration or definition is missing ';' or '{'.", "Add ';' for a prototype or '{...}' for a function body.", "C/C++ syntax");
                }
                if (/\bscanf\s*\(\s*["'][^"']*["']\s*,\s*[^&]/.test(trimmed)) {
                    e(lineNum, "scanf argument may be missing '&' address-of operator.", "Pass the address of the variable: scanf(\"%d\", &var).", "C/C++ syntax");
                }
                if (/\bmalloc\s*\(/.test(trimmed) && !/\bfree\s*\(/.test(fullCode)) {
                    e(lineNum, "malloc() called but no matching free() found in the file.", "Always free() every malloc() allocation to prevent memory leaks.", "C/C++ memory", "warning");
                }
                if (lang === 'C++' && /\bgets\s*\(/.test(trimmed)) {
                    e(lineNum, "gets() is unsafe and removed in C11.", "Use fgets(buf, size, stdin) instead.", "C/C++ security", "warning");
                }
                if (lang === 'C++' && /\bnew\b/.test(trimmed) && !/\bdelete\b/.test(fullCode)) {
                    e(lineNum, "'new' used but no 'delete' found — possible memory leak.", "Match every 'new' with a 'delete' or use smart pointers (unique_ptr).", "C++ memory", "warning");
                }
            } else if (lang === 'Go') {
                if (/^\s*func\s+\w+\s*\([^)]*$/.test(line)) {
                    e(lineNum, "Go function signature appears incomplete.", "Close the parameter list with ')' and add the opening brace.", "Go syntax");
                }
                if (/fmt\.Print(?:ln|f)?\s+["']/.test(trimmed)) {
                    e(lineNum, "Go print call is missing parentheses.", "Use fmt.Println(...).", "Go syntax");
                }
                if (/\b:=\b/.test(trimmed) && /^\s*(if|for|switch)\b/.test(line)) {
                    e(lineNum, "Variable declared with ':=' inside a control statement is block-scoped.", "Declare the variable before the block with 'var' if you need it outside.", "Go scope", "warning");
                }
                if (/\bfmt\./.test(fullCode) && !/\bfmt\b/.test((fullCode.match(/import\s*\(([^)]*)\)/) || ['', ''])[1])) {
                    e(lineNum, "fmt package may not be imported.", "Add \"fmt\" to your import block.", "Go imports", "warning");
                }
                if (/\berr\b/.test(trimmed) && /,\s*err\s*:=/.test(trimmed) && !/if\s+err/.test(lines.slice(idx + 1, idx + 3).join(' '))) {
                    e(lineNum, "Error return value 'err' may not be checked.", "Add 'if err != nil { ... }' after this call.", "Go error handling", "warning");
                }
            } else if (lang === 'Rust') {
                if (/\bprintln\s*\(/.test(trimmed) && !/\bprintln!\s*\(/.test(trimmed)) {
                    e(lineNum, "Rust macros require '!' — use println!(...) not println(...).", "Add '!' after println.", "Rust syntax");
                }
                if (/\bpanic\s*\(/.test(trimmed) && !/\bpanic!\s*\(/.test(trimmed)) {
                    e(lineNum, "panic is a macro in Rust — use panic!(...).", "Add '!' after panic.", "Rust syntax");
                }
                if (/\bfn\s+\w+\s*\([^)]*\)\s*$/.test(trimmed)) {
                    e(lineNum, "Rust function is missing a body.", "Add { ... } after the function signature.", "Rust syntax");
                }
                if (/\bunwrap\s*\(\s*\)/.test(trimmed)) {
                    e(lineNum, "unwrap() will panic if the value is None or Err.", "Use match, if let, or unwrap_or_else() to handle errors safely.", "Rust error handling", "warning");
                }
                if (/\bclone\s*\(\s*\)/.test(trimmed)) {
                    e(lineNum, "Calling clone() — make sure this is necessary and not avoidable with borrowing.", "Consider passing a reference (&val) instead of cloning if ownership isn't required.", "Rust performance", "info");
                }
            } else if (lang === 'PHP') {
                if (/^\s*[A-Za-z_]\w*\s*=/.test(line) && !/^\s*\$/.test(line) && !/^\s*(if|else|for|while|foreach|function|class|return|echo|namespace|use)\b/.test(line)) {
                    e(lineNum, "PHP variables must start with '$'.", "Change 'name' to '$name'.", "PHP syntax");
                }
                if (!/;\s*$/.test(trimmed) && /^\s*(echo|print|return|\$\w+\s*=)/.test(line)) {
                    e(lineNum, "PHP statement may be missing a semicolon.", "Add ';' at the end of the line.", "PHP syntax");
                }
                if (/\bmysql_/.test(trimmed)) {
                    e(lineNum, "mysql_*() functions are removed in PHP 7+.", "Use mysqli_*() or PDO instead.", "PHP syntax");
                }
                if (/\beval\s*\(/.test(trimmed)) {
                    e(lineNum, "eval() is dangerous in PHP and can lead to remote code execution.", "Avoid eval(); use safer alternatives.", "PHP security", "warning");
                }
            } else if (lang === 'Ruby') {
                if (/\bdef\s+\w+/.test(trimmed) && !lines.slice(idx, idx + 30).some(l => /^\s*end\b/.test(l))) {
                    e(lineNum, "Ruby method defined with 'def' may be missing a closing 'end'.", "Add 'end' after the method body.", "Ruby syntax");
                }
                if (/\bputs\s*\(/.test(trimmed)) {
                    e(lineNum, "'puts(...)' with parentheses is valid but 'puts ...' is idiomatic Ruby.", "Drop the parentheses: puts value.", "Ruby style", "info");
                }
                if (/\brescue\s*$/.test(trimmed)) {
                    e(lineNum, "Bare 'rescue' catches all exceptions including system errors.", "Rescue a specific exception class: rescue SomeError => e.", "Ruby style", "warning");
                }
            }
        });
        return issues;
    }
    // Instant recognition from a single unmistakable token — runs before full scoring
    static earlyHint(code) {
        const hints = [
            [/<\?php/i,                                          'PHP'],
            [/<!DOCTYPE\s+html>/i,                               'HTML'],
            [/^#!\/bin\/(bash|sh)\b/m,                           'Bash'],
            [/^#!\/usr\/bin\/(perl|env\s+perl)/m,               'Perl'],
            [/^#!\/usr\/bin\/(ruby|env\s+ruby)/m,               'Ruby'],
            [/^#!\/usr\/bin\/(python3?|env\s+python3?)/m,       'Python'],
            [/\bIDENTIFICATION\s+DIVISION\b/i,                  'COBOL'],
            [/\bIMPLICIT\s+NONE\b/i,                            'Fortran'],
            [/\bPROGRAM-ID\b/i,                                  'COBOL'],
            [/const\s+std\s*=\s*@import\s*\("std"\)/,           'Zig'],
            [/@import\s*\("std"\)/,                              'Zig'],
            [/\bcomptime\b/,                                     'Zig'],
            [/section\s+\.(text|data|bss)\b/i,                  'Assembly'],
            [/\bglobal\s+_start\b/,                             'Assembly'],
            [/\bdefmodule\b/,                                    'Elixir'],
            [/\bIO\.puts\b/,                                     'Elixir'],
            [/^-module\s*\(/m,                                   'Erlang'],
            [/\bio:format\b/,                                    'Erlang'],
            [/\[<EntryPoint>\]/,                                 'F#'],
            [/\bprintfn\b/,                                      'F#'],
            [/\blet\s*\(\s*\)\s*=/,                              'OCaml'],
            [/\bPrintf\.printf\b/,                               'OCaml'],
            [/^\s*\(defn\b/m,                                    'Clojure'],
            [/^\s*\(ns\s+\w/m,                                   'Clojure'],
            [/\bputStrLn\b/,                                     'Haskell'],
            [/\bmain\s*=\s*do\b/,                               'Haskell'],
            [/\bimport\s+'package:flutter/,                      'Dart'],
            [/\bStatelessWidget\b|\bStatefulWidget\b/,           'Dart'],
            [/\battr_(reader|writer|accessor)\b/,               'Ruby'],
            [/\bdo\s*\|[\w,\s]+\|/,                             'Ruby'],
            [/@State\b|@Binding\b|@Published\b/,                'Swift'],
            [/\bguard\s+let\b/,                                  'Swift'],
            [/\bdata\s+class\s+\w+/,                            'Kotlin'],
            [/\bwhen\s*\(\w+\)\s*\{/,                           'Kotlin'],
            [/\bcase\s+class\b/,                                 'Scala'],
            [/\bobject\s+\w+\s+extends\b/,                      'Scala'],
            [/\bprintln!\s*\(/,                                  'Rust'],
            [/\blet\s+mut\b/,                                    'Rust'],
            [/\bcout\s*<</,                                      'C++'],
            [/\bstd::/,                                          'C++'],
            [/\bSystem\.out\.print/,                             'Java'],
            [/\bpublic\s+static\s+void\s+main\b/,               'Java'],
            [/\bConsole\.WriteLine\b/,                           'C#'],
            [/\busing\s+System\b/,                               'C#'],
            [/^package\s+\w+\s*$/m,                              'Go'],
            [/\bfmt\.Print(?:ln|f)?\b/,                         'Go'],
            [/\bggplot\s*\(/,                                    'R'],
            [/\bdata\.frame\s*\(/,                               'R'],
            [/\bipairs\s*\(|\bpairs\s*\(/,                      'Lua'],
            [/\bIPO\b|\bWRITE\s*\(\s*\*\s*,/i,                 'Fortran'],
            [/\bputs\b.*\bend\b/s,                               'Ruby'],
            [/\bnim\s+import\b|\becho\s+"/,                      'Nim'],
            [/\bwriteln\s*\(\s*["']/,                            'Pascal'],
            [/\bBEGIN\b[\s\S]*\bEND\b/,                         'Pascal'],
            [/^\?-\s/m,                                          'Prolog'],
            [/\?-\s*[\w]+\s*\(/,                                 'Prolog'],
            [/^\s*\(defun\b/m,                                   'Lisp'],
            [/^\s*\(format\s+t\b/m,                             'Lisp'],
            [/\b@\[[\w.]+\]/,                                    'Julia'],
            [/\busing\s+\w+(?:,\s*\w+)*\s*$/m,                  'Julia'],
        ];
        for (const [pattern, lang] of hints) {
            if (pattern.test(code)) return lang;
        }
        return null;
    }

    static detectLanguage(code) {
        if (!code || code.trim().length < 3) return null;
        const scores = {};
        const add = (lang, pts) => { scores[lang] = (scores[lang] || 0) + pts; };

        // Early hint: a single unmistakable token is enough to tentatively identify
        const hint = this.earlyHint(code);
        if (hint) add(hint, 50);

        // --- Python ---
        if (/^\s*def\s+\w+\s*\(/m.test(code)) add('Python', 20);
        if (/^\s*class\s+\w+.*:/m.test(code)) add('Python', 15);
        if (/\belif\b/.test(code)) add('Python', 20);
        if (/^\s*from\s+\w+\s+import\b/m.test(code)) add('Python', 18);
        if (/\bself\b/.test(code)) add('Python', 15);
        if (/\bNone\b/.test(code) && !/\/\//.test(code)) add('Python', 10);
        if (/\bTrue\b|\bFalse\b/.test(code) && !/\/\//.test(code)) add('Python', 8);
        if (/\blambda\b/.test(code)) add('Python', 12);
        if (/\bprint\s*\(/.test(code) && !/console\./.test(code) && !/System\.out/.test(code) && !/\bprintln\b/.test(code)) add('Python', 10);
        if (/#[^!]/.test(code) && !/\/\//.test(code)) add('Python', 5);

        // --- JavaScript ---
        if (/\bconsole\.log\b/.test(code)) add('Javascript', 22);
        if (/\bdocument\.\w+|\bwindow\.\w+/.test(code)) add('Javascript', 20);
        if (/\bmodule\.exports\b/.test(code)) add('Javascript', 22);
        if (/\brequire\s*\(['"]/.test(code)) add('Javascript', 18);
        if (/\bPromise\b|\basync\s+function\b/.test(code)) add('Javascript', 14);
        if (/\bconst\b|\blet\b/.test(code) && !/:\s*(string|number|boolean)\b/.test(code)) add('Javascript', 8);
        if (/\bfunction\s+\w+\s*\(/.test(code) && !/\bdef\b/.test(code) && !/\bfun\b/.test(code)) add('Javascript', 10);
        if (/=>\s*[{(]/.test(code)) add('Javascript', 10);
        if (/\bnull\b/.test(code) && /\bundefined\b/.test(code)) add('Javascript', 10);
        if (/\bdocument\.getElementById\b/.test(code)) add('Javascript', 22);

        // --- TypeScript ---
        if (/\binterface\s+[A-Z]/.test(code)) add('TypeScript', 28);
        if (/\btype\s+[A-Z]\w*\s*=/.test(code)) add('TypeScript', 25);
        if (/\benum\s+\w+\s*\{/.test(code)) add('TypeScript', 25);
        if (/:\s*(string|number|boolean|void|never|unknown|any)\b/.test(code)) add('TypeScript', 18);
        if (/\bReadonly<|\bPartial<|\bRequired<|\bRecord</.test(code)) add('TypeScript', 28);
        if (/\)\s*:\s*[A-Za-z][\w<>[\]| ]+\s*(=>|\{)/.test(code)) add('TypeScript', 18);
        if (/<[A-Z]\w*>/.test(code) && /\binterface\b|\btype\b/.test(code)) add('TypeScript', 12);

        // --- HTML ---
        if (/<!DOCTYPE\s+html>/i.test(code)) add('HTML', 40);
        if (/<html[\s>]/i.test(code)) add('HTML', 25);
        if (/<\/?(div|span|body|head|script|style|meta|link)\b/i.test(code)) add('HTML', 20);
        if (/<\/\w+>/.test(code) && /<\w[\w-]*[\s>]/.test(code)) add('HTML', 15);

        // --- C++ ---
        if (/#include\s*<\w+>/.test(code)) add('C++', 22);
        if (/\bstd::/.test(code)) add('C++', 25);
        if (/\bcout\s*<</.test(code)) add('C++', 28);
        if (/\btemplate\s*</.test(code)) add('C++', 28);
        if (/\bvector\s*<|\bmap\s*<|\bunordered_map\s*</.test(code)) add('C++', 22);
        if (/\bint\s+main\s*\(\s*\)/.test(code) && /#include/.test(code)) add('C++', 15);
        if (/\bdelete\s+\w+/.test(code) && /\bnew\b/.test(code)) add('C++', 15);

        // --- C ---
        if (/#include\s*<stdio\.h>/.test(code)) add('C', 30);
        if (/\bprintf\s*\(/.test(code) && !/#include\s*<iostream>/.test(code) && !/\bstd::/.test(code)) add('C', 22);
        if (/\bscanf\s*\(/.test(code)) add('C', 22);
        if (/\bmalloc\s*\(|\bcalloc\s*\(|\bfree\s*\(/.test(code)) add('C', 22);
        if (/\bint\s+main\s*\(\s*void\s*\)/.test(code)) add('C', 22);
        if (/#include\s*<string\.h>|#include\s*<stdlib\.h>/.test(code)) add('C', 15);

        // --- Java ---
        if (/\bpublic\s+static\s+void\s+main\s*\(/.test(code)) add('Java', 35);
        if (/\bSystem\.out\.print/.test(code)) add('Java', 28);
        if (/\bpublic\s+class\s+[A-Z]/.test(code)) add('Java', 22);
        if (/\bimport\s+java\./.test(code)) add('Java', 28);
        if (/@Override\b/.test(code)) add('Java', 22);
        if (/\bArrayList\b|\bHashMap\b|\bLinkedList\b/.test(code)) add('Java', 18);
        if (/\bthrows\s+\w+Exception\b/.test(code)) add('Java', 20);

        // --- C# ---
        if (/\bConsole\.Write(?:Line)?\s*\(/.test(code)) add('C#', 28);
        if (/\busing\s+System\b/.test(code)) add('C#', 28);
        if (/\bnamespace\s+\w+/.test(code)) add('C#', 22);
        if (/\bpublic\s+static\s+void\s+Main\s*\(/.test(code)) add('C#', 25);
        if (/\bList<\w+>\b|\bDictionary</.test(code)) add('C#', 18);
        if (/\bforeach\s*\(/.test(code) && /\bvar\b/.test(code)) add('C#', 15);
        if (/\[Serializable\]|\[HttpGet\]|\[ApiController\]/.test(code)) add('C#', 25);

        // --- Go ---
        if (/^package\s+\w+/m.test(code)) add('Go', 28);
        if (/\bfunc\s+main\s*\(\)/.test(code)) add('Go', 28);
        if (/\bfmt\.Print(?:ln|f)?/.test(code)) add('Go', 22);
        if (/:=/.test(code) && /^package\b/m.test(code)) add('Go', 15);
        if (/\bgoroutine\b|\bchan\b|\bselect\b/.test(code)) add('Go', 25);
        if (/\bimport\s+\(/.test(code) && /^package\b/m.test(code)) add('Go', 18);

        // --- Rust ---
        if (/\bfn\s+main\s*\(\)/.test(code)) add('Rust', 25);
        if (/\bprintln!\s*\(/.test(code)) add('Rust', 28);
        if (/\blet\s+mut\b/.test(code)) add('Rust', 22);
        if (/\bimpl\s+\w+/.test(code)) add('Rust', 20);
        if (/\bSome\(|\bNone\b|\bOk\(|\bErr\(/.test(code)) add('Rust', 15);
        if (/\buse\s+std::/.test(code)) add('Rust', 22);
        if (/\bmatch\s+\w+\s*\{/.test(code)) add('Rust', 15);
        if (/\bunwrap\s*\(\)/.test(code)) add('Rust', 12);

        // --- PHP ---
        if (/<\?php/.test(code)) add('PHP', 40);
        if (/\$[a-zA-Z_]\w*/.test(code) && /\becho\b/.test(code)) add('PHP', 22);
        if (/\bforeach\s*\(\s*\$/.test(code)) add('PHP', 22);
        if (/\barray\s*\(/.test(code) && /\$/.test(code)) add('PHP', 15);

        // --- Ruby ---
        if (/^\s*end\s*$/m.test(code)) add('Ruby', 18);
        if (/\bputs\s+/.test(code) && /^\s*end\s*$/m.test(code)) add('Ruby', 20);
        if (/\bdo\s*\|[\w,\s]+\|/.test(code)) add('Ruby', 25);
        if (/\battr_(reader|writer|accessor)\b/.test(code)) add('Ruby', 28);
        if (/=~\s*\//.test(code)) add('Ruby', 18);
        if (/\.each\s+do\b|\bmap\s*\{/.test(code)) add('Ruby', 18);

        // --- Swift ---
        if (/\bimport\s+(Foundation|UIKit|SwiftUI)\b/.test(code)) add('Swift', 35);
        if (/\bguard\s+let\b|\bif\s+let\b/.test(code)) add('Swift', 22);
        if (/@State\b|@Binding\b|@Published\b|@ObservedObject\b/.test(code)) add('Swift', 35);
        if (/\bvar\s+\w+\s*:\s*[A-Z]/.test(code) && /\bfunc\b/.test(code)) add('Swift', 18);
        if (/\bnil\b/.test(code) && /\bfunc\b/.test(code)) add('Swift', 10);

        // --- Kotlin ---
        if (/\bfun\s+main\s*\(/.test(code)) add('Kotlin', 28);
        if (/\bprintln\s*\(/.test(code) && /\bval\b|\bvar\b/.test(code)) add('Kotlin', 22);
        if (/\bdata\s+class\s+\w+/.test(code)) add('Kotlin', 28);
        if (/\bwhen\s*\(/.test(code)) add('Kotlin', 22);
        if (/\bval\s+\w+\s*:/.test(code) && /\bfun\b/.test(code)) add('Kotlin', 15);

        // --- Bash ---
        if (/^#!\/bin\/(bash|sh)/m.test(code)) add('Bash', 40);
        if (/\[\[.*\]\]/.test(code)) add('Bash', 25);
        if (/\bfi\b/.test(code) && /\bthen\b/.test(code)) add('Bash', 22);
        if (/\bdone\b/.test(code) && /\bdo\b/.test(code)) add('Bash', 20);
        if (/\$\{[^}]+\}/.test(code)) add('Bash', 12);

        // --- R ---
        if (/<-\s*\w/.test(code) && !/\bclass\b/.test(code)) add('R', 22);
        if (/\blibrary\s*\(/.test(code)) add('R', 22);
        if (/\bggplot\s*\(|\bdplyr\b|\btidyr\b/.test(code)) add('R', 28);
        if (/\bdata\.frame\s*\(/.test(code)) add('R', 22);

        // --- Lua ---
        if (/\blocal\s+\w+\s*=/.test(code) && /\bend\b/.test(code)) add('Lua', 22);
        if (/\bipairs\s*\(|\bpairs\s*\(/.test(code)) add('Lua', 25);
        if (/\bfunction\s+\w+\s*\(/.test(code) && /\bend\b/.test(code) && !/\bdef\b/.test(code)) add('Lua', 18);
        if (/--[^\n]/.test(code) && /\blocal\b/.test(code)) add('Lua', 12);

        // --- Scala ---
        if (/\bobject\s+\w+\s+extends\b/.test(code)) add('Scala', 28);
        if (/\bcase\s+class\b/.test(code)) add('Scala', 28);
        if (/\bdef\s+\w+\s*\(/.test(code) && /\bval\b/.test(code)) add('Scala', 15);
        if (/\bprintln\s*\(/.test(code) && /\bval\b/.test(code) && /\bdef\b/.test(code)) add('Scala', 15);

        // --- Haskell ---
        if (/\bmain\s*=\s*do\b/.test(code)) add('Haskell', 35);
        if (/\bputStrLn\b|\bputStr\b/.test(code)) add('Haskell', 28);
        if (/\bimport\s+Data\./.test(code)) add('Haskell', 22);
        if (/\s->\s/.test(code) && /\b(where|let|in)\b/.test(code)) add('Haskell', 18);

        // --- Dart ---
        if (/\bvoid\s+main\s*\(\s*\)/.test(code) && /\bprint\s*\(/.test(code)) add('Dart', 25);
        if (/\bimport\s+'package:flutter/.test(code)) add('Dart', 40);
        if (/\bWidget\b|\bStatefulWidget\b|\bStatelessWidget\b/.test(code)) add('Dart', 35);

        // --- Perl ---
        if (/^#!\/usr\/bin\/(perl|env\s+perl)/m.test(code)) add('Perl', 40);
        if (/\buse\s+strict\b/.test(code)) add('Perl', 22);
        if (/\buse\s+warnings\b/.test(code)) add('Perl', 18);
        if (/\bmy\s+\$\w+/.test(code)) add('Perl', 20);
        if (/\bsub\s+\w+\s*\{/.test(code)) add('Perl', 18);
        if (/\bchomp\b/.test(code)) add('Perl', 22);
        if (/\$_\b|\@_\b/.test(code)) add('Perl', 15);

        // --- Elixir ---
        if (/\bdefmodule\b/.test(code)) add('Elixir', 35);
        if (/\bIO\.puts\b/.test(code)) add('Elixir', 28);
        if (/\|>/.test(code) && /\bdef\b/.test(code)) add('Elixir', 20);
        if (/\bdef\s+\w+\s*\(/.test(code) && /\bend\b/.test(code) && /\bdo\b/.test(code)) add('Elixir', 18);

        // --- Erlang ---
        if (/^-module\s*\(/m.test(code)) add('Erlang', 40);
        if (/\bio:format\b/.test(code)) add('Erlang', 28);
        if (/^-export\s*\(/m.test(code)) add('Erlang', 25);
        if (/\bspawn\s*\(|\breceive\b/.test(code)) add('Erlang', 20);

        // --- OCaml ---
        if (/\blet\s*\(\s*\)\s*=/.test(code)) add('OCaml', 35);
        if (/\bPrintf\.printf\b/.test(code)) add('OCaml', 28);
        if (/\blet\s+rec\b/.test(code)) add('OCaml', 22);
        if (/\bmatch\b.+\bwith\b/s.test(code) && !/\bRust\b/.test(code)) add('OCaml', 18);
        if (/\bopen\s+[A-Z]\w+/.test(code)) add('OCaml', 15);

        // --- F# ---
        if (/\[<EntryPoint>\]/.test(code)) add('F#', 40);
        if (/\bprintfn\b/.test(code)) add('F#', 30);
        if (/\bopen\s+System\b/.test(code) && /\bprintfn\b/.test(code)) add('F#', 18);
        if (/\|>/.test(code) && /\blet\b/.test(code) && /\bprintfn\b/.test(code)) add('F#', 15);

        // --- Clojure ---
        if (/^\s*\(ns\s+\w/m.test(code)) add('Clojure', 35);
        if (/^\s*\(defn\b/m.test(code)) add('Clojure', 30);
        if (/^\s*\(println\b/m.test(code)) add('Clojure', 22);
        if (/^\s*\(def\s+\w/m.test(code)) add('Clojure', 18);

        // --- Julia ---
        if (/\busing\s+\w+(?:,\s*\w+)*\s*$/m.test(code)) add('Julia', 25);
        if (/\bfunction\s+\w+\s*\(/.test(code) && /\bend\b/.test(code) && /::\w+/.test(code)) add('Julia', 22);
        if (/\b@show\b|\b@time\b|\b@assert\b/.test(code)) add('Julia', 22);
        if (/::Int(?:64)?|::Float(?:64)?|::String\b/.test(code)) add('Julia', 20);
        if (/\bprintln\s*\(/.test(code) && /\busing\b/.test(code)) add('Julia', 15);

        // --- Lisp ---
        if (/^\s*\(defun\b/m.test(code)) add('Lisp', 35);
        if (/^\s*\(format\s+t\b/m.test(code)) add('Lisp', 28);
        if (/^\s*\(setq\b/m.test(code)) add('Lisp', 22);
        if (/^\s*\(let\s+\(/m.test(code)) add('Lisp', 18);

        // --- Prolog ---
        if (/^\?-\s/m.test(code)) add('Prolog', 35);
        if (/:-\s*use_module\b/.test(code)) add('Prolog', 30);
        if (/\b\w+\s*:-\s*\w+/.test(code)) add('Prolog', 22);
        if (/\bwrite\s*\(/.test(code) && /\.\s*$/m.test(code)) add('Prolog', 15);

        // --- Fortran ---
        if (/\bIMPLICIT\s+NONE\b/i.test(code)) add('Fortran', 35);
        if (/\bPROGRAM\s+\w+/i.test(code) && /\bEND\s+PROGRAM\b/i.test(code)) add('Fortran', 30);
        if (/\bWRITE\s*\(\s*\*\s*,/i.test(code)) add('Fortran', 25);
        if (/\bREAL\s*::|INTEGER\s*::|LOGICAL\s*::/i.test(code)) add('Fortran', 22);
        if (/\bSUBROUTINE\s+\w+/i.test(code)) add('Fortran', 20);

        // --- COBOL ---
        if (/\bIDENTIFICATION\s+DIVISION\b/i.test(code)) add('COBOL', 40);
        if (/\bPROGRAM-ID\b/i.test(code)) add('COBOL', 30);
        if (/\bDATA\s+DIVISION\b|\bPROCEDURE\s+DIVISION\b/i.test(code)) add('COBOL', 25);
        if (/\bDISPLAY\s+["']/.test(code)) add('COBOL', 18);
        if (/\bMOVE\b.+\bTO\b/i.test(code)) add('COBOL', 18);

        // --- Assembly ---
        if (/section\s+\.(text|data|bss)\b/i.test(code)) add('Assembly', 35);
        if (/\bglobal\s+_start\b/.test(code)) add('Assembly', 30);
        if (/\bmov\s+[a-z]{2,3}\s*,/i.test(code)) add('Assembly', 22);
        if (/\bint\s+0x80\b|\bsyscall\b/.test(code)) add('Assembly', 25);
        if (/\bpush\s+\w+|\bpop\s+\w+/.test(code) && /\bret\b/.test(code)) add('Assembly', 20);

        // --- D ---
        if (/\bimport\s+std\.stdio\b/.test(code)) add('D', 35);
        if (/\bwriteln\s*\(/.test(code)) add('D', 25);
        if (/\bimmutable\b/.test(code) && /\bauto\b/.test(code)) add('D', 20);
        if (/\bvoid\s+main\s*\(\s*\)/.test(code) && /\bwriteln\b/.test(code)) add('D', 20);

        // --- Zig ---
        if (/@import\s*\("std"\)/.test(code)) add('Zig', 40);
        if (/\bcomptime\b/.test(code)) add('Zig', 25);
        if (/\bpub\s+fn\s+main\b/.test(code)) add('Zig', 22);
        if (/\bstd\.debug\.print\b/.test(code)) add('Zig', 25);
        if (/\bconst\s+\w+\s*=\s*@import\b/.test(code)) add('Zig', 22);

        // --- Nim ---
        if (/^import\s+\w+/m.test(code) && /\becho\s+"/.test(code)) add('Nim', 30);
        if (/\bproc\s+\w+\s*\(/.test(code)) add('Nim', 25);
        if (/\becho\s+"/.test(code) && /\bvar\b/.test(code)) add('Nim', 18);
        if (/\bwhen\s+isMainModule\b/.test(code)) add('Nim', 30);

        // --- Pascal ---
        if (/\bprogram\s+\w+\s*;/i.test(code)) add('Pascal', 35);
        if (/\bbegin\b/i.test(code) && /\bend\.\s*$/im.test(code)) add('Pascal', 28);
        if (/\bwriteln\s*\(/.test(code) && /\bbegin\b/i.test(code)) add('Pascal', 22);
        if (/\bvar\b/i.test(code) && /\binteger\b|\bstring\b|\breal\b/i.test(code)) add('Pascal', 18);
        if (/\bprocedure\s+\w+/i.test(code)) add('Pascal', 18);

        // Negative scoring: penalize languages when clear contradicting signals are present
        const sub = (lang, pts) => { scores[lang] = (scores[lang] || 0) - pts; };
        if (/\bconsole\.log\b/.test(code) || /\bdocument\.\w/.test(code)) { sub('Python', 20); sub('Java', 10); sub('Go', 10); }
        if (/\bSystem\.out\.print\b/.test(code)) { sub('Javascript', 15); sub('Python', 15); sub('Go', 10); }
        if (/\bdef\s+\w+\s*\(/.test(code) && /\bself\b/.test(code)) { sub('Javascript', 10); sub('Ruby', 10); }
        if (/\belif\b/.test(code)) { sub('Javascript', 15); sub('Java', 15); sub('Go', 15); }
        if (/<\?php/.test(code)) { sub('Javascript', 20); sub('Python', 20); }
        if (/\bfn\s+main\b/.test(code) && /\blet\s+mut\b/.test(code)) { sub('Javascript', 15); sub('Go', 15); }
        if (/\bpackage\s+main\b/.test(code) && /\bfunc\b/.test(code)) { sub('Rust', 10); sub('Javascript', 10); }
        if (/\bimport\s+java\.\w/.test(code)) { sub('Kotlin', 5); sub('Scala', 5); sub('C#', 10); }
        if (/\busing\s+System\b/.test(code)) { sub('Java', 15); sub('Javascript', 10); }
        if (/\bprintln!\s*\(/.test(code)) { sub('Kotlin', 10); sub('Javascript', 10); }
        // Clamp negative scores to 0
        Object.keys(scores).forEach(k => { if (scores[k] < 0) scores[k] = 0; });

        const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
        if (sorted.length === 0) return null;
        const [topLang, topScore] = sorted[0];
        const runnerUp = sorted[1] ? sorted[1][1] : 0;

        if (topScore >= 10 && topScore - runnerUp >= 8) {
            const confidence = topScore >= 35 ? 'confirmed' : topScore >= 18 ? 'tentative' : null;
            if (!confidence) return null;
            return { lang: topLang, score: topScore, confidence, ext: JungleIntelligence.getDefaultExtension(topLang) || '.txt' };
        }
        return null;
    }
}
class JungleRunner {
    static async execute(lang, code, files) {
        try {
            const scanIssues = JungleScanner.scan(lang, code);
            const scanErrors = scanIssues.filter(i => i.severity === 'error');
            const scanWarnings = scanIssues.filter(i => i.severity !== 'error');
            if (scanErrors.length > 0) {
                const primaryError = scanErrors[0];
                switchView('terminal', false);
                terminalStatus.textContent = "FAILED TO RUN";
                terminalStatus.className = "text-rose-500 font-bold";
                const p = JungleUI.getCurrentProject();
                const errorDetails = {
                    file: (p && p.currentFile) || "main",
                    lineNo: primaryError.line,
                    column: primaryError.column,
                    errorMsg: primaryError.msg,
                    likelyCause: primaryError.kind,
                    suggestion: primaryError.hint,
                    severity: primaryError.severity,
                    additionalErrors: scanIssues.slice(1, 5)
                };
                this.printCrashAnalysis(errorDetails, "", "");
                const extra = scanIssues.length > 1 ? ` (+${scanIssues.length - 1} more)` : "";
                JungleUI.showToast(`⛔ ${scanErrors.length} error${scanErrors.length > 1 ? 's' : ''} found${extra}. Tap to inspect.`, () => {
                    switchView('terminal', false);
                    this.printCrashAnalysis(errorDetails, "", "");
                });
                return;
            }
            if (scanWarnings.length > 0) {
                const warnLines = scanWarnings.map(w => {
                    const icon = w.severity === 'info' ? 'ℹ️' : '⚠️';
                    return `${icon} Line ${w.line} [${w.kind}]: ${w.msg}`;
                }).join('\n');
                switchView('terminal', false);
                terminalViewBody.textContent = `Warnings detected (code will still run):\n\n${warnLines}\n\n${'─'.repeat(50)}\n`;
                JungleUI.showToast(`⚠️ ${scanWarnings.length} warning${scanWarnings.length > 1 ? 's' : ''} — running anyway.`, null);
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
            const pistonDirect = "https://emkc.org/api/v2/piston/execute";
            const pistonMirror = "https://piston.engineering.purdue.edu/api/v2/piston/execute";
            const endpoints = [
                { name: "EMKC Primary API Hub", url: pistonDirect },
                { name: "Purdue University Mirror", url: pistonMirror },
                { name: "CORS-Proxied EMKC (corsproxy.io)", url: `https://corsproxy.io/?${pistonDirect}` },
                { name: "CORS-Proxied Mirror (corsproxy.io)", url: `https://corsproxy.io/?${pistonMirror}` },
                { name: "CORS-Proxied EMKC (allorigins)", url: `https://api.allorigins.win/raw?url=${encodeURIComponent(pistonDirect)}`, useRaw: true },
                { name: "CORS-Proxied EMKC (cors.sh)", url: `https://cors.sh/${pistonDirect}` },
                { name: "CORS-Proxied Mirror (cors.sh)", url: `https://cors.sh/${pistonMirror}` },
            ];
            let responseReceived = false, result = null, errorReports = [];
            for (let i = 0; i < endpoints.length; i++) {
                const currentTarget = endpoints[i];
                if (i > 0) { terminalViewBody.textContent += `\n⚠️ Node [${endpoints[i-1].name}] failed or blocked. Failover: Routing to ${currentTarget.name}...`; }
                try {
                    const headers = { 'Content-Type': 'application/json' };
                    if (currentTarget.url.includes('cors.sh')) headers['x-cors-api-key'] = 'temp_' + Math.random().toString(36).slice(2);
                    const response = await fetch(currentTarget.url, { method: 'POST', headers, body: JSON.stringify(payload) });
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    result = currentTarget.useRaw ? JSON.parse(await response.text()) : await response.json();
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
                terminalViewBody.textContent = this.formatSimpleReport({
                    lineNo: "Unknown",
                    errorMsg: "all compiler endpoints unreachable",
                    likelyCause: "All API endpoints and CORS proxies were blocked by the browser's security policy or are currently offline.",
                    suggestion: "Try a different network, disable browser extensions that block requests, or check if the site is served over HTTPS."
                });
            }
        } catch (globalErr) { this.handleGlobalFailure(globalErr); }
        terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
    }
    static handleGlobalFailure(err) {
        switchView('terminal', false);
        terminalStatus.textContent = "FAILED TO RUN";
        terminalStatus.className = "text-rose-500 font-bold";
        terminalViewBody.textContent = this.formatSimpleReport({
            lineNo: "Unknown",
            errorMsg: err.message || err || "environment failure"
        });
        JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => { switchView('terminal', false); });
    }
    static parseError(stderr, stdout, lang) {
        let errorMsg = "Execution anomaly detected.", lineNo = "Unknown line", file = "main";
        let column = null, likelyCause = "", suggestion = "";
        const combined = (stderr || "") + "\n" + (stdout || "");
        const lines = combined.trim().split('\n').filter(Boolean);
        if (lang === 'Python') {
            const match = combined.match(/File\s+"([^"]+)",\s+line\s+(\d+)/i);
            if (match) { file = match[1]; lineNo = match[2]; }
            for (let i = lines.length - 1; i >= 0; i--) {
                const l = lines[i].trim();
                if (l && (l.includes('Error:') || l.includes('Exception:') || l.match(/^[a-zA-Z0-9_]+Error:/))) { errorMsg = l; break; }
            }
            if (errorMsg === "Execution anomaly detected." && lines.length > 0) { errorMsg = lines[lines.length - 1]; }
        } else if (lang === 'Javascript' || lang === 'TypeScript') {
            if (lines[0]) errorMsg = lines[0];
            const match = combined.match(/\/([^/:\s]+):(\d+):(\d+)/) || combined.match(/(?:^|\n)([^:\n]+):(\d+):(\d+)/) || combined.match(/at\s+.*:(\d+):(\d+)/);
            if (match) {
                if (match.length > 3) { file = match[1] || "main.js"; lineNo = match[2]; column = match[3]; } else { lineNo = match[1]; column = match[2]; }
            }
        } else if (lang === 'C++' || lang === 'Java') {
            const match = combined.match(/([^:\n]+):(\d+):(?:(\d+):)?\s+(?:fatal\s+)?error:\s+(.+)/i);
            if (match) { file = match[1]; lineNo = match[2]; column = match[3] || null; errorMsg = match[4]; }
            if (lang === 'Java') {
                const exception = combined.match(/Exception in thread "[^"]+"\s+([^\n]+)/i);
                const javaFrame = combined.match(/\bat\s+.*\(([^():]+):(\d+)\)/);
                if (exception) errorMsg = exception[1].trim();
                if (javaFrame) { file = javaFrame[1]; lineNo = javaFrame[2]; }
            }
        } else {
            const generic = combined.match(/([^:\n]+):(\d+):(?:(\d+):)?\s*(.+)/);
            if (generic) { file = generic[1]; lineNo = generic[2]; column = generic[3] || null; errorMsg = generic[4]; }
            else if (lines.length > 0) { errorMsg = lines[0]; }
        }
        const insight = this.explainError(errorMsg, lang, combined);
        likelyCause = insight.likelyCause;
        suggestion = insight.suggestion;
        return { errorMsg, lineNo, file, column, likelyCause, suggestion, rawOutput: combined.trim() };
    }
    static explainError(errorMsg, lang, rawOutput) {
        const text = `${errorMsg}\n${rawOutput || ""}`.toLowerCase();
        const rules = [
            { test: /unexpected end of input|unexpected eof/i, cause: "The file ends before all opened blocks or expressions are closed.", fix: "Look for unclosed braces {}, brackets [], parentheses (), or quotes at the end of the file." },
            { test: /syntaxerror|invalid syntax|unexpected token|expected/i, cause: "The parser found code that does not match the language grammar.", fix: "Check punctuation near the reported line: missing commas, colons, braces, or quotes are common causes." },
            { test: /indentationerror|expected an indented block|unexpected indent/i, cause: "Python indentation is inconsistent or a block has no body.", fix: "Align the block with spaces consistently and indent the statements under def/if/for/while." },
            { test: /nameerror|is not defined|referenceerror/i, cause: "The code uses a variable, function, or class name before it exists.", fix: "Check the spelling and make sure the value is declared before this line runs." },
            { test: /cannot read propert(?:y|ies) of (null|undefined)/i, cause: "Trying to access a property on a value that is null or undefined.", fix: "Add a null check (e.g. if (obj) { ... }) before accessing properties, or use optional chaining: obj?.prop." },
            { test: /typeerror|cannot read properties|undefined is not a function|not a function/i, cause: "A value is being used with the wrong type or before it has the expected shape.", fix: "Inspect the value on the previous line and guard against null/undefined or convert it to the expected type." },
            { test: /maximum call stack|stack overflow|recursion/i, cause: "Infinite or deeply nested recursion caused the call stack to overflow.", fix: "Make sure the recursive function has a base case that stops the recursion." },
            { test: /indexerror|rangeerror|out of range|index out of bounds/i, cause: "The code tried to access an item outside the available range.", fix: "Check the array/list length before accessing that index. Remember indexes start at 0." },
            { test: /keyerror/i, cause: "A dictionary key does not exist.", fix: "Use dict.get(key) or check 'if key in dict' before accessing it." },
            { test: /attributeerror|has no attribute/i, cause: "An object does not have the property or method being accessed.", fix: "Check the spelling of the attribute and make sure the object is the expected type." },
            { test: /zerodivision|divide by zero|division by zero/i, cause: "The program attempted to divide a number by zero.", fix: "Guard the division with a check: if (denominator !== 0) { ... }" },
            { test: /modulenotfounderror|cannot find module|package .* not found|no module named/i, cause: "A dependency or imported file is missing from the sandbox.", fix: "Add the missing file to the project or use a module available in the selected runtime." },
            { test: /permission denied|eacces/i, cause: "The runtime blocked a file or system operation.", fix: "Avoid writing to protected paths and keep file access inside the sandbox workspace." },
            { test: /time limit|timed out|timeout/i, cause: "The program ran too long, often because of an infinite loop or slow input handling.", fix: "Add a loop exit condition or reduce the amount of work done per run." },
            { test: /segmentation fault|core dumped/i, cause: "Native code accessed invalid memory.", fix: "Check pointer usage, array bounds, and object lifetimes around the reported location." },
            { test: /overflow|integer overflow/i, cause: "A numeric value exceeded the maximum allowed size.", fix: "Use a larger numeric type or add bounds checking before performing the arithmetic." },
            { test: /assertion.*failed|assertionerror/i, cause: "An assert statement in the code evaluated to false.", fix: "Check the condition being asserted and the values it compares at that point in the program." },
            { test: /unicode|encoding|decode/i, cause: "A string or file contains characters that could not be decoded with the current encoding.", fix: "Specify an encoding explicitly (e.g. open(file, encoding='utf-8')) or sanitize the input." }
        ];
        const matched = rules.find(rule => rule.test.test(text));
        if (matched) return { likelyCause: matched.cause, suggestion: matched.fix };
        if (lang === 'Python') return { likelyCause: "Python raised an exception while executing the script.", suggestion: "Read the last traceback line first, then inspect the reported source line." };
        if (lang === 'Javascript' || lang === 'TypeScript') return { likelyCause: "The JavaScript runtime stopped on an exception.", suggestion: "Check the first error line and the top stack frame that points into your file." };
        if (lang === 'C++' || lang === 'C') return { likelyCause: "The compiler or runtime rejected the native program.", suggestion: "Start with the first compiler error; later errors are often side effects." };
        if (lang === 'Java') return { likelyCause: "The Java compiler or JVM stopped because of the reported error.", suggestion: "Verify the class name, method signatures, and the first reported line." };
        return { likelyCause: "The selected runtime reported an execution error.", suggestion: "Inspect the raw output and confirm the file language matches the selected runtime." };
    }
    static getCodeFrame(file, lineNo, column = null) {
        const p = JungleUI.getCurrentProject();
        if (!p || !p.files) return "";
        const source = p.files[file] || p.files[p.currentFile];
        const lineNumber = Number(lineNo);
        if (!source || !Number.isFinite(lineNumber)) return "";
        const lines = source.split('\n');
        const start = Math.max(1, lineNumber - 2);
        const end = Math.min(lines.length, lineNumber + 2);
        const frame = [];
        for (let i = start; i <= end; i++) {
            const marker = i === lineNumber ? ">" : " ";
            frame.push(`${marker} ${String(i).padStart(4, ' ')} | ${lines[i - 1]}`);
            if (i === lineNumber && column) {
                frame.push(`       | ${" ".repeat(Math.max(0, Number(column) - 1))}^`);
            }
        }
        return frame.join('\n');
    }
    static severityIcon(sev) {
        if (sev === 'warning') return '⚠️';
        if (sev === 'info') return 'ℹ️';
        return '⛔';
    }
    static formatSimpleReport(details) {
        const lineNo = details.lineNo || "Unknown";
        const errorKind = this.getSimpleErrorKind(details.errorMsg || "");
        const message = this.simplifyErrorMessage(details.errorMsg || "unknown error");
        const icon = this.severityIcon(details.severity);
        let out = `${icon} Error on Line ${lineNo} — ${errorKind}\n   ${message}`;
        if (details.likelyCause) out += `\n\nLikely cause: ${details.likelyCause}`;
        if (details.suggestion) out += `\nSuggestion:   ${details.suggestion}`;
        return out;
    }
    static getSimpleErrorKind(message) {
        const text = String(message).toLowerCase();
        if (/indentation|expected an indented block|unexpected indent/.test(text)) return "Indentation error";
        if (/syntax|unexpected|mismatched|unclosed|expected|invalid|missing|closing tag|html tag/.test(text)) return "Syntax error";
        if (/typeerror|type error|not a function|cannot read/.test(text)) return "Type error";
        if (/attributeerror|has no attribute|undefined property/.test(text)) return "Attribute error";
        if (/referenceerror|nameerror|not defined|is undefined/.test(text)) return "Reference error";
        if (/module|import|package|no module|missing file|file not found/.test(text)) return "Import error";
        if (/valueerror|invalid literal|nan|numberformat/.test(text)) return "Value error";
        if (/indexerror|rangeerror|out of range|index out of bounds/.test(text)) return "Index error";
        if (/zerodivision|divide by zero|division by zero/.test(text)) return "Math error";
        if (/nullpointer|null pointer|nullreference/.test(text)) return "Null error";
        if (/timeout|timed out|time limit/.test(text)) return "Timeout error";
        return "Error";
    }
    static simplifyErrorMessage(message) {
        let text = String(message || "unknown error").trim();
        if (/Unexpected end of input/i.test(text)) return "unexpected end of input";
        const closingBracket = text.match(/(?:Unexpected token|unexpected|Mismatched closing bracket)\s*['"`]?([}\])])['"`]?/i);
        if (closingBracket) return `unexpected ${closingBracket[1]}`;
        const unclosed = text.match(/Unclosed bracket or delimiter\s*['"`]?([({[])['"`]?/i);
        if (unclosed) {
            const closers = { '(': ')', '[': ']', '{': '}' };
            return `missing ${closers[unclosed[1]] || unclosed[1]}`;
        }
        const expected = text.match(/expected\s+['"`]?([^'"`.,\n]+)['"`]?/i);
        if (expected) return `expected ${expected[1].trim()}`;
        const notDefined = text.match(/([A-Za-z_$][\w$]*)\s+(?:is not defined|is undefined)/i);
        if (notDefined) return `${notDefined[1]} is not defined`;
        const noModule = text.match(/(?:No module named|Cannot find module)\s+['"]?([^'"\n]+)['"]?/i);
        if (noModule) return `missing module ${noModule[1].trim()}`;
        const noAttribute = text.match(/has no attribute\s+['"]([^'"]+)['"]/i);
        if (noAttribute) return `missing attribute ${noAttribute[1]}`;
        const cannotRead = text.match(/Cannot read (?:properties|property) of (undefined|null)(?: \(reading ['"]([^'"]+)['"]\))?/i);
        if (cannotRead) return cannotRead[2] ? `cannot read ${cannotRead[2]} of ${cannotRead[1]}` : `cannot read value of ${cannotRead[1]}`;
        const invalidLiteral = text.match(/invalid literal .*?:\s*['"]([^'"]+)['"]/i);
        if (invalidLiteral) return `invalid number ${invalidLiteral[1]}`;
        text = text
            .replace(/^syntaxerror:\s*/i, "")
            .replace(/^error:\s*/i, "")
            .replace(/^typeerror:\s*/i, "")
            .replace(/^referenceerror:\s*/i, "")
            .replace(/^nameerror:\s*/i, "")
            .replace(/^valueerror:\s*/i, "")
            .replace(/^attributeerror:\s*/i, "")
            .replace(/\s+/g, " ")
            .replace(/[.。]+$/, "");
        return text || "unknown error";
    }
    static printCrashAnalysis(details, stdout, stderr) {
        let output = this.formatSimpleReport(details);
        if (details.lineNo && details.lineNo !== "Unknown") {
            const frame = this.getCodeFrame(details.file, details.lineNo, details.column);
            if (frame) output += `\n\n${frame}`;
        }
        if (details.additionalErrors && details.additionalErrors.length > 0) {
            output += `\n\n─── Additional issues ───`;
            details.additionalErrors.forEach(e => {
                const icon = this.severityIcon(e.severity);
                output += `\n${icon} Line ${e.line} [${e.kind}]: ${e.msg}`;
                if (e.hint) output += `\n      → ${e.hint}`;
            });
        }
        terminalViewBody.textContent = output;
        terminalViewBody.scrollTop = 0;
    }
}
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
                    const newProj = JungleIntelligence.createStarterProject(newId, name);
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
            li.appendChild(actions);
            fileListContainer.appendChild(li);
        });
    }
    static deleteFile(name) {
        const p = this.getCurrentProject();
        if (!p) return;
        if (Object.keys(p.files).length <= 1) {
            this.showToast("A project needs at least one file.");
            return;
        }
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
        manualLanguageOverride = false;
        p.currentFile = filename;
        currentFileLabel.textContent = filename;
        editor.value = p.files[filename] || '';
        document.querySelectorAll('#file-list li').forEach(item => {
            const cleanName = item.textContent.replace('📄 ', '').replace('🗑️', '').trim();
            if (cleanName === filename) item.classList.add('active');
            else item.classList.remove('active');
        });
        selectedLanguages = [JungleIntelligence.languageFromFilename(filename, p.lang || selectedLanguages[0])];
        p.lang = selectedLanguages[0];
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
    const isHtml = p.currentFile.endsWith('.html') || p.currentFile.endsWith('.htm');
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
projectTitleBtn.onclick = () => { switchView('editor'); };
languageBtn.onclick = (e) => { e.stopPropagation(); languageMenu.classList.toggle('show'); };
window.onclick = () => { languageMenu.classList.remove('show'); };
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
    templateToggleArrow.textContent = open ? '▼' : '▲';
};
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
        templateToggleArrow.textContent = '▲';
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
            manualLanguageOverride = true;
            currentLanguageText.textContent = `Language: ${targetLang}`;
            languageMenu.classList.remove('show');
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
};
