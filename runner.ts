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
    compiler?: string;
}

interface LangMeta {
    compiled: boolean;
    runtime: string;
    judge0: number | null;
    piston: string | null;
    wasm?: string;
}

class JungleRunner {
    // Per-language metadata: compiler/runtime name, whether it's a compiled language,
    // Judge0 CE language ID, Piston language name, optional WASM offline runtime key
    static LANG_META: Record<string, LangMeta> = {
        'Javascript': { compiled: false, runtime: 'Node.js / V8',        judge0: 63,   piston: 'javascript' },
        'TypeScript': { compiled: true,  runtime: 'tsc → V8',            judge0: 74,   piston: 'typescript' },
        'Python':     { compiled: false, runtime: 'CPython 3.12',        judge0: 71,   piston: 'python',    wasm: 'pyodide' },
        'Java':       { compiled: true,  runtime: 'javac + JVM 17',      judge0: 62,   piston: 'java' },
        'C':          { compiled: true,  runtime: 'GCC 12',              judge0: 50,   piston: 'c' },
        'C++':        { compiled: true,  runtime: 'G++ 12',              judge0: 54,   piston: 'cpp' },
        'C#':         { compiled: true,  runtime: 'dotnet / Mono',       judge0: 51,   piston: 'csharp' },
        'Go':         { compiled: true,  runtime: 'Go compiler 1.21',    judge0: 60,   piston: 'go' },
        'Rust':       { compiled: true,  runtime: 'rustc 1.75',          judge0: 73,   piston: 'rust' },
        'Kotlin':     { compiled: true,  runtime: 'kotlinc + JVM',       judge0: 78,   piston: 'kotlin' },
        'Swift':      { compiled: true,  runtime: 'swiftc 5.9',          judge0: 83,   piston: 'swift' },
        'Scala':      { compiled: true,  runtime: 'scalac + JVM',        judge0: 81,   piston: 'scala' },
        'Haskell':    { compiled: true,  runtime: 'GHC 9.4',             judge0: 61,   piston: 'haskell' },
        'Elixir':     { compiled: true,  runtime: 'elixirc + BEAM',      judge0: 57,   piston: 'elixir' },
        'Erlang':     { compiled: true,  runtime: 'erlc + BEAM',         judge0: 58,   piston: 'erlang' },
        'Clojure':    { compiled: true,  runtime: 'Clojure + JVM',       judge0: 86,   piston: 'clojure' },
        'OCaml':      { compiled: true,  runtime: 'ocamlopt',            judge0: 65,   piston: 'ocaml' },
        'F#':         { compiled: true,  runtime: 'dotnet F# 8',         judge0: 87,   piston: 'fsharp' },
        'D':          { compiled: true,  runtime: 'DMD 2.105',           judge0: 56,   piston: 'd' },
        'Fortran':    { compiled: true,  runtime: 'gfortran 12',         judge0: 59,   piston: 'fortran' },
        'COBOL':      { compiled: true,  runtime: 'GnuCOBOL 3.1',       judge0: 77,   piston: 'cobol' },
        'Pascal':     { compiled: true,  runtime: 'FPC 3.2',             judge0: 67,   piston: 'pascal' },
        'Assembly':   { compiled: true,  runtime: 'NASM + ld',           judge0: 45,   piston: 'nasm' },
        'Dart':       { compiled: true,  runtime: 'dart 3.2',            judge0: null, piston: 'dart' },
        'Zig':        { compiled: true,  runtime: 'zig 0.11',            judge0: null, piston: 'zig' },
        'Nim':        { compiled: true,  runtime: 'nim 2.0',             judge0: null, piston: 'nim' },
        'Julia':      { compiled: false, runtime: 'Julia 1.9 (JIT)',     judge0: null, piston: 'julia' },
        'Ruby':       { compiled: false, runtime: 'Ruby 3.2',            judge0: 72,   piston: 'ruby',   wasm: 'opal' },
        'PHP':        { compiled: false, runtime: 'PHP 8.2',             judge0: 68,   piston: 'php',    wasm: 'php-wasm' },
        'Lua':        { compiled: false, runtime: 'Lua 5.4',             judge0: 64,   piston: 'lua',    wasm: 'wasmoon' },
        'R':          { compiled: false, runtime: 'R 4.3',               judge0: 80,   piston: 'r' },
        'Perl':       { compiled: false, runtime: 'Perl 5.36',           judge0: 85,   piston: 'perl' },
        'Bash':       { compiled: false, runtime: 'Bash 5.2',            judge0: 46,   piston: 'bash' },
        'Lisp':       { compiled: false, runtime: 'SBCL 2.3',            judge0: 55,   piston: 'commonlisp' },
        'Prolog':     { compiled: false, runtime: 'SWI-Prolog 9',        judge0: 69,   piston: 'prolog' },
        'SQL':        { compiled: false, runtime: 'SQLite 3.43',         judge0: null, piston: null },
    };

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

            const meta = this.LANG_META[lang] || { compiled: false, runtime: lang, judge0: null, piston: null };
            const actionLabel = meta.compiled
                ? `⚙️ Compiling with ${meta.runtime}...`
                : `▶ Running with ${meta.runtime}...`;

            // ── Tier 1: Visual JS/TS — DOM/canvas code rendered in preview iframe ─
            if ((lang === 'Javascript' || lang === 'TypeScript') && this.isVisualCode(code)) {
                let jsCode = code;
                if (lang === 'TypeScript') {
                    terminalViewBody.textContent = "⚙️ Compiling TypeScript (tsc)...";
                    try { jsCode = await this.compileTypeScript(code); }
                    catch (tsErr: any) { terminalViewBody.textContent += `\n  → ${tsErr.message}`; }
                }
                this.renderJSPreview(jsCode);
                return;
            }

            // ── Tier 2: Native JS console output (always works, no network) ─────
            if (lang === 'Javascript') {
                terminalViewBody.textContent = "";
                const res = await this.runNativeJS(code);
                this.showRunResult(res.stdout, res.stderr, lang, { errName: res.errName, errStack: res.errStack });
                return;
            }

            // ── Tier 3: TypeScript — in-browser tsc (offline-capable) ─────────
            if (lang === 'TypeScript') {
                terminalViewBody.textContent = "⚙️ Compiling TypeScript (tsc)...";
                try {
                    const js = await this.compileTypeScript(code);
                    const res = await this.runNativeJS(js);
                    this.showRunResult(res.stdout, res.stderr, lang, { errName: res.errName, errStack: res.errStack, compiler: 'tsc (in-browser)' });
                    return;
                } catch (tsErr: any) {
                    terminalViewBody.textContent += `\n  → ${tsErr.message}\n⚠️ tsc failed — falling back to Judge0...`;
                }
            }

            // ── Tier 4: SQL — SQLite WASM (offline-capable) ──────────────────
            if (lang === 'SQL') {
                await this.runSqlJs(code);
                return;
            }

            // ── Tier 5: Visual Python — matplotlib/turtle via Pyodide → preview ─
            if (lang === 'Python' && this.isVisualPython(code)) {
                switchView('terminal', false);
                terminalViewBody.textContent = "⏳ Loading Python + graphics packages (~15 MB first load)...";
                terminalStatus.textContent = "RUNNING";
                terminalStatus.className = "text-[#74a896] font-bold animate-pulse";
                try {
                    const result = await this.runPyodideVisual(code);
                    if (result.images.length > 0) {
                        this.renderPyVisualOutput(result.images, result.stdout, result.stderr);
                        return;
                    }
                    this.showRunResult(result.stdout, result.stderr, lang);
                    return;
                } catch(e: any) {
                    terminalViewBody.textContent += `\n⚠️ Visual Python failed: ${e.message}\n   Falling back to API execution...`;
                }
            }

            // ── Tier 6: Judge0 CE — real compilers, online ────────────────────
            terminalViewBody.textContent = `🌐 ${actionLabel}\n   Connecting to Judge0...`;
            const j0 = await this.runJudge0(lang, code);
            if (j0) {
                this.showRunResult(j0.stdout, j0.stderr, lang, { compiler: meta.runtime });
                return;
            }

            // ── Tier 7: Piston cluster — compiled + interpreted, online ────────
            terminalViewBody.textContent = `⚠️ Judge0 unreachable — trying Piston...\n   ${actionLabel}`;
            const piston = await this.runPistonDirect(lang, code, p);
            if (piston) {
                this.showRunResult(piston.stdout, piston.stderr, lang);
                return;
            }

            // ── Tier 8: WASM offline runtimes — last resort ───────────────────
            const wasmKey = meta.wasm;
            const wasmRunners: Record<string, () => Promise<RunResult>> = {
                'pyodide':  () => this.runPyodide(code),
                'php-wasm': () => this.runPhpWasm(code),
                'wasmoon':  () => this.runLuaWasm(code),
                'opal':     () => this.runRubyOpal(code),
            };
            if (wasmKey && wasmRunners[wasmKey]) {
                terminalViewBody.textContent = `⚠️ All APIs unreachable — loading offline WASM runtime...\n   ${actionLabel}`;
                try {
                    const res = await wasmRunners[wasmKey]();
                    this.showRunResult(res.stdout, res.stderr, lang);
                    return;
                } catch (e: any) {
                    terminalViewBody.textContent += `\n⚠️ WASM runtime failed: ${e.message}`;
                }
            }

            // All tiers exhausted
            terminalStatus.textContent = "ALL RUNTIMES OFFLINE";
            terminalStatus.className = "text-rose-500 font-bold";
            terminalViewBody.textContent = this.formatSimpleReport({
                lineNo: "—", errorMsg: "All execution engines unreachable",
                likelyCause: `JS/HTML run locally; TypeScript compiles in-browser; SQL uses SQLite WASM. All API endpoints (Judge0, Piston) are unreachable, and ${lang} has no offline WASM runtime.`,
                suggestion: "Check network connectivity or try a different language. JavaScript, TypeScript, HTML, and SQL always work offline."
            });

        } catch (globalErr: any) { this.handleGlobalFailure(globalErr); }
        terminalViewBody.scrollTop = terminalViewBody.scrollHeight;
    }

    // ── Visual output detection ───────────────────────────────────────────────
    static isVisualCode(code: string): boolean {
        return /\b(document\.|window\.(onload|addEventListener)|getElementById|querySelector|innerHTML|appendChild|createElement|canvas|getContext|ctx\.|requestAnimationFrame|body\.style|drawImage|fillRect|clearRect|strokeRect|beginPath|arc\(|lineTo|moveTo)\b/.test(code);
    }

    static isVisualPython(code: string): boolean {
        return /\b(matplotlib|pyplot|plt\s*\.|seaborn|plotly|bokeh|turtle\s*\.|Turtle|pygame|PIL|Image\.open|cv2\.|imshow|savefig|show\(\)|scatter\(|plot\(|bar\(|pie\(|hist\()\b/.test(code);
    }

    // ── Render JS/TS in preview iframe with full DOM access ──────────────────
    static renderJSPreview(jsCode: string): void {
        const doc = (previewFrame as HTMLIFrameElement).contentDocument || ((previewFrame as HTMLIFrameElement).contentWindow as any).document;
        const escaped = jsCode.replace(/<\/script>/gi, '<\\/script>');
        doc.open();
        doc.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{margin:0;background:#fff;font-family:sans-serif;}</style></head><body>
<script>
window.onerror=function(m,s,l,c,e){if(window.parent&&window.parent.handleIframeError)window.parent.handleIframeError(m,s,l,c);return true;};
${escaped}
<\/script></body></html>`);
        doc.close();
        switchView('preview');
        terminalStatus.textContent = "PREVIEW";
        terminalStatus.className = "text-emerald-400 font-bold";
        JungleUI.showToast("Visual output shown in Preview panel.", null);
    }

    // ── Pyodide visual: run matplotlib/turtle code, capture PNG images ────────
    static async runPyodideVisual(code: string): Promise<{ images: string[]; stdout: string; stderr: string }> {
        if (!(window as any)._pyodide) {
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/pyodide.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
            (window as any)._pyodide = await (window as any).loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/' });
        }
        const py = (window as any)._pyodide;
        terminalViewBody.textContent = "⏳ Installing graphics packages...";
        await py.loadPackagesFromImports(code);
        const out: string[] = [], err: string[] = [];
        py.setStdout({ batched: (s: string) => out.push(s) });
        py.setStderr({ batched: (s: string) => err.push(s) });
        const wrapper = `
import sys as _sys_j
import io as _io_j, base64 as _b64_j
_jngl_imgs = []
_jngl_stderr = []

try:
    import matplotlib as _mpl_j
    _mpl_j.use('agg')
    import matplotlib.pyplot as _plt_j
except Exception: pass

try:
${code.split('\n').map((l: string) => '    ' + l).join('\n')}
except Exception as _e_j:
    _jngl_stderr.append(str(_e_j))

try:
    import matplotlib.pyplot as _plt_j2
    for _fig_i in _plt_j2.get_fignums():
        _fig = _plt_j2.figure(_fig_i)
        _buf = _io_j.BytesIO()
        _fig.savefig(_buf, format='png', bbox_inches='tight', dpi=120)
        _buf.seek(0)
        _jngl_imgs.append(_b64_j.b64encode(_buf.read()).decode('utf-8'))
    _plt_j2.close('all')
except Exception: pass
`;
        try {
            await py.runPythonAsync(wrapper);
            const rawImgs = py.globals.get('_jngl_imgs');
            const rawErrs = py.globals.get('_jngl_stderr');
            const images: string[] = rawImgs ? rawImgs.toJs() : [];
            const pyErrs: string = rawErrs ? rawErrs.toJs().join('\n') : '';
            rawImgs && rawImgs.destroy && rawImgs.destroy();
            rawErrs && rawErrs.destroy && rawErrs.destroy();
            return { images, stdout: out.join('\n'), stderr: pyErrs || err.join('\n') };
        } catch(e: any) {
            return { images: [], stdout: out.join('\n'), stderr: e.message || String(e) };
        }
    }

    // ── Render matplotlib PNG images + stdout in preview iframe ──────────────
    static renderPyVisualOutput(images: string[], stdout: string, stderr: string): void {
        const imgTags = images.map(b64 =>
            `<img src="data:image/png;base64,${b64}" style="max-width:100%;display:block;margin:20px auto;border-radius:6px;box-shadow:0 4px 20px rgba(0,0,0,0.4);">`
        ).join('');
        const stdoutHtml = stdout.trim()
            ? `<pre style="margin:16px;padding:14px 16px;background:#111b16;color:#aed9cb;font-family:monospace;font-size:13px;border-radius:6px;white-space:pre-wrap;">${stdout.trim().replace(/</g,'&lt;').replace(/>/g,'&gt;')}</pre>`
            : '';
        const stderrHtml = stderr.trim()
            ? `<pre style="margin:16px;padding:14px 16px;background:#1c0d0d;color:#ff9999;font-family:monospace;font-size:13px;border-radius:6px;white-space:pre-wrap;">${stderr.trim().replace(/</g,'&lt;').replace(/>/g,'&gt;')}</pre>`
            : '';
        const doc = (previewFrame as HTMLIFrameElement).contentDocument || ((previewFrame as HTMLIFrameElement).contentWindow as any).document;
        doc.open();
        doc.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{margin:0;background:#0f1a15;min-height:100vh;}h4{color:#74a896;font-family:sans-serif;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin:20px 20px 8px;opacity:0.6;}</style></head><body>
${images.length > 0 ? '<h4>Plot Output</h4>' + imgTags : ''}
${stdoutHtml ? '<h4>Print Output</h4>' + stdoutHtml : ''}
${stderrHtml ? '<h4>Errors</h4>' + stderrHtml : ''}
</body></html>`);
        doc.close();
        switchView('preview');
        terminalStatus.textContent = "SUCCESS";
        terminalStatus.className = "text-emerald-400 font-bold";
        JungleUI.showToast("Plot rendered in Preview panel.", null);
    }

    // ── TypeScript in-browser compilation via CDN tsc ─────────────────────────
    static async compileTypeScript(code: string): Promise<string> {
        if (!(window as any).ts) {
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://cdn.jsdelivr.net/npm/typescript@5/lib/typescript.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
        }
        const ts = (window as any).ts;
        const result = ts.transpileModule(code, {
            compilerOptions: {
                target: ts.ScriptTarget.ES2020,
                module: ts.ModuleKind.None,
                strict: false,
                esModuleInterop: true,
            },
            reportDiagnostics: true,
        });
        if (result.diagnostics && result.diagnostics.length > 0) {
            const errs = result.diagnostics.map((d: any) => {
                const pos = d.file ? d.file.getLineAndCharacterOfPosition(d.start) : null;
                const line = pos ? ` (line ${pos.line + 1})` : '';
                return ts.flattenDiagnosticMessageText(d.messageText, '\n') + line;
            }).join('\n');
            throw new Error(errs);
        }
        return result.outputText;
    }

    // ── Native JS execution via sandboxed iframe + postMessage ─────────────────
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
                    resolve({ stdout: output.join('\n'), stderr: e.data.err || '', errName: e.data.errName || '', errStack: e.data.errStack || '' });
                }
            };
            window.addEventListener('message', handler);
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
            const wrap = (fn: string) => `(...a)=>{try{parent.postMessage({__jOut:true,t:[...a].map(x=>typeof x==='object'?JSON.stringify(x):String(x)).join(' ')},'*')}catch(e){}}`;
            iframe.srcdoc = `<!DOCTYPE html><html><body><script>
const console={log:${wrap('log')},info:${wrap('info')},warn:(...a)=>parent.postMessage({__jOut:true,t:'WARN: '+[...a].join(' ')},'*'),error:(...a)=>parent.postMessage({__jOut:true,t:'ERROR: '+[...a].join(' ')},'*'),dir:${wrap('dir')},table:${wrap('table')}};
window.onerror=function(msg,src,line,col,err){parent.postMessage({__jDone:true,err:err?err.toString():msg,errName:err?err.name:'Error',errStack:err?err.stack:'',errLine:line,errCol:col},'*');return true;};
window.onunhandledrejection=function(ev){var err=ev.reason||{};parent.postMessage({__jDone:true,err:err.toString?err.toString():String(err),errName:err.name||'UnhandledPromiseRejection',errStack:err.stack||''},'*');};
try{${code.replace(/<\/script>/gi,'<\\/script>')}\nparent.postMessage({__jDone:true,err:'',errName:'',errStack:''},'*');}catch(e){parent.postMessage({__jDone:true,err:e.toString(),errName:e.name||'Error',errStack:e.stack||''},'*');}
<\/script></body></html>`;
            const timer = setTimeout(() => {
                window.removeEventListener('message', handler);
                iframe.remove();
                resolve({ stdout: output.join('\n'), stderr: 'Execution timed out after 10s\nHint: Check for infinite loops (e.g. while(true) or a loop with no exit condition).', errName: 'TimeoutError', errStack: '' });
            }, 10000);
        });
    }

    // ── Pyodide — Python WASM (offline fallback) ──────────────────────────────
    static async runPyodide(code: string): Promise<RunResult> {
        if (!(window as any)._pyodide) {
            terminalViewBody.textContent = "⏳ Loading Python WASM (~10 MB, cached after first load)...";
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/pyodide.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
            (window as any)._pyodide = await (window as any).loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/' });
        }
        const py = (window as any)._pyodide;
        const out: string[] = [], err: string[] = [];
        py.setStdout({ batched: (s: string) => out.push(s) });
        py.setStderr({ batched: (s: string) => err.push(s) });
        try { await py.runPythonAsync(code); }
        catch (e: any) { err.push(e.message); }
        return { stdout: out.join('\n'), stderr: err.join('\n') };
    }

    // ── php-wasm — PHP 8 WASM (offline fallback) ──────────────────────────────
    static async runPhpWasm(code: string): Promise<RunResult> {
        if (!(window as any)._phpWasm) {
            terminalViewBody.textContent = "⏳ Loading PHP 8 WASM (~10 MB, cached after first load)...";
            const mod = await import('https://cdn.jsdelivr.net/npm/php-wasm/PhpWeb.mjs' as any);
            (window as any)._phpWasm = mod.PhpWeb;
        }
        return new Promise(async resolve => {
            const php = new (window as any)._phpWasm();
            const out: string[] = [], err: string[] = [];
            php.addEventListener('output', (e: any) => out.push(...e.detail));
            php.addEventListener('error',  (e: any) => err.push(...e.detail));
            const src = code.trim().startsWith('<?') ? code : `<?php\n${code}`;
            try { await php.run(src); } catch(e: any) { err.push(e.message); }
            resolve({ stdout: out.join(''), stderr: err.join('') });
        });
    }

    // ── wasmoon — Lua 5.4 WASM (offline fallback) ────────────────────────────
    static async runLuaWasm(code: string): Promise<RunResult> {
        if (!(window as any)._luaFactory) {
            terminalViewBody.textContent = "⏳ Loading Lua WASM (~1 MB, cached after first load)...";
            const mod = await import('https://cdn.jsdelivr.net/npm/wasmoon@1.16.0/+esm' as any);
            (window as any)._luaFactory = new mod.LuaFactory('https://unpkg.com/wasmoon@1.16.0/dist/glue.wasm');
        }
        const out: string[] = [], err: string[] = [];
        const lua = await (window as any)._luaFactory.createEngine();
        lua.global.set('print', (...a: any[]) => out.push(a.map(String).join('\t')));
        try { await lua.doString(code); }
        catch (e: any) { err.push(e.message); }
        lua.global.close();
        return { stdout: out.join('\n'), stderr: err.join('\n') };
    }

    // ── Opal — Ruby → JS transpiler (offline fallback) ───────────────────────
    static async runRubyOpal(code: string): Promise<RunResult> {
        if (!(window as any).Opal) {
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
                s.onload = () => { (window as any).Opal.load('opal-parser'); res(); };
                s.onerror = rej;
                document.head.appendChild(s);
            });
        }
        const out: string[] = [];
        try {
            (window as any).Opal.gvars['$stdout'] = { write: (s: string) => { out.push(s); return s.length; }, puts: (s: string) => { out.push(s + '\n'); } };
            (window as any).Opal.eval(code);
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
        if (!(window as any)._sqlJs) {
            terminalViewBody.textContent = "⏳ Loading SQLite WASM (~1 MB, cached after first load)...";
            await new Promise((res, rej) => {
                const s = document.createElement('script');
                s.src = 'https://sql.js.org/dist/sql-wasm.js';
                s.onload = res; s.onerror = rej;
                document.head.appendChild(s);
            });
            (window as any)._sqlJs = await (window as any).initSqlJs({ locateFile: (f: string) => `https://sql.js.org/dist/${f}` });
        }
        try {
            const db = new (window as any)._sqlJs.Database();
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

    // ── Judge0 CE — real compilers, 35+ languages ─────────────────────────────
    static async runJudge0(lang: string, code: string): Promise<RunResult | null> {
        const meta = this.LANG_META[lang];
        const id = meta && meta.judge0;
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

    // ── Piston — returns {stdout, stderr} or null ─────────────────────────────
    static async runPistonDirect(lang: string, code: string, p: Project): Promise<RunResult | null> {
        const meta = this.LANG_META[lang];
        const pistonLang = (meta && meta.piston) || lang.toLowerCase();
        if (!pistonLang) return null;
        const filesArray: Array<{ name: string; content: string }> = [{ name: p.currentFile || 'main', content: code }];
        Object.keys(p.files).forEach(f => { if (f !== p.currentFile) filesArray.push({ name: f, content: p.files[f] }); });
        const payload = { language: pistonLang, version: '*', files: filesArray };
        const e1 = 'https://emkc.org/api/v2/piston/execute';
        const e2 = 'https://piston.engineering.purdue.edu/api/v2/piston/execute';
        const enc = encodeURIComponent;
        const endpoints: Array<{ url: string; raw?: boolean }> = [
            { url: e1 },
            { url: e2 },
            { url: `https://corsproxy.io/?${e1}` },
            { url: `https://corsproxy.io/?${e2}` },
            { url: `https://api.allorigins.win/raw?url=${enc(e1)}`, raw: true },
            { url: `https://cors-anywhere.herokuapp.com/${e1}` },
            { url: `https://thingproxy.freeboard.io/fetch/${e1}` },
        ];
        for (const ep of endpoints) {
            try {
                const res = await fetch(ep.url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = ep.raw ? JSON.parse(await res.text()) : await res.json();
                if (data && data.run) return { stdout: data.run.stdout || '', stderr: data.run.stderr || '' };
            } catch(_) {}
        }
        return null;
    }

    // ── Shared result display ─────────────────────────────────────────────────
    static showRunResult(stdout: string, stderr: string, lang: string, meta: RunMeta = {}): void {
        const hasFail = stderr && stderr.trim();
        terminalViewBody.textContent = '';
        if (hasFail) {
            const details = this.parseError(stderr, stdout, lang, meta);
            this.printCrashAnalysis(details, stdout, stderr);
            JungleUI.showToast("❌ Runtime error — tap to inspect.", () => switchView('terminal', false));
            terminalStatus.textContent = "FAILED TO RUN";
            terminalStatus.className = "text-rose-500 font-bold";
        } else {
            const langMeta = this.LANG_META[lang] || {} as LangMeta;
            const compiler = meta.compiler || langMeta.runtime || '';
            const header = compiler ? `✓ ${langMeta.compiled ? 'Compiled & ran' : 'Ran'}  [${compiler}]\n${'─'.repeat(46)}\n` : '';
            terminalViewBody.textContent = header + (stdout || "✓ Ran successfully — no output.");
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

    static parseError(stderr: string, stdout: string, lang: string, meta?: RunMeta): ErrorDetails {
        let errorMsg = "Execution anomaly detected.", lineNo: string | number = "Unknown line", file = "main";
        let column: string | number | null = null, likelyCause = "", suggestion = "", errorType = "";
        const combined = (stderr || "") + "\n" + (stdout || "");
        const lines = combined.trim().split('\n').filter(Boolean);

        if (/execution timed out/i.test(combined)) {
            errorMsg = "Execution timed out after 10 seconds.";
            errorType = "Timeout";
            const insight = this.explainError("timeout", lang, combined);
            return { errorMsg, lineNo: "—", file, column, likelyCause: insight.likelyCause, suggestion: "Check for infinite loops (while(true), for(;;), or a recursive call with no base case). Add a break condition.", rawOutput: combined.trim(), errorType };
        }

        if (lang === 'Python') {
            const frameMatches = [...combined.matchAll(/File\s+"([^"]+)",\s+line\s+(\d+)/gi)];
            if (frameMatches.length > 0) { const last = frameMatches[frameMatches.length - 1]; file = last[1]; lineNo = last[2]; }
            for (let i = lines.length - 1; i >= 0; i--) {
                const l = lines[i].trim();
                const errMatch = l.match(/^([A-Za-z][A-Za-z0-9_]*(?:Error|Exception|Warning|Interrupt|Stop))\s*:\s*(.*)/);
                if (errMatch) { errorType = errMatch[1]; errorMsg = l; break; }
                if (l.includes('Error:') || l.includes('Exception:')) { errorMsg = l; break; }
            }
            if (errorMsg === "Execution anomaly detected." && lines.length > 0) errorMsg = lines[lines.length - 1];
            if (!errorType) { const tm = errorMsg.match(/^([A-Za-z][A-Za-z0-9_]*(?:Error|Exception))/); if (tm) errorType = tm[1]; }
        } else if (lang === 'Javascript' || lang === 'TypeScript') {
            const errName = (meta && meta.errName) || '';
            const errStack = (meta && meta.errStack) || '';
            errorType = errName || '';
            if (lines[0]) errorMsg = lines[0];
            const stackLines = (errStack || combined).split('\n');
            for (const sl of stackLines) {
                const m = sl.match(/at\s+.*?(?:<anonymous>|evalmachine\.__toString__|eval):(\d+):(\d+)/) ||
                          sl.match(/at\s+.*?:(\d+):(\d+)/);
                if (m) { lineNo = m[1]; column = m[2]; file = "main.js"; break; }
            }
            if (lineNo === "Unknown line") {
                const match = combined.match(/\/([^/:\s]+):(\d+):(\d+)/) || combined.match(/(?:^|\n)([^:\n]+):(\d+):(\d+)/);
                if (match) { file = match[1] || "main.js"; lineNo = match[2]; column = match[3]; }
            }
            if (errName && errorMsg) { const msgBody = errorMsg.replace(/^[A-Za-z][A-Za-z0-9_]*Error:\s*/i, ''); errorMsg = `${errName}: ${msgBody}`; }
        } else if (lang === 'C++' || lang === 'C' || lang === 'Rust' || lang === 'Go' || lang === 'Java' || lang === 'Kotlin' || lang === 'Swift') {
            const match = combined.match(/([^:\n]+):(\d+):(?:(\d+):)?\s+(?:fatal\s+)?(?:error|Error):\s+(.+)/i);
            if (match) { file = match[1]; lineNo = match[2]; column = match[3] || null; errorMsg = match[4]; errorType = "CompileError"; }
            if (lang === 'Java' || lang === 'Kotlin') {
                const exception = combined.match(/Exception in thread "[^"]+"\s+([^\n]+)/i);
                const frame = combined.match(/\bat\s+.*\(([^():]+):(\d+)\)/);
                if (exception) { errorMsg = exception[1].trim(); const em = errorMsg.match(/^([A-Za-z.]+Exception)/); if (em) errorType = em[1].split('.').pop() || ''; }
                if (frame) { file = frame[1]; lineNo = frame[2]; }
            }
            if (lang === 'Rust') {
                const rustMatch = combined.match(/error(?:\[E\d+\])?\s*:\s*([^\n]+)/);
                if (rustMatch) { errorMsg = rustMatch[1]; errorType = "CompileError"; }
                const rustLine = combined.match(/--> [^:]+:(\d+):(\d+)/);
                if (rustLine) { lineNo = rustLine[1]; column = rustLine[2]; }
            }
        } else {
            const generic = combined.match(/([^:\n]+):(\d+):(?:(\d+):)?\s*(.+)/);
            if (generic) { file = generic[1]; lineNo = generic[2]; column = generic[3] || null; errorMsg = generic[4]; }
            else if (lines.length > 0) errorMsg = lines[0];
        }
        const insight = this.explainError(errorMsg, lang, combined);
        likelyCause = insight.likelyCause;
        suggestion = insight.suggestion;
        return { errorMsg, lineNo, file, column, likelyCause, suggestion, rawOutput: combined.trim(), errorType };
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
            { test: /unicode|encoding|decode/i, cause: "A string or file contains characters that could not be decoded with the current encoding.", fix: "Specify an encoding explicitly (e.g. open(file, encoding='utf-8')) or sanitize the input." },
            { test: /borrow|lifetime|ownership/i, cause: "Rust's borrow checker rejected an ownership or lifetime constraint.", fix: "Review the borrow rules: only one mutable reference or many immutable references can exist at once." },
            { test: /linker|undefined reference|unresolved external/i, cause: "The linker could not find a function or symbol referenced in the code.", fix: "Check that all required libraries are linked and all function definitions are present." },
            { test: /null pointer|nullpointerexception/i, cause: "The program dereferenced a null or uninitialized pointer.", fix: "Initialize pointers before use and check for null before dereferencing." },
        ];
        const matched = rules.find(rule => rule.test.test(text));
        if (matched) return { likelyCause: matched.cause, suggestion: matched.fix };
        if (lang === 'Python') return { likelyCause: "Python raised an exception while executing the script.", suggestion: "Read the last traceback line first, then inspect the reported source line." };
        if (lang === 'Javascript' || lang === 'TypeScript') return { likelyCause: "The JavaScript runtime stopped on an exception.", suggestion: "Check the first error line and the top stack frame that points into your file." };
        if (lang === 'C++' || lang === 'C') return { likelyCause: "The compiler or runtime rejected the native program.", suggestion: "Start with the first compiler error; later errors are often side effects." };
        if (lang === 'Rust') return { likelyCause: "The Rust compiler rejected the program.", suggestion: "Read the first error carefully — Rust error messages include detailed explanations and fix suggestions." };
        if (lang === 'Java' || lang === 'Kotlin') return { likelyCause: "The JVM compiler or runtime stopped because of the reported error.", suggestion: "Verify the class name, method signatures, and the first reported line." };
        if (lang === 'Go') return { likelyCause: "The Go compiler rejected the program or the binary panicked at runtime.", suggestion: "Check the first compiler error; Go errors are precise and usually point directly at the issue." };
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
            if (i === lineNumber && column) frame.push(`       | ${" ".repeat(Math.max(0, Number(column) - 1))}^`);
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
        const errorKind = details.errorType || this.getSimpleErrorKind(details.errorMsg || "");
        const message = this.simplifyErrorMessage(details.errorMsg || "unknown error");
        const icon = this.severityIcon(details.severity || "");
        const typeLabel = details.errorType ? `[${details.errorType}] ` : '';
        let out = `${icon} ${typeLabel}Error on Line ${lineNo} — ${errorKind}\n   ${message}`;
        if (details.likelyCause) out += `\n\nLikely cause: ${details.likelyCause}`;
        if (details.suggestion) out += `\nSuggestion:   ${details.suggestion}`;
        return out;
    }

    static formatTraceback(stderr: string): string {
        if (!stderr || !stderr.trim()) return '';
        const lines = stderr.trim().split('\n');
        const out: string[] = [];
        for (const line of lines) {
            const trimmed = line.trim();
            if (/^File\s+"[^"]+",\s+line\s+\d+/.test(trimmed)) out.push('  → ' + trimmed);
            else if (/^[A-Za-z][A-Za-z0-9_]*(?:Error|Exception|Warning|Interrupt|Stop)\s*:/.test(trimmed)) out.push('  !! ' + trimmed);
            else if (/^Traceback\s+\(most recent call last\)/i.test(trimmed)) out.push('  ' + trimmed);
            else out.push('     ' + line);
        }
        return out.join('\n');
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
        if (/borrow|lifetime|ownership/.test(text)) return "Borrow error";
        if (/linker|undefined reference|unresolved/.test(text)) return "Linker error";
        return "Error";
    }

    static simplifyErrorMessage(message: string): string {
        let text = String(message || "unknown error").trim();
        if (/Unexpected end of input/i.test(text)) return "unexpected end of input";
        const closingBracket = text.match(/(?:Unexpected token|unexpected|Mismatched closing bracket)\s*['"`]?([}\])])['"`]?/i);
        if (closingBracket) return `unexpected ${closingBracket[1]}`;
        const unclosed = text.match(/Unclosed bracket or delimiter\s*['"`]?([({[])['"`]?/i);
        if (unclosed) { const closers: Record<string, string> = { '(': ')', '[': ']', '{': '}' }; return `missing ${closers[unclosed[1]] || unclosed[1]}`; }
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
        text = text.replace(/^syntaxerror:\s*/i, "").replace(/^error:\s*/i, "").replace(/^typeerror:\s*/i, "").replace(/^referenceerror:\s*/i, "").replace(/^nameerror:\s*/i, "").replace(/^valueerror:\s*/i, "").replace(/^attributeerror:\s*/i, "").replace(/\s+/g, " ").replace(/[.。]+$/, "");
        return text || "unknown error";
    }

    static printCrashAnalysis(details: ErrorDetails, stdout: string, stderr: string): void {
        let output = this.formatSimpleReport(details);
        if (details.lineNo && details.lineNo !== "Unknown" && details.lineNo !== "—") {
            const frame = this.getCodeFrame(details.file || "", details.lineNo, details.column);
            if (frame) output += `\n\n${frame}`;
        }
        if (stderr && stderr.includes('\n')) {
            const formatted = this.formatTraceback(stderr);
            if (formatted) output += `\n\n─── Traceback ───\n${formatted}`;
        }
        if (stdout && stdout.trim()) output += `\n\n─── Program output before crash ───\n${stdout.trim()}`;
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
