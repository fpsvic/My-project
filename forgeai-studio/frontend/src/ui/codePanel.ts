import type { ProjectFile } from '../types';
import { stitchProject } from './fileViewer';
import { openSandboxPreview } from './sandbox';

let _files: ProjectFile[] = [];
let _activeIdx = 0;
let _title = '';
let _kind = 'app';
let _ready = false;
let _sidebarCollapsed = false;

const SIDEBAR_KEY = 'forgeai_file_sidebar_collapsed';

export function initCodePanel(): void {
  document.getElementById('btnClosePanel')?.addEventListener('click', closeCodePanel);
  document.getElementById('btnPanelRun')?.addEventListener('click', _runProject);
  document.getElementById('btnPanelCopy')?.addEventListener('click', _copyFile);
  document.getElementById('btnToggleFileSidebar')?.addEventListener('click', _toggleFileSidebar);

  _sidebarCollapsed = localStorage.getItem(SIDEBAR_KEY) === '1';
  _applySidebarState();
}

export function showProjectInPanel(files: ProjectFile[], title: string, kind: string): void {
  _files = files.filter(f => f.name !== 'README.md');
  _activeIdx = 0;
  _title = title;
  _kind = kind;
  _ready = _files.length > 0;
  _render();
  _openPanel();
}

export function setCodePanelGenerating(): void {
  _files = [];
  _activeIdx = 0;
  _title = 'Generating...';
  _kind = 'app';
  _ready = false;
  _render();
  _openPanel();
  const content = document.getElementById('codePanelContent');
  if (content) {
    content.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full min-h-[200px] text-center px-6">
        <i class="fa-solid fa-circle-notch text-indigo-400 text-xl animate-spin mb-3"></i>
        <p class="text-sm text-slate-300 font-medium">Generating your code...</p>
        <p class="text-xs text-slate-500 mt-1">Preview will be available when generation finishes.</p>
      </div>`;
  }
  _setRunEnabled(false);
}

export function closeCodePanel(): void {
  document.getElementById('codePanel')?.classList.remove('panel-open');
}

function _openPanel(): void {
  document.getElementById('codePanel')?.classList.add('panel-open');
}

function _toggleFileSidebar(): void {
  _sidebarCollapsed = !_sidebarCollapsed;
  localStorage.setItem(SIDEBAR_KEY, _sidebarCollapsed ? '1' : '0');
  _applySidebarState();
}

function _applySidebarState(): void {
  const sidebar = document.getElementById('codePanelFileSidebar');
  const btn = document.getElementById('btnToggleFileSidebar');
  if (!sidebar) return;
  sidebar.classList.toggle('collapsed', _sidebarCollapsed);
  if (btn) {
    btn.title = _sidebarCollapsed ? 'Expand file sidebar' : 'Collapse file sidebar';
  }
}

function _setRunEnabled(enabled: boolean): void {
  const btn = document.getElementById('btnPanelRun') as HTMLButtonElement | null;
  if (!btn) return;
  btn.disabled = !enabled;
  btn.classList.toggle('opacity-40', !enabled);
  btn.classList.toggle('cursor-not-allowed', !enabled);
  btn.title = enabled ? 'Run project in preview' : 'No browser preview is available for this project';
}

function _hasPreviewableHtml(): boolean {
  return _files.some((file) => file.name.endsWith('.html'));
}

function _render(): void {
  _renderHeader();
  _renderTabs();
  _renderTree();
  if (_ready) {
    _renderContent();
  }
  _renderStats();
  _setRunEnabled(_ready && _hasPreviewableHtml());
}

function _renderHeader(): void {
  const t = document.getElementById('panelProjectTitle');
  const k = document.getElementById('panelProjectKind');
  if (t) t.textContent = _title;
  if (k) {
    k.textContent = _kind === 'game' ? 'Game' : (_kind === 'code' ? 'Code' : 'App');
    k.className = _kind === 'game'
      ? 'text-xs font-medium px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0'
      : _kind === 'code'
        ? 'text-xs font-medium px-1.5 py-0.5 rounded bg-fuchsia-500/10 text-fuchsia-300 border border-fuchsia-500/20 shrink-0'
        : 'text-xs font-medium px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0';
  }
}

function _renderTabs(): void {
  const bar = document.getElementById('codePanelTabs');
  if (!bar) return;
  bar.innerHTML = '';
  if (!_files.length) return;

  _files.forEach((file, i) => {
    const btn = document.createElement('button');
    const active = i === _activeIdx;
    btn.className = [
      'flex items-center space-x-1.5 px-3 py-2 text-sm border-b-2 whitespace-nowrap transition shrink-0',
      active ? 'text-white border-indigo-400 bg-slate-800/40' : 'text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/20',
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
  if (!_files.length) return;

  _files.forEach((file, i) => {
    const btn = document.createElement('button');
    const active = i === _activeIdx;
    const lines = file.content.split('\n').length;
    btn.className = [
      'w-full flex items-center gap-2 px-2 py-1.5 text-sm text-left rounded transition font-sans',
      active ? 'bg-indigo-500/10 text-indigo-200 border border-indigo-500/20' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent',
    ].join(' ');
    btn.innerHTML = `${_icon(file.language)}<span class="flex-1 truncate">${file.name}</span><span class="text-xs text-slate-600 shrink-0">${lines}L</span>`;
    btn.addEventListener('click', () => _selectFile(i));
    tree.appendChild(btn);
  });
}

function _renderContent(): void {
  const el = document.getElementById('codePanelContent');
  if (!el) return;
  const file = _files[_activeIdx];
  if (!file) { el.innerHTML = ''; return; }

  const escaped = file.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  const lines = escaped.split('\n');
  const numbered = lines.map((line, i) =>
    `<span class="select-none text-slate-600 inline-block w-9 text-right mr-3 text-xs font-mono">${i + 1}</span>${line}`,
  ).join('\n');

  el.innerHTML = `<pre class="text-sm font-mono leading-relaxed text-slate-300 whitespace-pre">${numbered}</pre>`;
}

function _renderStats(): void {
  const el = document.getElementById('codePanelStats');
  const file = _files[_activeIdx];
  if (!el) return;
  if (!file || !_ready) {
    el.textContent = _ready ? '' : 'Waiting for generated files...';
    return;
  }
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
    html: '<i class="fa-brands fa-html5 text-orange-400 text-xs shrink-0"></i>',
    css: '<i class="fa-brands fa-css3-alt text-blue-400 text-xs shrink-0"></i>',
    javascript: '<i class="fa-brands fa-js text-yellow-400 text-xs shrink-0"></i>',
    typescript: '<i class="fa-brands fa-js text-yellow-400 text-xs shrink-0"></i>',
    python: '<i class="fa-brands fa-python text-blue-300 text-xs shrink-0"></i>',
    java: '<i class="fa-brands fa-java text-orange-300 text-xs shrink-0"></i>',
    rust: '<i class="fa-brands fa-rust text-orange-500 text-xs shrink-0"></i>',
    ruby: '<i class="fa-solid fa-gem text-rose-400 text-xs shrink-0"></i>',
    sql: '<i class="fa-solid fa-database text-cyan-300 text-xs shrink-0"></i>',
    r: '<i class="fa-solid fa-chart-line text-sky-300 text-xs shrink-0"></i>',
    json: '<i class="fa-solid fa-brackets-curly text-slate-300 text-xs shrink-0"></i>',
    toml: '<i class="fa-solid fa-gear text-slate-400 text-xs shrink-0"></i>',
    xml: '<i class="fa-solid fa-code text-orange-300 text-xs shrink-0"></i>',
    makefile: '<i class="fa-solid fa-hammer text-amber-300 text-xs shrink-0"></i>',
    markdown: '<i class="fa-brands fa-markdown text-slate-400 text-xs shrink-0"></i>',
  };
  return m[lang] ?? '<i class="fa-solid fa-file-code text-slate-500 text-xs shrink-0"></i>';
}

function _runProject(): void {
  if (!_ready || !_files.length) return;
  if (!_hasPreviewableHtml()) return;
  const html = stitchProject(_files);
  if (!html.trim()) return;
  openSandboxPreview(html);
}

function _copyFile(): void {
  const file = _files[_activeIdx];
  if (!file) return;
  navigator.clipboard.writeText(file.content).then(() => {
    const btn = document.getElementById('btnPanelCopy');
    if (!btn) return;
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check text-xs"></i><span>Copied!</span>';
    setTimeout(() => { btn.innerHTML = orig; }, 1500);
  });
}
