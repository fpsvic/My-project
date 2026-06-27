import type { ProjectFile } from '../types';

// Re-export stitchProject locally so we don't import fileViewer (avoid circular)
function stitchProject(files: ProjectFile[]): string {
  const html   = files.find(f => f.name === 'index.html');
  const css    = files.find(f => f.language === 'css');
  const js     = files.find(f => f.language === 'javascript');
  if (!html) return '';
  let out = html.content;
  if (css) {
    out = out.replace(/<link[^>]*stylesheet[^>]*>/gi, '');
    out = out.replace('</head>', `<style>${css.content}</style></head>`);
  }
  if (js) {
    out = out.replace(/<script\s+src=["'][^"']+["'][^>]*><\/script>/gi, '');
    out = out.replace('</body>', `<script>${js.content}</script></body>`);
  }
  return out;
}

let _files: ProjectFile[] = [];
let _activeIdx = 0;
let _title = '';
let _kind = 'app';

export function initCodePanel(): void {
  document.getElementById('btnClosePanel')?.addEventListener('click', closeCodePanel);
  document.getElementById('btnPanelRun')?.addEventListener('click', _runProject);
  document.getElementById('btnPanelCopy')?.addEventListener('click', _copyFile);
}

export function showProjectInPanel(files: ProjectFile[], title: string, kind: string): void {
  _files = files;
  _activeIdx = 0;
  _title = title;
  _kind = kind;
  _render();
  _openPanel();
}

export function closeCodePanel(): void {
  document.getElementById('codePanel')?.classList.remove('panel-open');
}

function _openPanel(): void {
  document.getElementById('codePanel')?.classList.add('panel-open');
}

function _render(): void {
  _renderHeader();
  _renderTabs();
  _renderTree();
  _renderContent();
  _renderStats();
}

function _renderHeader(): void {
  const t = document.getElementById('panelProjectTitle');
  const k = document.getElementById('panelProjectKind');
  if (t) t.textContent = _title;
  if (k) {
    k.textContent = _kind === 'game' ? 'Game' : 'App';
    k.className = _kind === 'game'
      ? 'text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0'
      : 'text-[9px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0';
  }
}

function _renderTabs(): void {
  const bar = document.getElementById('codePanelTabs');
  if (!bar) return;
  bar.innerHTML = '';
  _files.forEach((file, i) => {
    const btn = document.createElement('button');
    const active = i === _activeIdx;
    btn.className = [
      'flex items-center space-x-1.5 px-3 py-2 text-[10px] font-mono border-b-2 whitespace-nowrap transition shrink-0',
      active ? 'text-white border-indigo-400 bg-slate-800/40' : 'text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/20'
    ].join(' ');
    btn.innerHTML = `${_icon(file.language)}<span>${file.name}</span>`;
    btn.addEventListener('click', () => _selectFile(i));
    bar.appendChild(btn);
  });
}

function _renderTree(): void {
  const tree = document.getElementById('codePanelFileTree');
  if (!tree) return;
  tree.innerHTML = '';
  _files.forEach((file, i) => {
    const btn = document.createElement('button');
    const active = i === _activeIdx;
    const lines = file.content.split('\n').length;
    btn.className = [
      'w-full flex items-center space-x-1.5 px-2 py-1.5 text-[10px] font-mono text-left rounded transition',
      active ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/40 border border-transparent'
    ].join(' ');
    btn.innerHTML = `${_icon(file.language)}<span class="flex-1 truncate">${file.name}</span><span class="text-[8px] text-slate-700 ml-1">${lines}L</span>`;
    btn.addEventListener('click', () => _selectFile(i));
    tree.appendChild(btn);
  });
}

function _renderContent(): void {
  const el = document.getElementById('codePanelContent');
  if (!el) return;
  const file = _files[_activeIdx];
  if (!file) { el.innerHTML = ''; return; }

  // Simple syntax coloring via CSS classes on a <pre>
  const escaped = file.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Add line numbers
  const lines = escaped.split('\n');
  const numbered = lines.map((line, i) =>
    `<span class="select-none text-slate-700 inline-block w-8 text-right mr-3 text-[9px]">${i + 1}</span>${line}`
  ).join('\n');

  el.innerHTML = `<pre class="text-[11px] font-mono leading-relaxed text-slate-300 whitespace-pre">${numbered}</pre>`;
}

function _renderStats(): void {
  const el = document.getElementById('codePanelStats');
  const file = _files[_activeIdx];
  if (!el || !file) return;
  const lines = file.content.split('\n').length;
  const size = (new TextEncoder().encode(file.content).length / 1024).toFixed(1);
  el.textContent = `${file.name}  ·  ${lines} lines  ·  ${size} KB`;
}

function _selectFile(idx: number): void {
  _activeIdx = idx;
  _renderTabs();
  _renderTree();
  _renderContent();
  _renderStats();
}

function _icon(lang: string): string {
  const m: Record<string, string> = {
    html: '<i class="fa-brands fa-html5 text-orange-400 text-[9px] shrink-0"></i>',
    css:  '<i class="fa-brands fa-css3-alt text-blue-400 text-[9px] shrink-0"></i>',
    javascript: '<i class="fa-brands fa-js text-yellow-400 text-[9px] shrink-0"></i>',
  };
  return m[lang] ?? '<i class="fa-solid fa-file-code text-slate-500 text-[9px] shrink-0"></i>';
}

function _runProject(): void {
  if (!_files.length) return;
  const html = stitchProject(_files);
  const frame = document.getElementById('sandboxFrame') as HTMLIFrameElement | null;
  const modal = document.getElementById('sandboxModal');
  if (frame && modal) {
    frame.srcdoc = html;
    modal.classList.remove('hidden');
  }
}

function _copyFile(): void {
  const file = _files[_activeIdx];
  if (!file) return;
  navigator.clipboard.writeText(file.content).then(() => {
    const btn = document.getElementById('btnPanelCopy');
    if (!btn) return;
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check text-[9px]"></i><span>Copied!</span>';
    setTimeout(() => { btn.innerHTML = orig; }, 1500);
  });
}
