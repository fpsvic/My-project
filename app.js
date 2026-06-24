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
        const templates = {
            'HTML': {
                files: {
                    'index.html': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Jungle Project</title>\n</head>\n<body>\n    <h1>Hello from Jungle Editor</h1>\n    <script src="script.js"></script>\n</body>\n</html>',
                    'script.js': 'console.log("Jungle project ready.");'
                },
                currentFile: 'index.html'
            },
            'Python': {
                files: { 'main.py': 'def main():\n    print("Hello from Jungle Editor")\n\nmain()\n' },
                currentFile: 'main.py'
            },
            'TypeScript': {
                files: { 'main.ts': 'const message: string = "Hello from Jungle Editor";\nconsole.log(message);\n' },
                currentFile: 'main.ts'
            },
            'Java': {
                files: { 'Main.java': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Jungle Editor");\n    }\n}\n' },
                currentFile: 'Main.java'
            },
            'C++': {
                files: { 'main.cpp': '#include <iostream>\n\nint main() {\n    std::cout << "Hello from Jungle Editor" << std::endl;\n    return 0;\n}\n' },
                currentFile: 'main.cpp'
            },
            'C': {
                files: { 'main.c': '#include <stdio.h>\n\nint main(void) {\n    printf("Hello from Jungle Editor\\n");\n    return 0;\n}\n' },
                currentFile: 'main.c'
            },
            'Go': {
                files: { 'main.go': 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello from Jungle Editor")\n}\n' },
                currentFile: 'main.go'
            },
            'Rust': {
                files: { 'main.rs': 'fn main() {\n    println!("Hello from Jungle Editor");\n}\n' },
                currentFile: 'main.rs'
            }
        };
        const template = templates[lang] || templates.HTML;
        return { id, name, files: { ...template.files }, currentFile: template.currentFile, lang };
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
        const errors = [
            ...this.scanDelimiters(lines),
            ...this.scanLanguagePatterns(lang, lines)
        ];
        if (lang === 'HTML') {
            errors.push(...this.scanHtmlTags(lines));
        }
        return errors;
    }
    static makeIssue(line, msg, hint = "", kind = "Static analysis", column = null) {
        return { line, msg, hint, kind, column };
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
        const errors = [];
        lines.forEach((line, idx) => {
            const lineNum = idx + 1;
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('#')) return;
            if (lang === 'Python') {
                if (/^(if|elif|else|for|while|def|class|try|except|finally|with)\b/.test(trimmed) && !trimmed.endsWith(':') && !trimmed.endsWith('\\')) {
                    errors.push(this.makeIssue(lineNum, "Python block statement is missing a trailing colon.", "Add ':' at the end of the line.", "Python syntax"));
                }
                if (/^print\s+[^(\s]/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Python print statement is missing parentheses.", "Use print(...) in Python 3.", "Python syntax"));
                }
                if (/[=+\-*/%]$/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Python expression ends with an operator.", "Finish the expression after the operator or remove it.", "Python syntax"));
                }
                if (/\b(console\.log|let|const|var)\b/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "This looks like JavaScript inside a Python file.", "Switch the language to JavaScript or rewrite the line using Python syntax.", "Language mismatch"));
                }
                if (/^\s*def\s+\w+\([^)]*\)\s*$/.test(line) && !trimmed.endsWith(':')) {
                    errors.push(this.makeIssue(lineNum, "Python function definition is missing a colon.", "Add ':' at the end of the def line.", "Python syntax"));
                }
                if (/\bxrange\s*\(/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "'xrange' does not exist in Python 3.", "Replace xrange(...) with range(...).", "Python syntax"));
                }
                if (/^\s*(return|yield)\s*$/.test(line) && idx + 1 < lines.length && lines[idx + 1].trim() !== '') {
                    errors.push(this.makeIssue(lineNum, "Bare 'return' or 'yield' with no value — possible missing expression.", "If you intend to return a value, place it on the same line.", "Python syntax"));
                }
                if (/\b===/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Python does not use '===' for comparison.", "Use '==' for equality in Python.", "Language mismatch"));
                }
            } else if (lang === 'Javascript' || lang === 'TypeScript') {
                const condition = trimmed.match(/\b(if|while)\s*\((.*)\)/);
                if (condition && /(^|[^=!<>])=([^=>]|$)/.test(condition[2])) {
                    errors.push(this.makeIssue(lineNum, "Possible assignment inside a condition.", "Use '===' for comparison unless you intentionally meant assignment.", "JavaScript logic"));
                }
                if (/\b(const|let|var)\s+[A-Za-z_$][\w$]*\s*=$/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Variable declaration is missing a value after '='.", "Add the value or remove the assignment.", "JavaScript syntax"));
                }
                if (/^\s*(if|while|for)\s+[^(]/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "JavaScript control statement is missing parentheses.", "Wrap the condition in parentheses.", "JavaScript syntax"));
                }
                if (/^\s*(def|elif|print\s*\()\b/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "This looks like Python inside a JavaScript file.", "Switch the language to Python or rewrite the line using JavaScript syntax.", "Language mismatch"));
                }
                if (/\bawait\b/.test(trimmed) && !/\basync\b/.test(lines.slice(0, idx).join('\n').slice(-500))) {
                    errors.push(this.makeIssue(lineNum, "'await' used but no 'async' function found above.", "Make sure the enclosing function is declared with 'async'.", "JavaScript async"));
                }
                if (/==[^=]/.test(trimmed) && !/["'`].*==.*["'`]/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Loose equality '==' used — this can cause unexpected type coercion.", "Prefer '===' for strict equality checks.", "JavaScript logic"));
                }
                if (/\bvar\b/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "'var' is function-scoped and can lead to hoisting bugs.", "Use 'const' for values that don't change, or 'let' for reassignable variables.", "JavaScript style"));
                }
                if (lang === 'TypeScript' && /\binterface\s+[A-Za-z_$][\w$]*\s*$/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "TypeScript interface declaration is missing a body.", "Add { ... } after the interface name.", "TypeScript syntax"));
                }
                if (lang === 'TypeScript' && /:\s*any\b/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Type 'any' disables TypeScript type checking for this value.", "Replace 'any' with a specific type to get proper type safety.", "TypeScript style"));
                }
            } else if (lang === 'Java') {
                if (/public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)/.test(trimmed) && !/\{/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Java class declaration is missing an opening brace.", "Add '{' after the class declaration.", "Java syntax"));
                }
                if (/System\.out\.print(?:ln)?\s+["']/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Java print call is missing parentheses.", "Use System.out.println(...).", "Java syntax"));
                }
                if (/\bString\s+\w+\s*==\s*["']/.test(trimmed) || /["']\s*==\s*\w+/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "String comparison with '==' compares references, not values.", "Use .equals() to compare String content: str.equals(\"value\").", "Java logic"));
                }
                if (/^\s*[a-z][A-Za-z0-9]*\s+[a-z][A-Za-z0-9]*\s*=/.test(line) && !/^\s*(int|long|float|double|boolean|char|byte|short|String|var)\b/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "Variable declaration may be missing a type or import.", "Specify the type explicitly or import the class.", "Java syntax"));
                }
            } else if (lang === 'C++' || lang === 'C') {
                if (/^\s*#include\s+[A-Za-z0-9_./]+/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "Include directive is missing angle brackets or quotes.", "Use #include <iostream> or #include \"file.h\".", "C/C++ syntax"));
                }
                if (/\b(int|float|double|char|bool|long|short|void)\s+\w+\s*\([^)]*\)\s*$/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Function declaration or definition is missing ';' or '{'.", "Add ';' for a prototype or '{' for a function body.", "C/C++ syntax"));
                }
                if (/\bscanf\s*\(\s*["'][^"']*["']\s*,\s*[^&]/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "scanf argument may be missing '&' address operator.", "Pass the address of the variable: scanf(\"%d\", &var).", "C/C++ syntax"));
                }
                if (/\bmalloc\s*\(/.test(trimmed) && !/\bfree\s*\(/.test(lines.join('\n'))) {
                    errors.push(this.makeIssue(lineNum, "malloc() called but no free() found in the file.", "Remember to free() every malloc() to avoid memory leaks.", "C/C++ memory"));
                }
            } else if (lang === 'Go') {
                if (/^\s*func\s+\w+\s*\([^)]*$/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "Go function signature looks incomplete.", "Close the parameter list and add an opening brace.", "Go syntax"));
                }
                if (/fmt\.Print(?:ln|f)?\s+["']/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Go print call is missing parentheses.", "Use fmt.Println(...).", "Go syntax"));
                }
                if (/\b:=\b/.test(trimmed) && /^\s*(if|for|switch)\b/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "Short variable declaration ':=' inside control statement — variable will be scoped to the block.", "If you need the variable outside, declare it before the block with 'var'.", "Go scope"));
                }
                if (/\bimport\s+"/.test(trimmed) && !/\bfmt\b/.test(lines.join('\n')) && /\bfmt\./.test(lines.join('\n'))) {
                    errors.push(this.makeIssue(lineNum, "fmt package is used but may not be imported.", "Add \"fmt\" to your import block.", "Go imports"));
                }
            } else if (lang === 'Rust') {
                if (/\bprintln\s*\(/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Rust print macro is missing '!'.", "Use println!(...) instead of println(...).", "Rust syntax"));
                }
                if (/\bfn\s+\w+\s*\([^)]*\)\s*$/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "Rust function is missing a body.", "Add { ... } after the function signature.", "Rust syntax"));
                }
                if (/\blet\s+\w+\s*=/.test(trimmed) && !/\blet\s+mut\b/.test(trimmed) && /\w+\s*=\s*\w+/.test(lines.slice(idx + 1, idx + 5).join('\n').match(/^\s*\w+\s*=/) || '')) {
                    errors.push(this.makeIssue(lineNum, "Variable declared without 'mut' — Rust variables are immutable by default.", "Use 'let mut' if you need to reassign this variable.", "Rust immutability"));
                }
                if (/\bunwrap\s*\(\s*\)/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "unwrap() will panic if the value is None or Err.", "Use match, if let, or unwrap_or_else() to handle the error case safely.", "Rust error handling"));
                }
            } else if (lang === 'PHP') {
                if (/^\s*\$?\w+\s*=/.test(line) && !/^\s*\$/.test(line) && !/^\s*(if|else|for|while|foreach|function|class|return)\b/.test(line)) {
                    errors.push(this.makeIssue(lineNum, "PHP variables must start with '$'.", "Change the variable to $variableName.", "PHP syntax"));
                }
                if (/\becho\s+\w+\s*$/.test(trimmed) && !trimmed.endsWith(';')) {
                    errors.push(this.makeIssue(lineNum, "PHP statement may be missing a semicolon.", "Add ';' at the end of the line.", "PHP syntax"));
                }
            } else if (lang === 'Ruby') {
                if (/\bdef\s+\w+/.test(trimmed) && !lines.slice(idx, idx + 20).some(l => /^\s*end\b/.test(l))) {
                    errors.push(this.makeIssue(lineNum, "Ruby method defined with 'def' may be missing a closing 'end'.", "Add 'end' after the method body.", "Ruby syntax"));
                }
                if (/\bputs\s+\(/.test(trimmed)) {
                    errors.push(this.makeIssue(lineNum, "In Ruby, 'puts(...)' with parentheses is valid but 'puts ...' is idiomatic.", "You can drop the parentheses: puts value.", "Ruby style"));
                }
            }
        });
        return errors;
    }
    static detectLanguage(code) {
        if (!code || code.trim().length < 8) return null;
        const scores = {};
        const add = (lang, pts) => { scores[lang] = (scores[lang] || 0) + pts; };

        // --- Python ---
        if (/^\s*def\s+\w+\s*\(/m.test(code)) add('Python', 20);
        if (/^\s*class\s+\w+.*:/m.test(code)) add('Python', 15);
        if (/\belif\b/.test(code)) add('Python', 18);
        if (/^\s*from\s+\w+\s+import\b/m.test(code)) add('Python', 18);
        if (/\bimport\s+\w+(?!\s*\{)/m.test(code) && !/from\s+['"]/.test(code)) add('Python', 8);
        if (/\bprint\s*\(/.test(code) && !/console\./.test(code) && !/System\.out/.test(code)) add('Python', 10);
        if (/\bself\b/.test(code)) add('Python', 15);
        if (/\bNone\b/.test(code) && !/\/\//.test(code)) add('Python', 10);
        if (/\bTrue\b|\bFalse\b/.test(code) && !/\/\//.test(code)) add('Python', 8);
        if (/\bxrange\b|\belif\b|\blambda\b/.test(code)) add('Python', 12);
        if (/#[^!]/.test(code)) add('Python', 5);

        // --- JavaScript ---
        if (/\bconsole\.log\b/.test(code)) add('Javascript', 22);
        if (/\bdocument\.\w+|\bwindow\.\w+/.test(code)) add('Javascript', 18);
        if (/\bmodule\.exports\b/.test(code)) add('Javascript', 22);
        if (/\brequire\s*\(['"]/.test(code)) add('Javascript', 18);
        if (/\bPromise\b|\basync\s+function\b/.test(code)) add('Javascript', 12);
        if (/\bconst\b|\blet\b/.test(code) && !/:\s*(string|number|boolean)/.test(code)) add('Javascript', 8);
        if (/\bfunction\s+\w+\s*\(/.test(code) && !/\bdef\b/.test(code)) add('Javascript', 10);
        if (/=>\s*[{(]/.test(code)) add('Javascript', 10);
        if (/\bnull\b/.test(code) && /\bundefined\b/.test(code)) add('Javascript', 8);

        // --- TypeScript ---
        if (/\binterface\s+[A-Z]/.test(code)) add('TypeScript', 28);
        if (/\btype\s+[A-Z]\w*\s*=/.test(code)) add('TypeScript', 25);
        if (/\benum\s+\w+\s*\{/.test(code)) add('TypeScript', 25);
        if (/:\s*(string|number|boolean|void|never|unknown|any)\b/.test(code)) add('TypeScript', 18);
        if (/\bReadonly<|\bPartial<|\bRequired<|\bRecord</.test(code)) add('TypeScript', 28);
        if (/\)\s*:\s*[A-Za-z][\w<>[\]| ]+\s*(=>|\{)/.test(code)) add('TypeScript', 18);
        if (/<[A-Z]\w*>/.test(code) && /\binterface\b|\btype\b/.test(code)) add('TypeScript', 12);

        // --- HTML ---
        if (/<!DOCTYPE\s+html>/i.test(code)) add('HTML', 45);
        if (/<html[\s>]/i.test(code)) add('HTML', 28);
        if (/<\/?(div|span|body|head|script|style|meta|link)\b/i.test(code)) add('HTML', 20);
        if (/<\/\w+>/.test(code) && /<\w[\w-]*\s/.test(code)) add('HTML', 15);

        // --- C++ ---
        if (/#include\s*<\w+>/.test(code)) add('C++', 28);
        if (/\bstd::/.test(code)) add('C++', 28);
        if (/\bcout\s*<</.test(code)) add('C++', 28);
        if (/\btemplate\s*</.test(code)) add('C++', 28);
        if (/\bvector\s*<|\bmap\s*<|\bunordered_map\s*</.test(code)) add('C++', 22);
        if (/\bnew\s+\w+\s*\(/.test(code) && /::/.test(code)) add('C++', 12);
        if (/\bint\s+main\s*\(\s*\)/.test(code) && /#include/.test(code)) add('C++', 15);

        // --- C ---
        if (/#include\s*<stdio\.h>/.test(code)) add('C', 32);
        if (/\bprintf\s*\(/.test(code) && !/#include\s*<iostream>/.test(code)) add('C', 22);
        if (/\bscanf\s*\(/.test(code)) add('C', 22);
        if (/\bmalloc\s*\(|\bcalloc\s*\(|\bfree\s*\(/.test(code)) add('C', 22);
        if (/\bint\s+main\s*\(\s*void\s*\)/.test(code)) add('C', 22);
        if (/#include\s*<string\.h>/.test(code)) add('C', 15);

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
        if (/\[Serializable\]|\[HttpGet\]/.test(code)) add('C#', 25);

        // --- Go ---
        if (/^package\s+\w+/m.test(code)) add('Go', 28);
        if (/\bfunc\s+main\s*\(\)/.test(code)) add('Go', 28);
        if (/\bfmt\.Print(?:ln|f)?/.test(code)) add('Go', 22);
        if (/:=/.test(code)) add('Go', 15);
        if (/\bgoroutine\b|\bchan\b|\bselect\b/.test(code)) add('Go', 25);
        if (/\bimport\s+\(/.test(code)) add('Go', 18);

        // --- Rust ---
        if (/\bfn\s+main\s*\(\)/.test(code)) add('Rust', 28);
        if (/\bprintln!\s*\(/.test(code)) add('Rust', 28);
        if (/\blet\s+mut\b/.test(code)) add('Rust', 22);
        if (/\bimpl\s+\w+/.test(code)) add('Rust', 22);
        if (/\bSome\(|\bNone\b|\bOk\(|\bErr\(/.test(code)) add('Rust', 18);
        if (/\buse\s+std::/.test(code)) add('Rust', 22);
        if (/\bmatch\s+\w+\s*\{/.test(code)) add('Rust', 15);
        if (/\bunwrap\s*\(\)/.test(code)) add('Rust', 12);

        // --- PHP ---
        if (/<\?php/.test(code)) add('PHP', 45);
        if (/\$[a-zA-Z_]\w*/.test(code) && /\becho\b/.test(code)) add('PHP', 22);
        if (/\bforeach\s*\(\s*\$/.test(code)) add('PHP', 22);
        if (/\barray\s*\(/.test(code) && /\$/.test(code)) add('PHP', 15);

        // --- Ruby ---
        if (/^\s*end\s*$/m.test(code)) add('Ruby', 18);
        if (/\bputs\s+/.test(code) && /^\s*end\s*$/m.test(code)) add('Ruby', 22);
        if (/\bdo\s*\|[\w,\s]+\|/.test(code)) add('Ruby', 25);
        if (/\battr_(reader|writer|accessor)\b/.test(code)) add('Ruby', 28);
        if (/\brequire\s+['"]/.test(code) && /\.rb['"]/.test(code)) add('Ruby', 20);
        if (/=~\s*\//.test(code)) add('Ruby', 18);

        // --- Swift ---
        if (/\bimport\s+(Foundation|UIKit|SwiftUI)\b/.test(code)) add('Swift', 35);
        if (/\bguard\s+let\b|\bif\s+let\b/.test(code)) add('Swift', 25);
        if (/@State\b|@Binding\b|@Published\b|@ObservedObject\b/.test(code)) add('Swift', 35);
        if (/\bvar\s+\w+\s*:\s*[A-Z]/.test(code) && /\bfunc\b/.test(code)) add('Swift', 18);
        if (/\boptional\b|\?\s*\{/.test(code)) add('Swift', 12);

        // --- Kotlin ---
        if (/\bfun\s+main\s*\(/.test(code)) add('Kotlin', 28);
        if (/\bprintln\s*\(/.test(code) && /\bval\b|\bvar\b/.test(code)) add('Kotlin', 22);
        if (/\bdata\s+class\s+\w+/.test(code)) add('Kotlin', 28);
        if (/\bwhen\s*\(/.test(code)) add('Kotlin', 22);
        if (/\bnullable\b|\?\s*:/.test(code)) add('Kotlin', 15);

        // --- Bash ---
        if (/^#!\/bin\/(bash|sh)/m.test(code)) add('Bash', 45);
        if (/\$\{[^}]+\}/.test(code) && /\bfi\b/.test(code)) add('Bash', 22);
        if (/\[\[.*\]\]/.test(code)) add('Bash', 25);
        if (/\bfi\b/.test(code) && /\bthen\b/.test(code)) add('Bash', 22);
        if (/\bdone\b/.test(code) && /\bdo\b/.test(code) && /\bfor\b/.test(code)) add('Bash', 18);

        // --- R ---
        if (/<-\s*\w/.test(code)) add('R', 22);
        if (/\blibrary\s*\(/.test(code)) add('R', 22);
        if (/\bggplot\s*\(|\bdplyr\b|\btidyr\b/.test(code)) add('R', 28);
        if (/\bdata\.frame\s*\(/.test(code)) add('R', 22);
        if (/\bc\s*\([\d.,\s]+\)/.test(code)) add('R', 12);

        // --- Lua ---
        if (/\blocal\s+\w+\s*=/.test(code) && /\bend\b/.test(code)) add('Lua', 22);
        if (/\bipairs\s*\(|\bpairs\s*\(/.test(code)) add('Lua', 25);
        if (/\bfunction\s+\w+\s*\(/.test(code) && /\bend\b/.test(code) && !/\bdef\b/.test(code)) add('Lua', 18);
        if (/--[^\n]/.test(code) && /\blocal\b/.test(code)) add('Lua', 12);

        // --- Scala ---
        if (/\bobject\s+\w+\s+extends\b/.test(code)) add('Scala', 28);
        if (/\bcase\s+class\b/.test(code)) add('Scala', 28);
        if (/\bdef\s+\w+\s*\(/.test(code) && /\bval\b|\bvar\b/.test(code)) add('Scala', 15);
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

        const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
        if (sorted.length === 0 || sorted[0][1] < 12) return null;
        const [topLang, topScore] = sorted[0];
        const runnerUp = sorted[1] ? sorted[1][1] : 0;
        // Require clear winner — top must be meaningfully ahead of runner-up
        if (topScore - runnerUp < 8 && topScore < 30) return null;
        return { lang: topLang, score: topScore, ext: JungleIntelligence.getDefaultExtension(topLang) || '.txt' };
    }
}
class JungleRunner {
    static async execute(lang, code, files) {
        try {
            const scanErrors = JungleScanner.scan(lang, code);
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
                    additionalErrors: scanErrors.slice(1, 4)
                };
                this.printCrashAnalysis(errorDetails, "", "");
                const extra = scanErrors.length > 1 ? ` (+${scanErrors.length - 1} more)` : "";
                JungleUI.showToast(`❌ ${scanErrors.length} issue${scanErrors.length > 1 ? 's' : ''} found${extra}. Tap to inspect.`, () => {
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
    static formatSimpleReport(details) {
        const lineNo = details.lineNo || "Unknown";
        const errorKind = this.getSimpleErrorKind(details.errorMsg || "");
        const message = this.simplifyErrorMessage(details.errorMsg || "unknown error");
        let out = `An error occurred running your code — Line ${lineNo}\n${errorKind} << ${message} >>`;
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
            output += `\n\n─── Additional issues found ───`;
            details.additionalErrors.forEach(e => {
                output += `\nLine ${e.line}: [${e.kind}] ${e.msg}`;
                if (e.hint) output += `\n  → ${e.hint}`;
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
        const code = editor.value, detection = JungleScanner.detectLanguage(code);
        if (detection) {
            const detectedLang = detection.lang;
            if (detectedLang !== selectedLanguages[0]) {
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
                JungleUI.showToast(`Auto-detected: ${detectedLang} — tap language button to override.`);
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
