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
            const enc = encodeURIComponent;
            const endpoints = [
                { name: "EMKC Primary",                   url: pistonDirect },
                { name: "Purdue Mirror",                  url: pistonMirror },
                { name: "corsproxy.io → EMKC",            url: `https://corsproxy.io/?${pistonDirect}` },
                { name: "corsproxy.io → Purdue",          url: `https://corsproxy.io/?${pistonMirror}` },
                { name: "allorigins → EMKC",              url: `https://api.allorigins.win/raw?url=${enc(pistonDirect)}`, useRaw: true },
                { name: "allorigins → Purdue",            url: `https://api.allorigins.win/raw?url=${enc(pistonMirror)}`, useRaw: true },
                { name: "cors.sh → EMKC",                 url: `https://cors.sh/${pistonDirect}`, corssh: true },
                { name: "cors.sh → Purdue",               url: `https://cors.sh/${pistonMirror}`, corssh: true },
                { name: "cors-anywhere → EMKC",           url: `https://cors-anywhere.herokuapp.com/${pistonDirect}` },
                { name: "cors-anywhere → Purdue",         url: `https://cors-anywhere.herokuapp.com/${pistonMirror}` },
                { name: "crossorigin.me → EMKC",          url: `https://crossorigin.me/${pistonDirect}` },
                { name: "thingproxy → EMKC",              url: `https://thingproxy.freeboard.io/fetch/${pistonDirect}` },
                { name: "thingproxy → Purdue",            url: `https://thingproxy.freeboard.io/fetch/${pistonMirror}` },
                { name: "jsonp.afeld.me → EMKC",          url: `https://jsonp.afeld.me/?url=${enc(pistonDirect)}`, useRaw: true },
                { name: "proxy.cors.st → EMKC",           url: `https://proxy.cors.st/${pistonDirect}` },
            ];
            let responseReceived = false, result = null, errorReports = [];
            for (let i = 0; i < endpoints.length; i++) {
                const currentTarget = endpoints[i];
                if (i > 0) { terminalViewBody.textContent += `\n⚠️ Node [${endpoints[i-1].name}] failed or blocked. Failover: Routing to ${currentTarget.name}...`; }
                try {
                    const headers = { 'Content-Type': 'application/json' };
                    if (currentTarget.corssh) headers['x-cors-api-key'] = 'temp_' + Math.random().toString(36).slice(2);
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
// --- AI Code Assistant (local intent engine — no API required) ---
const aiPanel = document.getElementById('ai-panel');
const aiPanelBackdrop = document.getElementById('ai-panel-backdrop');
const aiPanelBtn = document.getElementById('ai-panel-btn');
const aiPanelClose = document.getElementById('ai-panel-close');
const aiChatHistory = document.getElementById('ai-chat-history');
const aiPromptInput = document.getElementById('ai-prompt');
const aiSendBtn = document.getElementById('ai-send-btn');
const aiIncludeCode = document.getElementById('ai-include-code');

function openAiPanel() { aiPanel.classList.add('visible'); aiPanelBackdrop.classList.add('visible'); aiPromptInput.focus(); }
function closeAiPanel() { aiPanel.classList.remove('visible'); aiPanelBackdrop.classList.remove('visible'); }
aiPanelBtn.onclick = openAiPanel;
aiPanelClose.onclick = closeAiPanel;
aiPanelBackdrop.onclick = closeAiPanel;
aiPromptInput.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); aiSendBtn.click(); } });

function addAiMsg(role, html) {
    const div = document.createElement('div');
    div.className = `ai-msg ${role}`;
    div.innerHTML = html;
    aiChatHistory.appendChild(div);
    aiChatHistory.scrollTop = aiChatHistory.scrollHeight;
    return div;
}
function escHtml(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function formatAiResponse(text) {
    const parts = text.split(/(```[\s\S]*?```)/g);
    return parts.map(part => {
        if (part.startsWith('```')) {
            const lines = part.slice(3).split('\n');
            const lang = lines[0].trim();
            const code = lines.slice(1).join('\n').replace(/```$/, '').trimEnd();
            return `<pre><code>${escHtml(code)}</code></pre><button class="ai-apply-btn" data-code="${escHtml(code)}">⬇ Apply to Editor</button>`;
        }
        return escHtml(part).replace(/\n/g, '<br>');
    }).join('');
}

// ── Local intent engine ────────────────────────────────────────────────────────
class JungleAI {
    static score(prompt, ...terms) {
        const p = prompt.toLowerCase();
        return terms.reduce((n, t) => n + (p.includes(t) ? 1 : 0), 0);
    }
    static detect(prompt) {
        const p = prompt.toLowerCase();
        const s = (...t) => this.score(p, ...t);
        const intents = [
            { id:'fix',           w: s('fix','bug','broken','error','wrong','issue','crash','not work','doesnt work','problem') },
            { id:'comments',      w: s('comment','document','explain','annotate','add comment') },
            { id:'optimize',      w: s('optim','faster','speed','performance','efficient','refactor','clean','improve','better') },
            { id:'async',         w: s('async','await','promise','asynchronous') },
            { id:'error_handle',  w: s('error handling','try catch','try/catch','handle error','exception','safe') },
            { id:'types',         w: s('type','typescript','typed','interface','annotation') },
            { id:'todo',          w: s('todo','task','checklist','to-do','to do') },
            { id:'calculator',    w: s('calculator','calc','arithmetic','math app') },
            { id:'timer',         w: s('timer','countdown','stopwatch','count down') },
            { id:'clock',         w: s('clock','time','digital clock','analog clock') },
            { id:'quiz',          w: s('quiz','trivia','question','flashcard') },
            { id:'snake',         w: s('snake','game','canvas game') },
            { id:'notes',         w: s('note','notes','notepad','memo','journal') },
            { id:'weather',       w: s('weather','forecast','temperature') },
            { id:'login',         w: s('login','signup','auth','register','form','password') },
            { id:'budget',        w: s('budget','expense','finance','money','track spend') },
            { id:'sort',          w: s('sort','bubble sort','merge sort','quick sort','insertion sort','selection sort') },
            { id:'search',        w: s('search','binary search','linear search','find element') },
            { id:'linked_list',   w: s('linked list','node','pointer') },
            { id:'stack',         w: s('stack','push','pop','lifo') },
            { id:'queue',         w: s('queue','enqueue','dequeue','fifo') },
            { id:'fibonacci',     w: s('fibonacci','fib','golden ratio') },
            { id:'factorial',     w: s('factorial','permutation') },
            { id:'prime',         w: s('prime','sieve','primes') },
            { id:'palindrome',    w: s('palindrome','reverse','mirror') },
            { id:'fetch',         w: s('fetch','http','request','api call','get request','post request','rest') },
            { id:'dark_mode',     w: s('dark mode','dark theme','light mode','theme toggle') },
            { id:'password_gen',  w: s('password','generate password','random password','passgen') },
            { id:'random',        w: s('random','dice','coin flip','lottery','pick random') },
            { id:'matrix',        w: s('matrix','2d array','grid','table') },
            { id:'file_reader',   w: s('file','read file','upload','drag drop') },
            { id:'counter',       w: s('counter','count','increment','decrement') },
            { id:'currency',      w: s('currency','convert','exchange rate','usd','eur') },
            { id:'chatui',        w: s('chat','message','bubble','chat ui') },
            { id:'canvas',        w: s('canvas','draw','drawing','paint','sketch') },
        ];
        intents.sort((a, b) => b.w - a.w);
        return intents[0].w > 0 ? intents[0].id : 'generic';
    }

    static generate(prompt, lang, currentCode) {
        const intent = this.detect(prompt);
        const p = prompt.toLowerCase();
        const hasCode = currentCode && currentCode.trim().length > 10;

        // Code-modification intents that work on existing code
        if (intent === 'fix' && hasCode) return this.applyFix(currentCode, lang);
        if (intent === 'comments' && hasCode) return this.addComments(currentCode, lang);
        if (intent === 'optimize' && hasCode) return this.applyOptimize(currentCode, lang);
        if (intent === 'async' && hasCode) return this.makeAsync(currentCode, lang);
        if (intent === 'error_handle' && hasCode) return this.addErrorHandling(currentCode, lang);
        if (intent === 'types' && hasCode) return this.addTypes(currentCode, lang);

        // Build intents — generate full programs
        const gen = this.getTemplate(intent, lang, prompt);
        if (gen) return gen;

        // Fallback: generic starter for the language
        return this.genericStarter(lang, prompt);
    }

    // ── Code-modification helpers ──────────────────────────────────────────────
    static applyFix(code, lang) {
        let fixed = code;
        let notes = [];
        if (lang === 'Javascript' || lang === 'TypeScript') {
            if (/\bvar\b/.test(fixed)) { fixed = fixed.replace(/\bvar\b/g, 'const'); notes.push('Replaced var with const'); }
            if (/==[^=]/.test(fixed)) { fixed = fixed.replace(/([^=!<>])==([^=])/g, '$1===$2'); notes.push('Changed == to ==='); }
            if (/console\.log\(.*\)\s*$/.test(fixed)) { notes.push('console.log calls kept — remove before production'); }
        }
        if (lang === 'Python') {
            if (/print\s+[^(]/.test(fixed)) { fixed = fixed.replace(/print\s+([^\n(][^\n]*)/g, 'print($1)'); notes.push('Fixed print → print()'); }
            if (/\bxrange\b/.test(fixed)) { fixed = fixed.replace(/\bxrange\b/g, 'range'); notes.push('Replaced xrange with range (Python 3)'); }
        }
        const issues = JungleScanner.scan(lang, fixed).filter(i => i.severity === 'error');
        if (issues.length === 0 && notes.length === 0) {
            return { code: fixed, note: 'No obvious bugs found in a static scan. The code looks clean — try running it to see runtime errors.' };
        }
        return { code: fixed, note: notes.length ? `Fixed: ${notes.join('; ')}.` : `${issues.length} issue(s) detected — reviewed and patched where possible.` };
    }
    static addComments(code, lang) {
        const lines = code.split('\n');
        const commented = lines.map(line => {
            const t = line.trim();
            if (!t || t.startsWith('//') || t.startsWith('#') || t.startsWith('/*')) return line;
            const indent = line.match(/^(\s*)/)[1];
            const cmt = (lang === 'Python' || lang === 'Bash' || lang === 'R' || lang === 'Ruby') ? '#' : '//';
            if (/\bfunction\b|\bdef\b|\bfn\b|\bfunc\b/.test(t)) return `${indent}${cmt} Function: ${t.match(/(?:function|def|fn|func)\s+(\w+)/)?.[1] || 'defined here'}\n${line}`;
            if (/^\s*(if|elif|else|for|while|switch)\b/.test(line)) return `${indent}${cmt} Control flow: ${t.split(/[({]/)[0].trim()}\n${line}`;
            if (/\breturn\b/.test(t)) return `${indent}${cmt} Return result\n${line}`;
            if (/\bclass\b/.test(t)) return `${indent}${cmt} Class definition\n${line}`;
            if (/\bimport\b|\brequire\b/.test(t)) return `${indent}${cmt} Dependency: ${t}\n${line}`;
            return line;
        });
        return { code: commented.join('\n'), note: 'Added inline comments explaining functions, control flow, returns, and imports.' };
    }
    static applyOptimize(code, lang) {
        let out = code;
        if (lang === 'Javascript' || lang === 'TypeScript') {
            out = out.replace(/for\s*\(let\s+(\w+)\s*=\s*0;\s*\1\s*<\s*(\w+)\.length;\s*\1\+\+\)/g, 'for (let $1 = 0, _len = $2.length; $1 < _len; $1++)');
            out = out.replace(/\.forEach\(function\s*\((\w+)\)/g, '.forEach(($1) =>');
            out = out.replace(/function\s+(\w+)\s*\(([^)]*)\)\s*\{\s*return\s+([^;{}]+);\s*\}/g, 'const $1 = ($2) => $3;');
        }
        return { code: out, note: 'Applied optimizations: cached .length in loops, converted function expressions to arrow functions where safe.' };
    }
    static makeAsync(code, lang) {
        if (lang !== 'Javascript' && lang !== 'TypeScript') return { code, note: 'Async/await conversion is only available for JavaScript and TypeScript.' };
        let out = code.replace(/function\s+(\w+)\s*\(/g, 'async function $1(');
        out = out.replace(/\.then\s*\(\s*(?:function\s*)?\(?(\w+)?\)?\s*=>\s*\{([^}]+)\}\s*\)/gs, (_, v, body) => `\nawait ${v || 'result'};\n${body.trim()}`);
        out = out.replace(/new\s+Promise\s*\([^)]+\)/g, match => `await ${match}`);
        return { code: out, note: 'Converted function declarations to async and replaced .then() chains with await where detectable. Review the output — complex promise chains may need manual adjustment.' };
    }
    static addErrorHandling(code, lang) {
        if (lang === 'Javascript' || lang === 'TypeScript') {
            const wrapped = `try {\n${code.split('\n').map(l => '  ' + l).join('\n')}\n} catch (error) {\n  console.error('Error:', error.message);\n  throw error;\n}`;
            return { code: wrapped, note: 'Wrapped the code in a try/catch block. The error is logged and re-thrown so callers can handle it too.' };
        }
        if (lang === 'Python') {
            const wrapped = `try:\n${code.split('\n').map(l => '    ' + l).join('\n')}\nexcept Exception as e:\n    print(f'Error: {e}')\n    raise`;
            return { code: wrapped, note: 'Wrapped in try/except. Catches all exceptions, prints the message, and re-raises for the caller.' };
        }
        return { code, note: `Error handling wrap is not yet supported for ${lang} — add try/catch manually.` };
    }
    static addTypes(code, lang) {
        if (lang !== 'TypeScript') return { code, note: 'Type annotations are only added for TypeScript files. Switch the language to TypeScript first.' };
        let out = code.replace(/const\s+(\w+)\s*=\s*(\d+)/g, 'const $1: number = $2');
        out = out.replace(/const\s+(\w+)\s*=\s*['"`]/g, 'const $1: string = \'');
        out = out.replace(/const\s+(\w+)\s*=\s*\[\]/g, 'const $1: unknown[] = []');
        out = out.replace(/function\s+(\w+)\s*\(([^)]*)\)/g, (_, name, params) => {
            const typed = params.split(',').map(p => p.trim() ? `${p.trim()}: unknown` : '').join(', ');
            return `function ${name}(${typed}): unknown`;
        });
        return { code: out, note: 'Added basic TypeScript type annotations to variables and function signatures. Replace unknown with specific types for better safety.' };
    }

    // ── Build templates ────────────────────────────────────────────────────────
    static getTemplate(intent, lang, prompt) {
        const T = this.templates;
        const key = `${intent}:${lang}`;
        if (T[key]) return { code: T[key], note: this.noteFor(intent, lang) };
        // Language fallbacks
        const fallbackLang = ['Javascript','Python','Java','C++','Go','Rust'].find(l => T[`${intent}:${l}`]);
        if (fallbackLang) {
            return { code: T[`${intent}:${fallbackLang}`], note: `Built in ${fallbackLang} (no template for ${lang} yet). ${this.noteFor(intent, fallbackLang)}` };
        }
        return null;
    }
    static noteFor(intent, lang) {
        const notes = {
            todo: 'Full todo app with add, complete toggle, and delete. Each task persists while the tab is open.',
            calculator: 'Fully functional calculator with keyboard support and error handling for division by zero.',
            timer: 'Countdown timer and stopwatch with start/pause/reset controls.',
            clock: 'Live digital clock updating every second with formatted 12/24-hour time.',
            quiz: 'Multi-question quiz with scoring, immediate feedback, and a results screen.',
            snake: 'Playable Snake game on an HTML5 canvas — arrow keys to move, grows on food.',
            notes: 'Notepad with add, edit, delete, and localStorage persistence.',
            login: 'Login/signup form with client-side validation and clear field error messages.',
            budget: 'Budget tracker with income/expense entries, running balance, and category totals.',
            sort: 'Sorting algorithms with step-by-step output so you can trace the logic.',
            search: 'Binary and linear search implementations with comparison counts.',
            linked_list: 'Linked list with insert, delete, search, and print operations.',
            stack: 'Stack with push, pop, peek, and isEmpty — includes usage examples.',
            queue: 'Queue with enqueue, dequeue, peek, and size — includes usage examples.',
            fibonacci: 'Fibonacci with iterative, recursive, and memoized versions + performance comparison.',
            factorial: 'Factorial with iterative and recursive versions, handles large numbers safely.',
            prime: 'Sieve of Eratosthenes to find all primes up to N — fast and classic.',
            palindrome: 'Palindrome checker that handles strings, ignoring spaces and case.',
            fetch: 'Fetch template with async/await, error handling, loading state, and JSON parsing.',
            dark_mode: 'Dark/light theme toggle saved to localStorage so it persists across refreshes.',
            password_gen: 'Secure password generator with configurable length and character sets.',
            random: 'Random utilities: dice roller, coin flip, number range picker, and list shuffler.',
            counter: 'Counter with increment, decrement, reset, and step size control.',
            canvas: 'HTML5 canvas drawing app with brush, eraser, color picker, and clear button.',
            chatui: 'Chat bubble UI with sent/received message styling and smooth scroll.',
            matrix: '2D matrix class with creation, transpose, multiply, and display.',
            currency: 'Currency converter UI with hardcoded rates (update rates as needed).',
            weather: 'Weather UI layout — plug in your API key to load live data.',
            file_reader: 'File reader that accepts drag-and-drop or click-to-upload, reads text/JSON.',
        };
        return notes[intent] || `Generated ${lang} code for your request.`;
    }

    static genericStarter(lang, prompt) {
        const starters = {
            'Javascript': `// ${prompt}\n\n(function() {\n  'use strict';\n\n  function main() {\n    console.log('Running: ${prompt}');\n    // Your logic here\n  }\n\n  main();\n})();`,
            'Python': `# ${prompt}\n\ndef main():\n    print("Running: ${prompt}")\n    # Your logic here\n\nif __name__ == "__main__":\n    main()`,
            'Java': `// ${prompt}\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Running: ${prompt}");\n        // Your logic here\n    }\n}`,
            'C++': `// ${prompt}\n#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Running: ${prompt}" << endl;\n    // Your logic here\n    return 0;\n}`,
            'Go': `// ${prompt}\npackage main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Running: ${prompt}")\n\t// Your logic here\n}`,
            'Rust': `// ${prompt}\nfn main() {\n    println!("Running: ${prompt}");\n    // Your logic here\n}`,
            'Python': `# ${prompt}\n\ndef main():\n    print("Running: ${prompt}")\n\nif __name__ == "__main__":\n    main()`,
        };
        const code = starters[lang] || starters['Javascript'];
        return { code, note: `Started a ${lang} file for "${prompt}". Fill in your logic where the comment is.` };
    }

    static templates = {
// ── Todo ──────────────────────────────────────────────────────────────────────
'todo:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Todo List</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; display: flex; justify-content: center; padding: 40px 16px; }
  .container { width: 100%; max-width: 520px; }
  h1 { font-size: 1.6rem; margin-bottom: 20px; color: #a78bfa; }
  .input-row { display: flex; gap: 8px; margin-bottom: 24px; }
  input[type=text] { flex: 1; padding: 10px 14px; border: 1px solid #374151; border-radius: 8px; background: #111827; color: #fff; font-size: 1rem; outline: none; }
  input[type=text]:focus { border-color: #7c3aed; }
  button.add { padding: 10px 18px; background: #7c3aed; border: none; border-radius: 8px; color: #fff; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
  button.add:hover { background: #6d28d9; }
  .filters { display: flex; gap: 8px; margin-bottom: 16px; }
  .filter-btn { padding: 6px 14px; border: 1px solid #374151; border-radius: 20px; background: none; color: #9ca3af; cursor: pointer; font-size: 0.85rem; transition: all 0.15s; }
  .filter-btn.active { background: #7c3aed; border-color: #7c3aed; color: #fff; }
  ul { list-style: none; display: flex; flex-direction: column; gap: 8px; }
  li { display: flex; align-items: center; gap: 10px; background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 12px 14px; transition: opacity 0.2s; }
  li.done { opacity: 0.5; }
  li.done .task-text { text-decoration: line-through; color: #6b7280; }
  .task-check { width: 18px; height: 18px; accent-color: #7c3aed; cursor: pointer; flex-shrink: 0; }
  .task-text { flex: 1; font-size: 0.95rem; word-break: break-word; }
  .del-btn { background: none; border: none; color: #ef4444; font-size: 1.1rem; cursor: pointer; padding: 2px 6px; border-radius: 4px; opacity: 0.5; transition: opacity 0.15s; }
  li:hover .del-btn { opacity: 1; }
  .stats { margin-top: 16px; font-size: 0.8rem; color: #6b7280; text-align: right; }
</style>
</head>
<body>
<div class="container">
  <h1>✅ Todo List</h1>
  <div class="input-row">
    <input type="text" id="taskInput" placeholder="Add a new task...">
    <button class="add" onclick="addTask()">Add</button>
  </div>
  <div class="filters">
    <button class="filter-btn active" onclick="setFilter('all',this)">All</button>
    <button class="filter-btn" onclick="setFilter('active',this)">Active</button>
    <button class="filter-btn" onclick="setFilter('done',this)">Done</button>
  </div>
  <ul id="taskList"></ul>
  <p class="stats" id="stats"></p>
</div>
<script>
  let tasks = JSON.parse(localStorage.getItem('jungletasks') || '[]');
  let filter = 'all';

  function save() { localStorage.setItem('jungletasks', JSON.stringify(tasks)); }

  function addTask() {
    const input = document.getElementById('taskInput');
    const text = input.value.trim();
    if (!text) return;
    tasks.unshift({ id: Date.now(), text, done: false });
    input.value = '';
    save(); render();
  }

  function toggleTask(id) {
    const t = tasks.find(t => t.id === id);
    if (t) { t.done = !t.done; save(); render(); }
  }

  function deleteTask(id) {
    tasks = tasks.filter(t => t.id !== id);
    save(); render();
  }

  function setFilter(f, btn) {
    filter = f;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    render();
  }

  function render() {
    const visible = tasks.filter(t => filter === 'all' || (filter === 'done' ? t.done : !t.done));
    const ul = document.getElementById('taskList');
    ul.innerHTML = visible.length ? visible.map(t => \`
      <li class="\${t.done ? 'done' : ''}">
        <input class="task-check" type="checkbox" \${t.done ? 'checked' : ''} onchange="toggleTask(\${t.id})">
        <span class="task-text">\${t.text.replace(/</g,'&lt;')}</span>
        <button class="del-btn" onclick="deleteTask(\${t.id})">✕</button>
      </li>\`).join('') : '<li style="color:#6b7280;padding:12px 14px">No tasks here.</li>';
    const done = tasks.filter(t => t.done).length;
    document.getElementById('stats').textContent = \`\${done}/\${tasks.length} completed\`;
  }

  document.getElementById('taskInput').addEventListener('keydown', e => { if (e.key === 'Enter') addTask(); });
  render();
<\/script>
</body>
</html>`,

// ── Calculator ─────────────────────────────────────────────────────────────────
'calculator:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Calculator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #1c1c1e; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: system-ui, sans-serif; }
  .calc { background: #2c2c2e; border-radius: 20px; padding: 20px; width: 300px; box-shadow: 0 20px 60px rgba(0,0,0,0.6); }
  .display { background: #1c1c1e; border-radius: 12px; padding: 16px 20px; text-align: right; margin-bottom: 16px; }
  .expr { color: #8e8e93; font-size: 0.9rem; height: 20px; overflow: hidden; white-space: nowrap; }
  .result { color: #fff; font-size: 2.4rem; font-weight: 300; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
  button { border: none; border-radius: 12px; padding: 18px; font-size: 1.1rem; cursor: pointer; transition: filter 0.1s; }
  button:active { filter: brightness(0.8); }
  .op { background: #ff9f0a; color: #fff; }
  .fn { background: #3a3a3c; color: #fff; }
  .zero { grid-column: span 2; text-align: left; padding-left: 26px; }
  .eq { background: #ff9f0a; color: #fff; }
  .num { background: #505050; color: #fff; }
</style>
</head>
<body>
<div class="calc">
  <div class="display">
    <div class="expr" id="expr"></div>
    <div class="result" id="result">0</div>
  </div>
  <div class="grid">
    <button class="fn" onclick="clearAll()">AC</button>
    <button class="fn" onclick="toggleSign()">+/-</button>
    <button class="fn" onclick="percent()">%</button>
    <button class="op" onclick="setOp('/')">÷</button>
    <button class="num" onclick="digit('7')">7</button>
    <button class="num" onclick="digit('8')">8</button>
    <button class="num" onclick="digit('9')">9</button>
    <button class="op" onclick="setOp('*')">×</button>
    <button class="num" onclick="digit('4')">4</button>
    <button class="num" onclick="digit('5')">5</button>
    <button class="num" onclick="digit('6')">6</button>
    <button class="op" onclick="setOp('-')">−</button>
    <button class="num" onclick="digit('1')">1</button>
    <button class="num" onclick="digit('2')">2</button>
    <button class="num" onclick="digit('3')">3</button>
    <button class="op" onclick="setOp('+')">+</button>
    <button class="num zero" onclick="digit('0')">0</button>
    <button class="num" onclick="dot()">.</button>
    <button class="eq" onclick="equals()">=</button>
  </div>
</div>
<script>
  let current = '0', prev = null, op = null, fresh = false;
  const res = document.getElementById('result');
  const expr = document.getElementById('expr');

  function update() { res.textContent = current.length > 10 ? parseFloat(current).toExponential(4) : current; }

  function digit(d) {
    if (fresh) { current = d; fresh = false; }
    else current = current === '0' ? d : current + d;
    update();
  }

  function dot() {
    if (fresh) { current = '0.'; fresh = false; }
    else if (!current.includes('.')) current += '.';
    update();
  }

  function setOp(o) {
    if (op && !fresh) equals();
    prev = current; op = o; fresh = true;
    expr.textContent = \`\${prev} \${o}\`;
  }

  function equals() {
    if (!op || prev === null) return;
    const a = parseFloat(prev), b = parseFloat(current);
    let r;
    if (op === '+') r = a + b;
    else if (op === '-') r = a - b;
    else if (op === '*') r = a * b;
    else if (op === '/') { r = b === 0 ? 'Error' : a / b; }
    expr.textContent = \`\${prev} \${op} \${current} =\`;
    current = String(r !== undefined ? (Number.isInteger(r) ? r : parseFloat(r.toFixed(10))) : 'Error');
    op = null; prev = null; fresh = true;
    update();
  }

  function clearAll() { current = '0'; prev = null; op = null; fresh = false; expr.textContent = ''; update(); }
  function toggleSign() { current = String(-parseFloat(current)); update(); }
  function percent() { current = String(parseFloat(current) / 100); update(); }

  document.addEventListener('keydown', e => {
    if ('0123456789'.includes(e.key)) digit(e.key);
    else if (e.key === '.') dot();
    else if (['+','-','*','/'].includes(e.key)) setOp(e.key);
    else if (e.key === 'Enter' || e.key === '=') equals();
    else if (e.key === 'Escape') clearAll();
    else if (e.key === 'Backspace') { current = current.length > 1 ? current.slice(0,-1) : '0'; update(); }
  });

  update();
<\/script>
</body>
</html>`,

// ── Timer ──────────────────────────────────────────────────────────────────────
'timer:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Timer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f172a; color: #e2e8f0; font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
  .card { background: #1e293b; border-radius: 24px; padding: 40px; width: 340px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
  h2 { margin-bottom: 28px; color: #94a3b8; letter-spacing: 2px; font-size: 0.85rem; text-transform: uppercase; }
  .tabs { display: flex; background: #0f172a; border-radius: 10px; padding: 4px; margin-bottom: 28px; }
  .tab { flex: 1; padding: 8px; border: none; background: none; color: #64748b; font-size: 0.85rem; cursor: pointer; border-radius: 7px; transition: all 0.15s; }
  .tab.active { background: #334155; color: #e2e8f0; }
  .display { font-size: 4rem; font-weight: 200; letter-spacing: 4px; margin: 24px 0; font-variant-numeric: tabular-nums; color: #f1f5f9; }
  .countdown-inputs { display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; }
  .countdown-inputs input { width: 64px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #e2e8f0; font-size: 1.1rem; text-align: center; padding: 8px; outline: none; }
  .controls { display: flex; gap: 10px; justify-content: center; }
  button.ctrl { padding: 12px 24px; border-radius: 12px; border: none; font-size: 0.95rem; cursor: pointer; transition: all 0.15s; }
  .start { background: #10b981; color: #fff; }
  .start:hover { background: #059669; }
  .pause { background: #f59e0b; color: #fff; }
  .reset { background: #334155; color: #e2e8f0; }
  .reset:hover { background: #475569; }
</style>
</head>
<body>
<div class="card">
  <h2>⏱ Timer</h2>
  <div class="tabs">
    <button class="tab active" onclick="setMode('stopwatch',this)">Stopwatch</button>
    <button class="tab" onclick="setMode('countdown',this)">Countdown</button>
  </div>
  <div id="countdownInputs" class="countdown-inputs" style="display:none">
    <input id="hInput" type="number" placeholder="HH" min="0" max="99" value="0">
    <input id="mInput" type="number" placeholder="MM" min="0" max="59" value="5">
    <input id="sInput" type="number" placeholder="SS" min="0" max="59" value="0">
  </div>
  <div class="display" id="display">00:00:00</div>
  <div class="controls">
    <button class="ctrl start" id="startBtn" onclick="toggleStart()">Start</button>
    <button class="ctrl reset" onclick="resetTimer()">Reset</button>
  </div>
</div>
<script>
  let mode = 'stopwatch', elapsed = 0, target = 0, interval = null, running = false;

  function setMode(m, btn) {
    mode = m; resetTimer();
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('countdownInputs').style.display = m === 'countdown' ? 'flex' : 'none';
  }

  function pad(n) { return String(Math.floor(n)).padStart(2, '0'); }

  function fmt(secs) {
    const h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60), s = secs % 60;
    return \`\${pad(h)}:\${pad(m)}:\${pad(s)}\`;
  }

  function tick() {
    if (mode === 'stopwatch') { elapsed++; document.getElementById('display').textContent = fmt(elapsed); }
    else {
      if (elapsed <= 0) { clearInterval(interval); running = false; document.getElementById('startBtn').textContent = 'Start'; document.getElementById('display').textContent = '00:00:00'; alert('⏰ Time is up!'); return; }
      elapsed--;
      document.getElementById('display').textContent = fmt(elapsed);
    }
  }

  function toggleStart() {
    if (!running) {
      if (mode === 'countdown' && elapsed === 0) {
        const h = parseInt(document.getElementById('hInput').value) || 0;
        const m = parseInt(document.getElementById('mInput').value) || 0;
        const s = parseInt(document.getElementById('sInput').value) || 0;
        elapsed = h * 3600 + m * 60 + s;
        if (!elapsed) return;
      }
      interval = setInterval(tick, 1000);
      running = true;
      document.getElementById('startBtn').textContent = 'Pause';
      document.getElementById('startBtn').className = 'ctrl pause';
    } else {
      clearInterval(interval); running = false;
      document.getElementById('startBtn').textContent = 'Resume';
      document.getElementById('startBtn').className = 'ctrl start';
    }
  }

  function resetTimer() {
    clearInterval(interval); running = false; elapsed = 0;
    document.getElementById('display').textContent = '00:00:00';
    document.getElementById('startBtn').textContent = 'Start';
    document.getElementById('startBtn').className = 'ctrl start';
  }
<\/script>
</body>
</html>`,

// ── Snake ─────────────────────────────────────────────────────────────────────
'snake:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Snake</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0f1117; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: monospace; color: #aed9cb; }
  h1 { margin-bottom: 12px; font-size: 1.4rem; letter-spacing: 3px; }
  canvas { border: 2px solid #2a3d35; border-radius: 4px; }
  #score { margin-top: 12px; font-size: 1rem; color: #528b74; }
  #msg { margin-top: 8px; font-size: 0.85rem; color: #4b5563; }
</style>
</head>
<body>
<h1>🐍 SNAKE</h1>
<canvas id="c" width="400" height="400"></canvas>
<p id="score">Score: 0</p>
<p id="msg">Press any arrow key to start</p>
<script>
  const C = document.getElementById('c'), ctx = C.getContext('2d');
  const SZ = 20, COLS = 20, ROWS = 20;
  let snake, dir, nextDir, food, score, running, loop;

  function init() {
    snake = [{x:10,y:10},{x:9,y:10},{x:8,y:10}];
    dir = {x:1,y:0}; nextDir = {x:1,y:0};
    score = 0; running = false;
    placeFood(); draw();
    document.getElementById('score').textContent = 'Score: 0';
    document.getElementById('msg').textContent = 'Press any arrow key to start';
  }

  function placeFood() {
    do { food = {x:Math.floor(Math.random()*COLS), y:Math.floor(Math.random()*ROWS)}; }
    while (snake.some(s => s.x===food.x && s.y===food.y));
  }

  function step() {
    dir = nextDir;
    const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
    if (head.x<0||head.x>=COLS||head.y<0||head.y>=ROWS||snake.some(s=>s.x===head.x&&s.y===head.y)) {
      clearInterval(loop); running = false;
      document.getElementById('msg').textContent = \`Game over! Press R to restart.\`;
      return;
    }
    snake.unshift(head);
    if (head.x===food.x && head.y===food.y) { score++; document.getElementById('score').textContent = 'Score: ' + score; placeFood(); }
    else snake.pop();
    draw();
  }

  function draw() {
    ctx.fillStyle = '#0f1117'; ctx.fillRect(0,0,400,400);
    ctx.fillStyle = '#1c2521';
    for(let x=0;x<COLS;x++) for(let y=0;y<ROWS;y++) { if((x+y)%2===0) ctx.fillRect(x*SZ,y*SZ,SZ,SZ); }
    snake.forEach((s,i) => {
      ctx.fillStyle = i===0 ? '#74a896' : '#2a6a52';
      ctx.beginPath(); ctx.roundRect(s.x*SZ+1,s.y*SZ+1,SZ-2,SZ-2,4); ctx.fill();
    });
    ctx.fillStyle = '#ef4444';
    ctx.beginPath(); ctx.arc(food.x*SZ+SZ/2,food.y*SZ+SZ/2,SZ/2-2,0,Math.PI*2); ctx.fill();
  }

  document.addEventListener('keydown', e => {
    const keys = {ArrowUp:{x:0,y:-1},ArrowDown:{x:0,y:1},ArrowLeft:{x:-1,y:0},ArrowRight:{x:1,y:0}};
    if (keys[e.key]) {
      e.preventDefault();
      const d = keys[e.key];
      if (d.x !== -dir.x || d.y !== -dir.y) nextDir = d;
      if (!running) { running = true; loop = setInterval(step, 130); document.getElementById('msg').textContent = 'Arrow keys to steer'; }
    }
    if (e.key === 'r' || e.key === 'R') { clearInterval(loop); init(); }
  });

  init();
<\/script>
</body>
</html>`,

// ── Password Generator ─────────────────────────────────────────────────────────
'password_gen:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Password Generator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f172a; color: #e2e8f0; font-family: system-ui,sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
  .card { background: #1e293b; border-radius: 20px; padding: 36px; width: 380px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
  h1 { font-size: 1.3rem; margin-bottom: 24px; color: #7c3aed; }
  .pw-box { background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 14px 16px; font-family: monospace; font-size: 1.05rem; letter-spacing: 1px; word-break: break-all; min-height: 54px; color: #a78bfa; margin-bottom: 10px; }
  .strength { height: 6px; border-radius: 3px; margin-bottom: 20px; transition: all 0.3s; }
  label { display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px; }
  input[type=range] { width: 100%; accent-color: #7c3aed; margin-bottom: 16px; }
  .checks { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 24px; }
  .checks label { flex-direction: row; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem; color: #94a3b8; justify-content: flex-start; }
  .checks input { accent-color: #7c3aed; }
  .btns { display: flex; gap: 10px; }
  button { flex: 1; padding: 12px; border: none; border-radius: 10px; font-size: 0.95rem; cursor: pointer; transition: all 0.15s; }
  .gen-btn { background: #7c3aed; color: #fff; }
  .gen-btn:hover { background: #6d28d9; }
  .copy-btn { background: #334155; color: #e2e8f0; }
  .copy-btn:hover { background: #475569; }
</style>
</head>
<body>
<div class="card">
  <h1>🔐 Password Generator</h1>
  <div class="pw-box" id="pwDisplay">Click Generate</div>
  <div class="strength" id="strength"></div>
  <label>Length: <span id="lenLabel">16</span></label>
  <input type="range" id="lenRange" min="6" max="64" value="16" oninput="document.getElementById('lenLabel').textContent=this.value">
  <div class="checks">
    <label><input type="checkbox" id="chkUpper" checked> Uppercase</label>
    <label><input type="checkbox" id="chkLower" checked> Lowercase</label>
    <label><input type="checkbox" id="chkNum" checked> Numbers</label>
    <label><input type="checkbox" id="chkSym" checked> Symbols</label>
  </div>
  <div class="btns">
    <button class="gen-btn" onclick="generate()">Generate</button>
    <button class="copy-btn" onclick="copyPw()">Copy</button>
  </div>
</div>
<script>
  const UPPER='ABCDEFGHIJKLMNOPQRSTUVWXYZ', LOWER='abcdefghijklmnopqrstuvwxyz', NUMS='0123456789', SYMS='!@#$%^&*()-_=+[]{}|;:,.<>?';
  let lastPw = '';

  function generate() {
    const len = parseInt(document.getElementById('lenRange').value);
    const sets = [];
    if (document.getElementById('chkUpper').checked) sets.push(UPPER);
    if (document.getElementById('chkLower').checked) sets.push(LOWER);
    if (document.getElementById('chkNum').checked) sets.push(NUMS);
    if (document.getElementById('chkSym').checked) sets.push(SYMS);
    if (!sets.length) { alert('Pick at least one character type.'); return; }
    const pool = sets.join('');
    const arr = new Uint32Array(len);
    crypto.getRandomValues(arr);
    // Ensure at least one char from each set
    const required = sets.map(s => s[arr[Math.floor(Math.random()*len)] % s.length]);
    let pw = required.concat(Array.from({length: len - required.length}, (_,i) => pool[arr[i+required.length] % pool.length]));
    // Shuffle
    for (let i = pw.length - 1; i > 0; i--) { const j = arr[i] % (i + 1); [pw[i], pw[j]] = [pw[j], pw[i]]; }
    lastPw = pw.join('');
    document.getElementById('pwDisplay').textContent = lastPw;
    const score = Math.min(5, sets.length + (len >= 12 ? 1 : 0) + (len >= 20 ? 1 : 0));
    const colors = ['#ef4444','#f97316','#eab308','#22c55e','#10b981','#6366f1'];
    document.getElementById('strength').style.background = colors[score];
    document.getElementById('strength').style.width = (score/5*100)+'%';
  }

  function copyPw() {
    if (!lastPw) return;
    navigator.clipboard.writeText(lastPw).then(() => {
      const btn = document.querySelector('.copy-btn');
      btn.textContent = 'Copied!'; setTimeout(() => btn.textContent = 'Copy', 1500);
    });
  }

  generate();
<\/script>
</body>
</html>`,

// ── Sort algorithms ────────────────────────────────────────────────────────────
'sort:Python': `def bubble_sort(arr):
    n = len(arr)
    arr = arr[:]
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left   = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right  = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

if __name__ == "__main__":
    import random, time
    data = [random.randint(1, 1000) for _ in range(20)]
    print("Original :", data)
    for name, fn in [("Bubble", bubble_sort), ("Merge", merge_sort), ("Quick", quick_sort)]:
        t = time.perf_counter()
        result = fn(data)
        elapsed = (time.perf_counter() - t) * 1000
        print(f"{name:6}: {result}  ({elapsed:.3f}ms)")`,

'sort:Javascript': `// Sorting algorithms with performance comparison

function bubbleSort(arr) {
  arr = [...arr];
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    let swapped = false;
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        swapped = true;
      }
    }
    if (!swapped) break;
  }
  return arr;
}

function mergeSort(arr) {
  if (arr.length <= 1) return arr;
  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));
  const result = [];
  let i = 0, j = 0;
  while (i < left.length && j < right.length) {
    result.push(left[i] <= right[j] ? left[i++] : right[j++]);
  }
  return [...result, ...left.slice(i), ...right.slice(j)];
}

function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[Math.floor(arr.length / 2)];
  return [
    ...quickSort(arr.filter(x => x < pivot)),
    ...arr.filter(x => x === pivot),
    ...quickSort(arr.filter(x => x > pivot))
  ];
}

const data = Array.from({length: 20}, () => Math.floor(Math.random() * 1000));
console.log('Original:', data.join(', '));

for (const [name, fn] of [['Bubble', bubbleSort], ['Merge', mergeSort], ['Quick', quickSort]]) {
  const t = performance.now();
  const sorted = fn(data);
  const ms = (performance.now() - t).toFixed(3);
  console.log(\`\${name.padEnd(6)}: \${sorted.join(', ')}  (\${ms}ms)\`);
}`,

// ── Fibonacci ─────────────────────────────────────────────────────────────────
'fibonacci:Python': `import time

def fib_recursive(n):
    """Simple recursive — exponential time, for demonstration only."""
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

def fib_iterative(n):
    """Iterative — O(n) time, O(1) space."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def fib_memoized(n, memo={}):
    """Memoized recursive — O(n) time, O(n) space."""
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memoized(n - 1, memo) + fib_memoized(n - 2, memo)
    return memo[n]

def fib_sequence(n):
    """Return the full Fibonacci sequence up to index n."""
    if n == 0:
        return [0]
    seq = [0, 1]
    for i in range(2, n + 1):
        seq.append(seq[-1] + seq[-2])
    return seq

if __name__ == "__main__":
    N = 30
    print(f"Fibonacci sequence (first {N+1} numbers):")
    print(fib_sequence(N))
    print()

    for label, fn in [("Iterative", fib_iterative), ("Memoized", fib_memoized)]:
        t = time.perf_counter()
        result = fn(N)
        ms = (time.perf_counter() - t) * 1000
        print(f"fib({N}) via {label}: {result}  ({ms:.4f}ms)")

    print()
    SMALL = 10
    t = time.perf_counter()
    result = fib_recursive(SMALL)
    ms = (time.perf_counter() - t) * 1000
    print(f"fib({SMALL}) via Recursive: {result}  ({ms:.4f}ms)  (slow — only safe for small N)")`,

// ── Fetch template ─────────────────────────────────────────────────────────────
'fetch:Javascript': `// Fetch utility with async/await, retry logic, and error handling

async function fetchJSON(url, options = {}, retries = 3) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, {
        headers: { 'Accept': 'application/json', ...options.headers },
        ...options
      });
      if (!response.ok) {
        throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
      }
      return await response.json();
    } catch (error) {
      if (attempt === retries) throw error;
      const delay = 2 ** attempt * 200;
      console.warn(\`Attempt \${attempt} failed. Retrying in \${delay}ms...\`);
      await new Promise(res => setTimeout(res, delay));
    }
  }
}

async function postJSON(url, data, options = {}) {
  return fetchJSON(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    ...options
  });
}

// Example: fetch public data
async function main() {
  const url = 'https://jsonplaceholder.typicode.com/posts/1';
  console.log('Fetching:', url);

  try {
    const data = await fetchJSON(url);
    console.log('Response:', data);
    console.log('Title:', data.title);
  } catch (error) {
    console.error('Request failed:', error.message);
  }
}

main();`,

// ── Dark mode ─────────────────────────────────────────────────────────────────
'dark_mode:Javascript': `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<title>Dark Mode Toggle</title>
<style>
  :root[data-theme="dark"] {
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --sub: #94a3b8; --accent: #7c3aed;
    --btn-bg: #334155; --btn-text: #e2e8f0;
  }
  :root[data-theme="light"] {
    --bg: #f8fafc; --surface: #ffffff; --border: #e2e8f0;
    --text: #0f172a; --sub: #64748b; --accent: #7c3aed;
    --btn-bg: #e2e8f0; --btn-text: #0f172a;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; transition: background 0.25s, color 0.25s, border-color 0.25s; }
  body { background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 40px; width: 360px; }
  h1 { margin-bottom: 8px; }
  p { color: var(--sub); margin-bottom: 28px; font-size: 0.9rem; }
  .toggle-row { display: flex; justify-content: space-between; align-items: center; }
  .toggle { position: relative; width: 52px; height: 28px; }
  .toggle input { display: none; }
  .slider { position: absolute; inset: 0; background: var(--btn-bg); border-radius: 14px; cursor: pointer; transition: background 0.25s; }
  .slider::before { content: ''; position: absolute; width: 22px; height: 22px; left: 3px; top: 3px; background: #fff; border-radius: 50%; transition: transform 0.25s; }
  input:checked + .slider { background: var(--accent); }
  input:checked + .slider::before { transform: translateX(24px); }
  .label { font-size: 0.9rem; color: var(--text); }
  .theme-icon { font-size: 1.6rem; text-align: center; margin-top: 24px; }
</style>
</head>
<body>
<div class="card">
  <h1>Theme Switcher</h1>
  <p>Preference saved across page refreshes.</p>
  <div class="toggle-row">
    <span class="label" id="themeLabel">Dark mode</span>
    <label class="toggle">
      <input type="checkbox" id="themeToggle" onchange="toggleTheme(this)">
      <span class="slider"></span>
    </label>
  </div>
  <div class="theme-icon" id="themeIcon">🌙</div>
</div>
<script>
  function applyTheme(dark) {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    document.getElementById('themeLabel').textContent = dark ? 'Dark mode' : 'Light mode';
    document.getElementById('themeIcon').textContent = dark ? '🌙' : '☀️';
    document.getElementById('themeToggle').checked = dark;
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }
  function toggleTheme(el) { applyTheme(el.checked); }
  const saved = localStorage.getItem('theme');
  applyTheme(saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches);
<\/script>
</body>
</html>`,

// ── Counter ──────────────────────────────────────────────────────────────────
'counter:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Counter</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #111827; color: #f9fafb; font-family: system-ui,sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
  .card { background: #1f2937; border-radius: 24px; padding: 48px 40px; text-align: center; width: 320px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
  h1 { font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; color: #6b7280; margin-bottom: 24px; }
  .count { font-size: 5rem; font-weight: 200; margin: 16px 0 32px; transition: transform 0.1s; }
  .count.bump { transform: scale(1.1); }
  .btns { display: flex; gap: 12px; justify-content: center; margin-bottom: 24px; }
  button { width: 60px; height: 60px; border: none; border-radius: 50%; font-size: 1.6rem; cursor: pointer; transition: all 0.15s; }
  .dec { background: #374151; color: #f9fafb; }
  .dec:hover { background: #ef4444; }
  .inc { background: #374151; color: #f9fafb; }
  .inc:hover { background: #10b981; }
  .rst { background: #374151; color: #6b7280; font-size: 1rem; }
  .rst:hover { background: #4b5563; color: #f9fafb; }
  .step-row { display: flex; align-items: center; gap: 10px; justify-content: center; font-size: 0.85rem; color: #6b7280; }
  .step-row input { width: 60px; background: #111827; border: 1px solid #374151; border-radius: 8px; color: #f9fafb; padding: 6px; text-align: center; font-size: 0.85rem; outline: none; }
</style>
</head>
<body>
<div class="card">
  <h1>Counter</h1>
  <div class="count" id="display">0</div>
  <div class="btns">
    <button class="dec" onclick="change(-1)">−</button>
    <button class="rst" onclick="reset()">↺</button>
    <button class="inc" onclick="change(1)">+</button>
  </div>
  <div class="step-row">Step: <input id="step" type="number" value="1" min="1"></div>
</div>
<script>
  let count = 0;
  const display = document.getElementById('display');

  function change(dir) {
    const step = Math.abs(parseInt(document.getElementById('step').value) || 1);
    count += dir * step;
    display.textContent = count;
    display.style.color = count > 0 ? '#10b981' : count < 0 ? '#ef4444' : '#f9fafb';
    display.classList.remove('bump');
    void display.offsetWidth;
    display.classList.add('bump');
  }

  function reset() { count = 0; display.textContent = 0; display.style.color = '#f9fafb'; }

  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp' || e.key === '+') change(1);
    if (e.key === 'ArrowDown' || e.key === '-') change(-1);
    if (e.key === 'r' || e.key === 'R') reset();
  });
<\/script>
</body>
</html>`,

// ── Linked List ───────────────────────────────────────────────────────────────
'linked_list:Python': `class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        """Add to the end."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def prepend(self, data):
        """Add to the front."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete(self, data):
        """Remove first occurrence of data."""
        if not self.head:
            return
        if self.head.data == data:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next

    def search(self, data):
        """Return index of first occurrence, or -1."""
        current = self.head
        idx = 0
        while current:
            if current.data == data:
                return idx
            current = current.next
            idx += 1
        return -1

    def reverse(self):
        """Reverse the list in-place."""
        prev = None
        current = self.head
        while current:
            nxt = current.next
            current.next = prev
            prev = current
            current = nxt
        self.head = prev

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def __len__(self):
        return sum(1 for _ in self.to_list())

    def __repr__(self):
        return ' -> '.join(str(x) for x in self.to_list()) or '(empty)'


if __name__ == "__main__":
    ll = LinkedList()
    for val in [10, 20, 30, 40, 50]:
        ll.append(val)
    print("List:", ll)
    ll.prepend(5)
    print("After prepend(5):", ll)
    ll.delete(30)
    print("After delete(30):", ll)
    print("Search 40:", ll.search(40))
    ll.reverse()
    print("Reversed:", ll)
    print("Length:", len(ll))`,

// ── Stack ─────────────────────────────────────────────────────────────────────
'stack:Javascript': `class Stack {
  #items = [];

  push(item) { this.#items.push(item); }
  pop() {
    if (this.isEmpty()) throw new Error('Stack underflow — cannot pop from empty stack');
    return this.#items.pop();
  }
  peek() {
    if (this.isEmpty()) throw new Error('Stack is empty');
    return this.#items[this.#items.length - 1];
  }
  isEmpty() { return this.#items.length === 0; }
  size() { return this.#items.length; }
  clear() { this.#items = []; }
  toArray() { return [...this.#items]; }
  toString() { return \`Stack[\${this.#items.join(', ')}] ← top\`; }
}

// Example: balanced parentheses checker
function isBalanced(expression) {
  const stack = new Stack();
  const pairs = { ')': '(', ']': '[', '}': '{' };
  for (const char of expression) {
    if ('([{'.includes(char)) stack.push(char);
    else if (')]}'.includes(char)) {
      if (stack.isEmpty() || stack.pop() !== pairs[char]) return false;
    }
  }
  return stack.isEmpty();
}

// Example: reverse a string
function reverseString(str) {
  const stack = new Stack();
  for (const char of str) stack.push(char);
  let result = '';
  while (!stack.isEmpty()) result += stack.pop();
  return result;
}

// Demo
const s = new Stack();
s.push(1); s.push(2); s.push(3);
console.log(s.toString());
console.log('Peek:', s.peek());
console.log('Pop:', s.pop());
console.log(s.toString());

console.log('');
const tests = ['([]{})', '([)]', '{[()]}', '(((' ];
tests.forEach(t => console.log(\`isBalanced("\${t}"): \${isBalanced(t)}\`));

console.log('');
console.log('Reverse "hello":', reverseString('hello'));`,

// ── Canvas draw ────────────────────────────────────────────────────────────────
'canvas:Javascript': `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Drawing Canvas</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #111; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; font-family: system-ui, sans-serif; }
  #toolbar { display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: #1f2937; width: 100%; border-bottom: 1px solid #374151; flex-wrap: wrap; }
  .tool-btn { padding: 6px 14px; border: 1px solid #374151; border-radius: 8px; background: #111827; color: #e5e7eb; font-size: 0.85rem; cursor: pointer; transition: all 0.15s; }
  .tool-btn.active, .tool-btn:hover { background: #6366f1; border-color: #6366f1; color: #fff; }
  input[type=color] { width: 36px; height: 30px; border: none; border-radius: 6px; cursor: pointer; background: none; padding: 0; }
  label { font-size: 0.8rem; color: #9ca3af; display: flex; align-items: center; gap: 6px; }
  input[type=range] { width: 80px; accent-color: #6366f1; }
  canvas { cursor: crosshair; background: #fff; touch-action: none; }
</style>
</head>
<body>
<div id="toolbar">
  <button class="tool-btn active" id="brushBtn" onclick="setTool('brush',this)">✏️ Brush</button>
  <button class="tool-btn" id="eraserBtn" onclick="setTool('eraser',this)">🧹 Eraser</button>
  <label>Color <input type="color" id="colorPicker" value="#6366f1"></label>
  <label>Size <input type="range" id="sizeRange" min="1" max="60" value="8"></label>
  <button class="tool-btn" onclick="clearCanvas()">🗑 Clear</button>
  <button class="tool-btn" onclick="downloadCanvas()">⬇ Save</button>
</div>
<canvas id="c"></canvas>
<script>
  const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
  let tool = 'brush', drawing = false, lastX = 0, lastY = 0;

  function resize() {
    const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight - document.getElementById('toolbar').offsetHeight;
    ctx.putImageData(data, 0, 0);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  }

  function setTool(t, btn) {
    tool = t;
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    canvas.style.cursor = t === 'eraser' ? 'cell' : 'crosshair';
  }

  function getPos(e) {
    const r = canvas.getBoundingClientRect();
    const src = e.touches ? e.touches[0] : e;
    return [src.clientX - r.left, src.clientY - r.top];
  }

  function startDraw(e) {
    drawing = true;
    [lastX, lastY] = getPos(e);
  }

  function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    const [x, y] = getPos(e);
    const size = document.getElementById('sizeRange').value;
    const color = document.getElementById('colorPicker').value;
    ctx.globalCompositeOperation = tool === 'eraser' ? 'destination-out' : 'source-over';
    ctx.strokeStyle = tool === 'eraser' ? 'rgba(0,0,0,1)' : color;
    ctx.lineWidth = tool === 'eraser' ? size * 2 : size;
    ctx.beginPath(); ctx.moveTo(lastX, lastY); ctx.lineTo(x, y); ctx.stroke();
    [lastX, lastY] = [x, y];
  }

  function stopDraw() { drawing = false; }

  function clearCanvas() { ctx.clearRect(0, 0, canvas.width, canvas.height); }

  function downloadCanvas() {
    const a = document.createElement('a');
    a.download = 'drawing.png'; a.href = canvas.toDataURL(); a.click();
  }

  canvas.addEventListener('mousedown', startDraw); canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', stopDraw); canvas.addEventListener('mouseleave', stopDraw);
  canvas.addEventListener('touchstart', startDraw, {passive:false}); canvas.addEventListener('touchmove', draw, {passive:false});
  canvas.addEventListener('touchend', stopDraw);
  window.addEventListener('resize', resize);
  resize(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
<\/script>
</body>
</html>`,
    };
}

aiSendBtn.onclick = () => {
    const prompt = aiPromptInput.value.trim();
    if (!prompt) return;
    const p = JungleUI.getCurrentProject();
    const lang = selectedLanguages[0] || 'Javascript';
    const currentCode = (p && p.currentFile && p.files[p.currentFile]) || '';
    addAiMsg('user', escHtml(prompt));
    aiPromptInput.value = '';
    aiSendBtn.disabled = true;
    aiSendBtn.textContent = '⏳ Building...';
    const thinkingMsg = addAiMsg('assistant', '<em style="color:#528b74">Analyzing your request...</em>');
    setTimeout(() => {
        const { code, note } = JungleAI.generate(prompt, lang, aiIncludeCode.checked ? currentCode : '');
        aiSendBtn.disabled = false;
        aiSendBtn.textContent = '✨ Generate';
        const escapedCode = escHtml(code);
        thinkingMsg.className = 'ai-msg assistant';
        thinkingMsg.innerHTML = `<pre><code>${escapedCode}</code></pre><div style="margin-top:8px;font-size:0.8rem;color:#528b74">${escHtml(note)}</div><button class="ai-apply-btn">⬇ Apply to Editor</button>`;
        thinkingMsg.querySelector('.ai-apply-btn').onclick = () => {
            const editor = document.getElementById('code-editor');
            editor.value = code;
            editor.dispatchEvent(new Event('input'));
            if (p && p.currentFile) { p.files[p.currentFile] = code; JungleStorage.saveProjects(projects); }
            JungleUI.showToast('✅ Code applied to editor.');
            closeAiPanel();
        };
    }, 300);
};

window.onload = () => {
    projects = JungleStorage.getProjects();
};
