interface ScanIssue {
    line: number;
    msg: string;
    hint: string;
    kind: string;
    column: number | null;
    severity: 'error' | 'warning' | 'info';
}

interface DetectionResult {
    lang: string;
    score: number;
    confidence: 'confirmed' | 'tentative';
    ext: string;
}

class JungleScanner {
    static scan(lang: string, code: string): ScanIssue[] {
        const lines = code.split('\n');
        const issues: ScanIssue[] = [
            ...this.scanDelimiters(lines),
            ...this.scanLanguagePatterns(lang, lines)
        ];
        if (lang === 'HTML') issues.push(...this.scanHtmlTags(lines));
        if (lang === 'Python') issues.push(...this.scanPythonIndentation(lines));
        const order: Record<string, number> = { error: 0, warning: 1, info: 2 };
        issues.sort((a, b) => (order[a.severity] ?? 1) - (order[b.severity] ?? 1) || a.line - b.line);
        return issues;
    }
    static scanPythonIndentation(lines: string[]): ScanIssue[] {
        const issues: ScanIssue[] = [];
        const indentStack: number[] = [0];
        let prevIndent = 0;
        let expectIndent = false;
        for (let i = 0; i < lines.length; i++) {
            const raw = lines[i];
            const trimmed = raw.trim();
            if (!trimmed || trimmed.startsWith('#')) continue;
            const indent = raw.match(/^(\s*)/)![1].length;
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
    static makeIssue(line: number, msg: string, hint: string = "", kind: string = "Static analysis", column: number | null = null, severity: 'error' | 'warning' | 'info' = "error"): ScanIssue {
        return { line, msg, hint, kind, column, severity };
    }
    static scanDelimiters(lines: string[]): ScanIssue[] {
        const errors: ScanIssue[] = [];
        const stack: Array<{ char: string; line: number; column: number }> = [];
        const bracketPairs: Record<string, string> = { '(': ')', '[': ']', '{': '}' };
        const matchingPairs: Record<string, string> = { ')': '(', ']': '[', '}': '{' };
        let inBlockComment = false;
        let inString: string | null = null;
        let blockCommentStart: { line: number; column: number } | null = null;
        let stringStart: { line: number; column: number } | null = null;
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
                        const last = stack.pop()!;
                        if (last.char !== matchingPairs[char]) {
                            errors.push(this.makeIssue(lineNum, `Mismatched closing bracket '${char}' - expected '${bracketPairs[last.char]}' for '${last.char}' from line ${last.line}.`, `Close '${last.char}' with '${bracketPairs[last.char]}' before using '${char}'.`, "Delimiter check", j + 1));
                        }
                    }
                }
            }
            if (inString && inString !== '`' && !line.trimEnd().endsWith('\\')) {
                errors.push(this.makeIssue(stringStart!.line, `Unclosed string literal starting with ${inString}.`, `Add a closing ${inString} before the end of the line.`, "String check", stringStart!.column));
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
            const unclosed = stack.pop()!;
            errors.push(this.makeIssue(unclosed.line, `Unclosed bracket or delimiter '${unclosed.char}' detected.`, `Add '${bracketPairs[unclosed.char]}' to close the block opened here.`, "Delimiter check", unclosed.column));
        }
        return errors;
    }
    static scanHtmlTags(lines: string[]): ScanIssue[] {
        const errors: ScanIssue[] = [];
        const stack: Array<{ tag: string; line: number; column: number }> = [];
        const voidTags = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
        const tagRegex = /<!--[\s\S]*?-->|<!doctype[^>]*>|<\/?([a-zA-Z0-9:-]+)(?:\s[^>]*)?>/gi;
        const code = lines.join('\n');
        let match: RegExpExecArray | null;
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
            const unclosed = stack.pop()!;
            errors.push(this.makeIssue(unclosed.line, `Unclosed HTML tag <${unclosed.tag}> detected.`, `Add </${unclosed.tag}> after this element's content.`, "HTML structure", unclosed.column));
        }
        return errors;
    }
    static scanLanguagePatterns(lang: string, lines: string[]): ScanIssue[] {
        const issues: ScanIssue[] = [];
        const fullCode = lines.join('\n');
        const e = (ln: number, msg: string, hint: string, kind: string, sev: 'error' | 'warning' | 'info' = "error") => issues.push(this.makeIssue(ln, msg, hint, kind, null, sev));
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
    static earlyHint(code: string): string | null {
        const hints: Array<[RegExp, string]> = [
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

    static detectLanguage(code: string): DetectionResult | null {
        if (!code || code.trim().length < 3) return null;
        const scores: Record<string, number> = {};
        const add = (lang: string, pts: number): void => { scores[lang] = (scores[lang] || 0) + pts; };

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
        const sub = (lang: string, pts: number): void => { scores[lang] = (scores[lang] || 0) - pts; };
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
            const confidence: 'confirmed' | 'tentative' | null = topScore >= 35 ? 'confirmed' : topScore >= 18 ? 'tentative' : null;
            if (!confidence) return null;
            return { lang: topLang, score: topScore, confidence, ext: JungleIntelligence.getDefaultExtension(topLang) || '.txt' };
        }
        return null;
    }
}
