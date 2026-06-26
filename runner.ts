interface RunResult {
    stdout: string;
    stderr: string;
    errName?: string;
    errStack?: string;
}

interface ErrorDetails {
    errorMsg: string;
    lineNo: string | number;
    file?: string;
    column?: string | number | null;
    likelyCause?: string;
    suggestion?: string;
    severity?: string;
    additionalErrors?: ScanIssue[];
    rawOutput?: string;
    errorType?: string;
}

interface RunMeta {
    errName?: string;
    errStack?: string;
}

class JungleRunner {
    static async execute(lang: string, code: string, files: Record<string, string>): Promise<void> {
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
                const errorDetails: ErrorDetails = {
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
            terminalStatus.textContent = "RUNNING";
            terminalStatus.className = "text-[#74a896] font-bold animate-pulse";
            const p = JungleUI.getCurrentProject();
            if (!p) return;

            // ── Tier 1: Native JS/TS (no network) ─────────────────────────────
            if (lang === 'Javascript' || lang === 'TypeScript') {
                terminalViewBody.textContent = "⚡ Running locally (native JS)...";
                const res = await this.runNativeJS(code);
                this.showRunResult(res.stdout, res.stderr, lang);
                return;
            }
            // ── Tier 2: SQL — sql.js WASM (no network) ────────────────────────
            if (lang === 'SQL') {
                await this.runSqlJs(code);
                return;
            }
            // ── Tier 3: Language-specific WASM runtimes ────────────────────────
            const wasmRunner: Record<string, () => Promise<RunResult>> = {
                'Python': () => this.runPyodide(code),
                'PHP':    () => this.runPhpWasm(code),
                'Lua':    () => this.runLuaWasm(code),
                'Ruby':   () => this.runRubyOpal(code),
            };
            const runner = wasmRunner[lang];
            if (runner) {
                try {
                    const res = await runner();
                    this.showRunResult(res.stdout, res.stderr, lang);
                    return;
                } catch (e: any) {
                    terminalViewBody.textContent += `\n⚠️ WASM runtime failed (${e.message}), trying API fallback...`;
                }
            }
            // ── Tier 4: Judge0 CE (60+ languages, no auth) ────────────────────
            terminalViewBody.textContent = "🌐 Connecting to Judge0 API...";
            const j0 = await this.runJudge0(lang, code);
            if (j0) { this.showRunResult(j0.stdout, j0.stderr, lang); return; }
            // ── Tier 5: Piston + CORS proxy fallback chain ────────────────────
            terminalViewBody.textContent += "\n⚠️ Judge0 unreachable, trying Piston cluster...";
            await this.runPiston(lang, code, p);

        } catch (globalErr: any) { this.handleGlobalFailure(globalErr); }
        terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
    }

    // ── Native JS execution via sandboxed iframe + postMessage ────────────────
    static runNativeJS(code: string): Promise<RunResult> {
        return new Promise(resolve => {
            const output: string[] = [];
            const handler = (e: MessageEvent) => {
                if (!e.data || typeof e.data !== 'object') return;
                if (e.data.__jOut) output.push(e.data.t);
                if (e.data.__jDone) {
                    clearTimeout(timer);
                    window.removeEventListener('message', handler);
                    iframe.remove();
                    resolve({ stdout: output.join('\n'), stderr: e.data.err || '' });
                }
            };
            window.addEventListener('message', handler);
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
            const wrap = (fn: string) => `(...a)=>{try{parent.postMessage({__jOut:true,t:[...a].map(x=>typeof x==='object'?JSON.stringify(x):String(x)).join(' ')},'*')}catch(e){}}`;
            iframe.srcdoc = `<!DOCTYPE html><html><body><script>
const console={log:${wrap('log')},info:${wrap('info')},warn:(...a)=>parent.postMessage({__jOut:true,t:'WARN: '+[...a].join(' ')},'*'),error:(...a)=>parent.postMessage({__jOut:true,t:'ERROR: '+[...a].join(' ')},'*'),dir:${wrap('dir')},table:${wrap('table')}};
try{${code.replace(/<\/script>/gi,'<\\/script>')}\nparent.postMessage({__jDone:true,err:''},'*');}catch(e){parent.postMessage({__jDone:true,err:e.toString()},'*');}
<\/script></body></html>`;
            const timer = setTimeout(() => {
                window.removeEventListener('message', handler);
                iframe.remove();
                resolve({ stdout: output.join('\n'), stderr: 'Execution timed out after 10s' });
            }, 10000);
        });
    }

    // ── Pyodide — Python WASM ─────────────────────────────────────────────────
    static async runPyodide(code: string): Promise<RunResult> {
        if (!window._pyodide) {
            terminalViewBody.textContent = "⏳ Loading Python WASM (~10 MB, cached after first load)...";
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/pyodide.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
            window._pyodide = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/' });
        }
        const py = window._pyodide;
        const out: string[] = [], err: string[] = [];
        py.setStdout({ batched: (s: string) => out.push(s) });
        py.setStderr({ batched: (s: string) => err.push(s) });
        try { await py.runPythonAsync(code); }
        catch (e: any) { err.push(e.message); }
        return { stdout: out.join('\n'), stderr: err.join('\n') };
    }

    // ── php-wasm — PHP 8 WASM ─────────────────────────────────────────────────
    static async runPhpWasm(code: string): Promise<RunResult> {
        if (!window._phpWasm) {
            terminalViewBody.textContent = "⏳ Loading PHP 8 WASM (~10 MB, cached after first load)...";
            const mod = await import('https://cdn.jsdelivr.net/npm/php-wasm/PhpWeb.mjs');
            window._phpWasm = mod.PhpWeb;
        }
        return new Promise(async resolve => {
            const php = new window._phpWasm();
            const out: string[] = [], err: string[] = [];
            php.addEventListener('output', (e: any) => out.push(...e.detail));
            php.addEventListener('error',  (e: any) => err.push(...e.detail));
            const src = code.trim().startsWith('<?') ? code : `<?php\n${code}`;
            try { await php.run(src); } catch(e: any) { err.push(e.message); }
            resolve({ stdout: out.join(''), stderr: err.join('') });
        });
    }

    // ── wasmoon — Lua 5.4 WASM ───────────────────────────────────────────────
    static async runLuaWasm(code: string): Promise<RunResult> {
        if (!window._luaFactory) {
            terminalViewBody.textContent = "⏳ Loading Lua WASM (~1 MB, cached after first load)...";
            const mod = await import('https://cdn.jsdelivr.net/npm/wasmoon@1.16.0/+esm');
            window._luaFactory = new mod.LuaFactory('https://unpkg.com/wasmoon@1.16.0/dist/glue.wasm');
        }
        const out: string[] = [], err: string[] = [];
        const lua = await window._luaFactory.createEngine();
        lua.global.set('print', (...a: any[]) => out.push(a.map(String).join('\t')));
        try { await lua.doString(code); }
        catch (e: any) { err.push(e.message); }
        lua.global.close();
        return { stdout: out.join('\n'), stderr: err.join('\n') };
    }

    // ── Opal — Ruby → JS transpiler (in-browser, no WASM download) ───────────
    static async runRubyOpal(code: string): Promise<RunResult> {
        if (!window.Opal) {
            terminalViewBody.textContent = "⏳ Loading Ruby (Opal) runtime...";
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://cdn.opalrb.com/opal/current/opal.min.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://cdn.opalrb.com/opal/current/opal-parser.min.js';
                s.onload = () => { Opal.load('opal-parser'); res(); };
                s.onerror = rej;
                document.head.appendChild(s);
            });
        }
        const out: string[] = [];
        const origWrite = Opal.gvars['$stdout'] && Opal.gvars['$stdout'].write;
        try {
            Opal.gvars['$stdout'] = { write: (s: string) => { out.push(s); return s.length; }, puts: (s: string) => { out.push(s + '\n'); } };
            Opal.eval(code);
        } catch(e: any) {
            return { stdout: out.join(''), stderr: e.message || String(e) };
        }
        return { stdout: out.join(''), stderr: '' };
    }

    // ── sql.js — SQLite WASM ──────────────────────────────────────────────────
    static async runSqlJs(code: string): Promise<void> {
        switchView('terminal', false);
        terminalStatus.textContent = "RUNNING";
        terminalStatus.className = "text-[#74a896] font-bold animate-pulse";
        if (!window._sqlJs) {
            terminalViewBody.textContent = "⏳ Loading SQLite WASM (~1 MB, cached after first load)...";
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://sql.js.org/dist/sql-wasm.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
            window._sqlJs = await initSqlJs({ locateFile: (f: string) => `https://sql.js.org/dist/${f}` });
        }
        try {
            const db = new window._sqlJs.Database();
            const results = db.exec(code);
            if (!results.length) {
                terminalViewBody.textContent = "Query executed successfully (no rows returned).";
            } else {
                const lines: string[] = [];
                results.forEach((r: any) => {
                    lines.push(r.columns.join(' | '));
                    lines.push('─'.repeat(r.columns.join(' | ').length));
                    r.values.forEach((row: any[]) => lines.push(row.join(' | ')));
                    lines.push('');
                });
                terminalViewBody.textContent = lines.join('\n');
            }
            db.close();
            terminalStatus.textContent = "SUCCESS";
            terminalStatus.className = "text-emerald-400 font-bold";
        } catch(e: any) {
            terminalViewBody.textContent = `SQL Error: ${e.message}`;
            terminalStatus.textContent = "FAILED TO RUN";
            terminalStatus.className = "text-rose-500 font-bold";
        }
    }

    // ── Judge0 CE — 60+ languages, no auth ───────────────────────────────────
    static async runJudge0(lang: string, code: string): Promise<RunResult | null> {
        const ids: Record<string, number> = {
            'Javascript': 63, 'TypeScript': 74, 'Python': 71,
            'Java': 62, 'C': 50, 'C++': 54, 'C#': 51,
            'Go': 60, 'Rust': 73, 'Ruby': 72, 'PHP': 68,
            'Swift': 83, 'Kotlin': 78, 'Scala': 81,
            'R': 80, 'Perl': 85, 'Haskell': 61,
            'Lua': 64, 'Bash': 46, 'Fortran': 59,
            'Erlang': 58, 'Elixir': 57, 'Clojure': 86,
            'OCaml': 65, 'D': 56, 'Assembly': 45,
            'Lisp': 55, 'Prolog': 69, 'Pascal': 67,
        };
        const id = ids[lang];
        if (!id) return null;
        const base = 'https://ce.judge0.com';
        const enc = encodeURIComponent;
        const proxies = [
            base,
            `https://corsproxy.io/?${base}`,
            `https://api.allorigins.win/raw?url=${enc(base)}`,
        ];
        const body = JSON.stringify({ source_code: code, language_id: id, stdin: '' });
        for (const proxy of proxies) {
            try {
                const res = await fetch(`${proxy}/submissions?base64_encoded=false&wait=true`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                const stdout: string = data.stdout || '';
                const stderr: string = (data.stderr || '') + (data.compile_output || '');
                return { stdout, stderr };
            } catch(_) {}
        }
        return null;
    }

    // ── Piston cluster — last resort fallback ─────────────────────────────────
    static async runPiston(lang: string, code: string, p: Project): Promise<void> {
        const langMap: Record<string, string> = { 'Javascript': 'javascript', 'Python': 'python', 'C++': 'cpp', 'Java': 'java', 'TypeScript': 'typescript', 'C': 'c', 'C#': 'csharp', 'Ruby': 'ruby', 'Go': 'go', 'Rust': 'rust', 'PHP': 'php', 'Swift': 'swift', 'Kotlin': 'kotlin', 'Scala': 'scala', 'R': 'r', 'Perl': 'perl', 'Haskell': 'haskell', 'Julia': 'julia', 'Lua': 'lua', 'Clojure': 'clojure', 'Elixir': 'elixir', 'Erlang': 'erlang', 'OCaml': 'ocaml', 'F#': 'fsharp', 'Dart': 'dart', 'Bash': 'bash', 'Fortran': 'fortran', 'COBOL': 'cobol', 'D': 'd', 'Zig': 'zig', 'Nim': 'nim', 'Assembly': 'nasm', 'Lisp': 'commonlisp', 'Prolog': 'prolog', 'Pascal': 'pascal' };
        const pistonLang = langMap[lang] || 'javascript';
        const filesArray: Array<{ name: string; content: string }> = [{ name: p.currentFile || 'main', content: code }];
        Object.keys(p.files).forEach(f => { if (f !== p.currentFile) filesArray.push({ name: f, content: p.files[f] }); });
        const payload = { language: pistonLang, version: '*', files: filesArray };
        const e1 = 'https://emkc.org/api/v2/piston/execute';
        const e2 = 'https://piston.engineering.purdue.edu/api/v2/piston/execute';
        const enc = encodeURIComponent;
        const endpoints: Array<{ name: string; url: string; raw?: boolean; corssh?: boolean }> = [
            { name: 'EMKC', url: e1 }, { name: 'Purdue', url: e2 },
            { name: 'corsproxy→EMKC', url: `https://corsproxy.io/?${e1}` },
            { name: 'corsproxy→Purdue', url: `https://corsproxy.io/?${e2}` },
            { name: 'allorigins→EMKC', url: `https://api.allorigins.win/raw?url=${enc(e1)}`, raw: true },
            { name: 'allorigins→Purdue', url: `https://api.allorigins.win/raw?url=${enc(e2)}`, raw: true },
            { name: 'cors.sh→EMKC', url: `https://cors.sh/${e1}`, corssh: true },
            { name: 'cors-anywhere→EMKC', url: `https://cors-anywhere.herokuapp.com/${e1}` },
            { name: 'thingproxy→EMKC', url: `https://thingproxy.freeboard.io/fetch/${e1}` },
        ];
        let result: any = null;
        for (let i = 0; i < endpoints.length; i++) {
            const ep = endpoints[i];
            if (i > 0) terminalViewBody.textContent += `\n↳ Trying ${ep.name}...`;
            try {
                const headers: Record<string, string> = { 'Content-Type': 'application/json' };
                if (ep.corssh) headers['x-cors-api-key'] = 'temp_' + Math.random().toString(36).slice(2);
                const res = await fetch(ep.url, { method: 'POST', headers, body: JSON.stringify(payload) });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                result = ep.raw ? JSON.parse(await res.text()) : await res.json();
                break;
            } catch(_) {}
        }
        if (result && result.run) {
            this.showRunResult(result.run.stdout || '', result.run.stderr || '', lang);
        } else {
            terminalStatus.textContent = "ALL RUNTIMES OFFLINE";
            terminalStatus.className = "text-rose-500 font-bold";
            terminalViewBody.textContent = this.formatSimpleReport({
                lineNo: "—", errorMsg: "All execution engines unreachable",
                likelyCause: "JS/HTML run locally. Python/PHP/Lua/Ruby/SQL load via WASM. All API endpoints (Judge0, Piston) are currently blocked or offline.",
                suggestion: "Try a different network or browser extension blocker settings. JS and HTML always work offline."
            });
        }
    }

    // ── Shared result display ─────────────────────────────────────────────────
    static showRunResult(stdout: string, stderr: string, lang: string): void {
        const hasFail = stderr && stderr.trim();
        terminalViewBody.textContent = '';
        if (hasFail) {
            const details = this.parseError(stderr, stdout, lang);
            this.printCrashAnalysis(details, stdout, stderr);
            JungleUI.showToast("❌ Runtime error — tap to inspect.", () => switchView('terminal', false));
            terminalStatus.textContent = "FAILED TO RUN";
            terminalStatus.className = "text-rose-500 font-bold";
        } else {
            terminalViewBody.textContent = stdout || "Program executed successfully with no output.";
            terminalStatus.textContent = "SUCCESS";
            terminalStatus.className = "text-emerald-400 font-bold";
        }
        terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
    }
    static handleGlobalFailure(err: Error | string): void {
        switchView('terminal', false);
        terminalStatus.textContent = "FAILED TO RUN";
        terminalStatus.className = "text-rose-500 font-bold";
        terminalViewBody.textContent = this.formatSimpleReport({
            lineNo: "Unknown",
            errorMsg: (err as any).message || err || "environment failure"
        });
        JungleUI.showToast("❌ Failed to run! Tap here to inspect terminal diagnostics.", () => { switchView('terminal', false); });
    }
    static parseError(stderr: string, stdout: string, lang: string): ErrorDetails {
        let errorMsg = "Execution anomaly detected.", lineNo: string | number = "Unknown line", file = "main";
        let column: string | number | null = null, likelyCause = "", suggestion = "";
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
    static explainError(errorMsg: string, lang: string, rawOutput: string): { likelyCause: string; suggestion: string } {
        const text = `${errorMsg}\n${rawOutput || ""}`.toLowerCase();
        const rules: Array<{ test: RegExp; cause: string; fix: string }> = [
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
    static getCodeFrame(file: string, lineNo: string | number, column: string | number | null = null): string {
        const p = JungleUI.getCurrentProject();
        if (!p || !p.files) return "";
        const source = p.files[file] || p.files[p.currentFile];
        const lineNumber = Number(lineNo);
        if (!source || !Number.isFinite(lineNumber)) return "";
        const lines = source.split('\n');
        const start = Math.max(1, lineNumber - 2);
        const end = Math.min(lines.length, lineNumber + 2);
        const frame: string[] = [];
        for (let i = start; i <= end; i++) {
            const marker = i === lineNumber ? ">" : " ";
            frame.push(`${marker} ${String(i).padStart(4, ' ')} | ${lines[i - 1]}`);
            if (i === lineNumber && column) {
                frame.push(`       | ${" ".repeat(Math.max(0, Number(column) - 1))}^`);
            }
        }
        return frame.join('\n');
    }
    static severityIcon(sev: string): string {
        if (sev === 'warning') return '⚠️';
        if (sev === 'info') return 'ℹ️';
        return '⛔';
    }
    static formatSimpleReport(details: ErrorDetails): string {
        const lineNo = details.lineNo || "Unknown";
        const errorKind = this.getSimpleErrorKind(details.errorMsg || "");
        const message = this.simplifyErrorMessage(details.errorMsg || "unknown error");
        const icon = this.severityIcon(details.severity || "");
        let out = `${icon} Error on Line ${lineNo} — ${errorKind}\n   ${message}`;
        if (details.likelyCause) out += `\n\nLikely cause: ${details.likelyCause}`;
        if (details.suggestion) out += `\nSuggestion:   ${details.suggestion}`;
        return out;
    }
    static getSimpleErrorKind(message: string): string {
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
    static simplifyErrorMessage(message: string): string {
        let text = String(message || "unknown error").trim();
        if (/Unexpected end of input/i.test(text)) return "unexpected end of input";
        const closingBracket = text.match(/(?:Unexpected token|unexpected|Mismatched closing bracket)\s*['"`]?([}\])])['"`]?/i);
        if (closingBracket) return `unexpected ${closingBracket[1]}`;
        const unclosed = text.match(/Unclosed bracket or delimiter\s*['"`]?([({[])['"`]?/i);
        if (unclosed) {
            const closers: Record<string, string> = { '(': ')', '[': ']', '{': '}' };
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
    static printCrashAnalysis(details: ErrorDetails, stdout: string, stderr: string): void {
        let output = this.formatSimpleReport(details);
        if (details.lineNo && details.lineNo !== "Unknown") {
            const frame = this.getCodeFrame(details.file || "", details.lineNo, details.column);
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
