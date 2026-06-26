import type { ProjectFile } from '../types';

// Language → display label
const LANG_LABEL: Record<string, string> = {
  html: 'HTML',
  css: 'CSS',
  javascript: 'JS',
  typescript: 'TS',
  python: 'PY',
  json: 'JSON',
};

// Language → icon
const LANG_ICON: Record<string, string> = {
  html: 'fa-code',
  css: 'fa-palette',
  javascript: 'fa-js',
  typescript: 'fa-code',
  python: 'fa-python',
  json: 'fa-brackets-curly',
};

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fileIcon(lang: string): string {
  const icon = LANG_ICON[lang] ?? 'fa-file-code';
  return `<i class="fa-brands ${icon} text-[9px]"></i>`;
}

function langBadge(lang: string): string {
  return LANG_LABEL[lang] ?? lang.toUpperCase();
}

/** Stitch multi-file project into a single runnable HTML document. */
export function stitchProject(files: ProjectFile[]): string {
  const html = files.find(f => f.name.endsWith('.html'));
  const css  = files.find(f => f.name.endsWith('.css'));
  const js   = files.find(f => f.name.endsWith('.js') || f.name.endsWith('.ts'));

  if (!html) {
    // Fallback: just the first file content
    return files[0]?.content ?? '';
  }

  let doc = html.content;

  // Inject CSS inline before </head> (or at top if no head)
  if (css) {
    const styleTag = `<style>\n${css.content}\n</style>`;
    if (doc.includes('</head>')) {
      doc = doc.replace('</head>', `${styleTag}\n</head>`);
    } else {
      doc = styleTag + '\n' + doc;
    }
    // Remove the <link rel="stylesheet"> reference
    doc = doc.replace(/<link\s[^>]*rel=["']stylesheet["'][^>]*>/gi, '');
  }

  // Inject JS inline before </body> (or at end)
  if (js) {
    const scriptTag = `<script>\n${js.content}\n</script>`;
    if (doc.includes('</body>')) {
      doc = doc.replace('</body>', `${scriptTag}\n</body>`);
    } else {
      doc = doc + '\n' + scriptTag;
    }
    // Remove the <script src="..."> reference
    doc = doc.replace(/<script\s[^>]*src=["'][^"']*["'][^>]*><\/script>/gi, '');
  }

  return doc;
}

/** Build a file-viewer element and return it. */
export function buildFileViewer(
  files: ProjectFile[],
  kind: 'game' | 'app' | string,
): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'file-viewer my-4 bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-lg font-mono text-[11px]';

  // ── Header: Explorer label + Run button ──
  const isGame = kind === 'game';
  const runLabel = isGame ? 'Play Game' : 'Run Project';
  const runIcon  = isGame ? 'fa-gamepad' : 'fa-rocket';
  const runColor = isGame ? 'text-indigo-400 border-indigo-500/30 bg-indigo-950/20 hover:text-white hover:border-indigo-400/50' : 'text-emerald-400 border-emerald-500/30 bg-emerald-950/20 hover:text-white hover:border-emerald-400/50';

  const header = document.createElement('div');
  header.className = 'bg-slate-950/60 px-4 py-2.5 border-b border-slate-800 flex justify-between items-center';
  header.innerHTML = `
    <div class="flex items-center space-x-2 text-slate-400">
      <i class="fa-solid fa-folder-open text-[10px] text-slate-500"></i>
      <span class="text-[10px] font-bold tracking-wider uppercase text-slate-500">Project Files</span>
      <span class="text-slate-700 text-[10px]">${files.length} file${files.length !== 1 ? 's' : ''}</span>
    </div>
    <div class="flex items-center space-x-2">
      <button class="btn-copy-all font-semibold transition flex items-center space-x-1.5 border border-slate-800 bg-slate-950/40 px-2 py-1 rounded text-slate-400 hover:text-white text-[9px]">
        <i class="fa-regular fa-copy text-[10px]"></i><span>Copy All</span>
      </button>
      <button class="btn-run font-semibold transition flex items-center space-x-1.5 border px-2.5 py-1 rounded-md ${runColor} text-[9px]">
        <i class="fa-solid ${runIcon} text-[10px]"></i><span>${runLabel}</span>
      </button>
    </div>`;
  wrap.appendChild(header);

  // ── Tab bar ──
  const tabBar = document.createElement('div');
  tabBar.className = 'flex items-end border-b border-slate-800 bg-slate-950/30 overflow-x-auto';

  files.forEach((file, idx) => {
    const tab = document.createElement('button');
    tab.dataset.idx = String(idx);
    tab.className = [
      'tab-btn flex items-center space-x-1.5 px-3 py-2 text-[10px] font-medium border-b-2 transition shrink-0',
      idx === 0
        ? 'text-slate-200 border-indigo-500 bg-slate-900/60'
        : 'text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/30',
    ].join(' ');
    tab.innerHTML = `
      ${fileIcon(file.language)}
      <span>${escapeHtml(file.name)}</span>
      <span class="text-[8px] font-bold text-slate-600 ml-0.5">${langBadge(file.language)}</span>`;
    tabBar.appendChild(tab);
  });
  wrap.appendChild(tabBar);

  // ── Code panels ──
  const panels: HTMLElement[] = files.map((file, idx) => {
    const panel = document.createElement('div');
    panel.dataset.panelIdx = String(idx);
    panel.className = idx === 0 ? '' : 'hidden';
    panel.innerHTML = `<pre class="p-4 overflow-x-auto text-slate-200 leading-normal max-h-[420px] overflow-y-auto"><code>${escapeHtml(file.content)}</code></pre>`;
    return panel;
  });
  panels.forEach(p => wrap.appendChild(p));

  // ── Footer: copy active file ──
  const footer = document.createElement('div');
  footer.className = 'bg-slate-950/30 border-t border-slate-800 px-4 py-1.5 flex items-center justify-between';
  footer.innerHTML = `
    <span class="active-file-label text-[9px] text-slate-600">${escapeHtml(files[0]?.name ?? '')}</span>
    <button class="btn-copy-file text-[9px] font-medium text-slate-500 hover:text-white transition flex items-center space-x-1">
      <i class="fa-regular fa-copy text-[10px]"></i><span>Copy File</span>
    </button>`;
  wrap.appendChild(footer);

  // ── Wire up tab switching ──
  let activeIdx = 0;
  const tabs = Array.from(tabBar.querySelectorAll<HTMLElement>('.tab-btn'));

  function switchTab(idx: number): void {
    activeIdx = idx;
    tabs.forEach((t, i) => {
      if (i === idx) {
        t.classList.add('text-slate-200', 'border-indigo-500', 'bg-slate-900/60');
        t.classList.remove('text-slate-500', 'border-transparent', 'hover:text-slate-300', 'hover:bg-slate-800/30');
      } else {
        t.classList.remove('text-slate-200', 'border-indigo-500', 'bg-slate-900/60');
        t.classList.add('text-slate-500', 'border-transparent', 'hover:text-slate-300', 'hover:bg-slate-800/30');
      }
    });
    panels.forEach((p, i) => p.classList.toggle('hidden', i !== idx));
    const label = footer.querySelector('.active-file-label');
    if (label) label.textContent = files[idx]?.name ?? '';
  }

  tabs.forEach((tab, idx) => tab.addEventListener('click', () => switchTab(idx)));

  // ── Copy file ──
  footer.querySelector('.btn-copy-file')?.addEventListener('click', () => {
    const content = files[activeIdx]?.content ?? '';
    navigator.clipboard.writeText(content).catch(() => {});
  });

  // ── Copy all ──
  header.querySelector('.btn-copy-all')?.addEventListener('click', () => {
    const all = files.map(f => `/* ===== ${f.name} ===== */\n${f.content}`).join('\n\n');
    navigator.clipboard.writeText(all).catch(() => {});
  });

  // ── Run project ──
  header.querySelector('.btn-run')?.addEventListener('click', () => {
    const doc = stitchProject(files);
    const modal = document.getElementById('sandboxModal');
    const frame = document.getElementById('sandboxFrame') as HTMLIFrameElement | null;
    if (modal && frame) {
      modal.classList.remove('hidden');
      frame.srcdoc = doc;
    }
  });

  return wrap;
}
