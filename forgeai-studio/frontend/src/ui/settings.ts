import { state } from '../state';

const STORAGE_KEY = 'forgeai_settings';

export interface AppSettings {
  darkMode: boolean;
  streamingText: boolean;
  quickMode: boolean;
  compactMessages: boolean;
  textSize: 'sm' | 'base' | 'lg';
  showSearchIndicator: boolean;
  showTypingShimmer: boolean;
}

const DEFAULTS: AppSettings = {
  darkMode: false,
  streamingText: true,
  quickMode: false,
  compactMessages: false,
  textSize: 'sm',
  showSearchIndicator: true,
  showTypingShimmer: true,
};

export function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : { ...DEFAULTS };
  } catch {
    return { ...DEFAULTS };
  }
}

function saveSettings(s: AppSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

export let settings: AppSettings = loadSettings();

// ── Dark mode style injection ─────────────────────────────────────────────────

const DARK_STYLE_ID = 'forgeai-dark-style';

function applyDarkMode(on: boolean): void {
  let tag = document.getElementById(DARK_STYLE_ID) as HTMLStyleElement | null;
  if (on) {
    if (!tag) {
      tag = document.createElement('style');
      tag.id = DARK_STYLE_ID;
      document.head.appendChild(tag);
    }
    tag.textContent = `
      body { background: #0f172a !important; color: #e2e8f0 !important; }
      main { background: #0f172a !important; }
      header { background: #1e293b !important; border-color: #334155 !important; }
      footer { background: #1e293b !important; border-color: #334155 !important; }
      #chatFeed { background: #0f172a !important; }
      aside#sidebarPanel { background: #1e293b !important; border-color: #334155 !important; }
      #chatForm { background: #1e293b !important; border-color: #334155 !important; }
      #userInput { color: #e2e8f0 !important; background: transparent !important; }
      #settingsPanel { background: #1e293b !important; border-color: #334155 !important; }
      #settingsPanel p, #settingsPanel span { color: #cbd5e1 !important; }
      #settingsPanel .text-slate-800 { color: #e2e8f0 !important; }
      #settingsPanel .text-slate-400 { color: #94a3b8 !important; }
      .bg-slate-50 { background: #1e293b !important; }
      .bg-white { background: #1e293b !important; }
      .border-slate-200 { border-color: #334155 !important; }
      .text-slate-800 { color: #e2e8f0 !important; }
      .text-slate-700 { color: #cbd5e1 !important; }
      .text-slate-600 { color: #94a3b8 !important; }
      .text-slate-500 { color: #94a3b8 !important; }
    `;
  } else if (tag) {
    tag.textContent = '';
  }
}

// ── Compact messages ──────────────────────────────────────────────────────────

const COMPACT_STYLE_ID = 'forgeai-compact-style';

function applyCompact(on: boolean): void {
  let tag = document.getElementById(COMPACT_STYLE_ID) as HTMLStyleElement | null;
  if (on) {
    if (!tag) {
      tag = document.createElement('style');
      tag.id = COMPACT_STYLE_ID;
      document.head.appendChild(tag);
    }
    tag.textContent = `#chatFeed { gap: 0.75rem !important; } #chatFeed > div { margin-bottom: 0 !important; } #chatFeed > div .p-5 { padding: 0.625rem 0.875rem !important; }`;
  } else if (tag) {
    tag.textContent = '';
  }
}

// ── Text size ─────────────────────────────────────────────────────────────────

function applyTextSize(size: AppSettings['textSize']): void {
  const map = { sm: '13px', base: '15px', lg: '17px' };
  const feed = document.getElementById('chatFeed');
  if (feed) feed.style.fontSize = map[size];
}

// ── Quick mode sync ───────────────────────────────────────────────────────────

function applyQuickMode(on: boolean): void {
  state.quickMode = on;
  const btn = document.getElementById('btnQuickMode');
  const icon = document.getElementById('quickModeIcon');
  if (!btn || !icon) return;
  if (on) {
    btn.style.background = '#10b981';
    btn.style.borderColor = '#10b981';
    btn.style.color = '#fff';
    icon.style.color = '#fff';
  } else {
    btn.style.background = '';
    btn.style.borderColor = '';
    btn.style.color = '';
    icon.style.color = '';
  }
}

// ── Main apply ────────────────────────────────────────────────────────────────

export function applySettings(s: AppSettings): void {
  settings = s;
  saveSettings(s);
  applyDarkMode(s.darkMode);
  applyCompact(s.compactMessages);
  applyTextSize(s.textSize);
  applyQuickMode(s.quickMode);
}

// ── Toggle visual ─────────────────────────────────────────────────────────────

function styleToggle(btn: HTMLElement, on: boolean): void {
  btn.style.background = on ? '#6366f1' : '#cbd5e1';
  const knob = btn.querySelector('span') as HTMLElement;
  if (knob) knob.style.transform = on ? 'translateX(16px)' : 'translateX(0)';
}

function styleSizeButtons(panel: HTMLElement, active: string): void {
  panel.querySelectorAll<HTMLElement>('.size-btn').forEach((b) => {
    const isActive = b.dataset.size === active;
    b.style.background = isActive ? '#6366f1' : '#fff';
    b.style.borderColor = isActive ? '#6366f1' : '#e2e8f0';
    b.style.color = isActive ? '#fff' : '#475569';
  });
}

function refreshPanel(panel: HTMLElement, s: AppSettings): void {
  panel.querySelectorAll<HTMLElement>('.toggle-btn').forEach((btn) => {
    const key = btn.dataset.key as keyof AppSettings;
    styleToggle(btn, Boolean(s[key]));
  });
  styleSizeButtons(panel, s.textSize);
}

// ── Panel HTML ────────────────────────────────────────────────────────────────

function buildPanel(): HTMLElement {
  const el = document.createElement('div');
  el.id = 'settingsPanel';
  el.style.cssText = `
    position:fixed;top:0;right:0;height:100%;width:320px;
    background:#fff;border-left:1px solid #e2e8f0;box-shadow:-8px 0 32px rgba(0,0,0,0.12);
    z-index:60;display:flex;flex-direction:column;
    transform:translateX(100%);transition:transform 0.25s cubic-bezier(0.4,0,0.2,1);
  `;

  const row = (label: string, desc: string, key: string): string => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
      <div>
        <p style="font-size:12px;font-weight:600;color:#1e293b;margin:0;">${label}</p>
        <p style="font-size:10px;color:#94a3b8;margin:2px 0 0;">${desc}</p>
      </div>
      <button class="toggle-btn" data-key="${key}"
        style="position:relative;width:36px;height:20px;border-radius:999px;background:#cbd5e1;border:none;cursor:pointer;flex-shrink:0;transition:background 0.2s;">
        <span style="position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.2);transition:transform 0.2s;display:block;"></span>
      </button>
    </div>`;

  el.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid #e2e8f0;flex-shrink:0;">
      <div style="display:flex;align-items:center;gap:8px;">
        <i class="fa-solid fa-sliders" style="color:#6366f1;font-size:13px;"></i>
        <span style="font-size:13px;font-weight:700;color:#1e293b;">Settings</span>
      </div>
      <button id="btnCloseSettings" style="background:none;border:none;cursor:pointer;color:#94a3b8;font-size:14px;padding:4px 6px;border-radius:6px;" onmouseover="this.style.color='#1e293b'" onmouseout="this.style.color='#94a3b8'">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>

    <div style="flex:1;overflow-y:auto;padding:16px 20px;">

      <p style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;margin:0 0 4px;">Appearance</p>
      ${row('Dark Mode', 'Switch to dark theme', 'darkMode')}
      ${row('Compact Messages', 'Reduce spacing between messages', 'compactMessages')}

      <div style="padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <p style="font-size:12px;font-weight:600;color:#1e293b;margin:0 0 8px;">Text Size</p>
        <div style="display:flex;gap:8px;">
          <button class="size-btn" data-size="sm"   style="flex:1;padding:6px;border-radius:8px;border:1px solid #e2e8f0;font-size:11px;font-weight:600;cursor:pointer;transition:.15s;">Small</button>
          <button class="size-btn" data-size="base" style="flex:1;padding:6px;border-radius:8px;border:1px solid #e2e8f0;font-size:11px;font-weight:600;cursor:pointer;transition:.15s;">Normal</button>
          <button class="size-btn" data-size="lg"   style="flex:1;padding:6px;border-radius:8px;border:1px solid #e2e8f0;font-size:11px;font-weight:600;cursor:pointer;transition:.15s;">Large</button>
        </div>
      </div>

      <p style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;margin:16px 0 4px;">Behaviour</p>
      ${row('Streaming Text', 'Animate words as they appear', 'streamingText')}
      ${row('Quick Mode', 'Short, direct answers only', 'quickMode')}
      ${row('Typing Shimmer', 'Show shimmer bars while waiting', 'showTypingShimmer')}
      ${row('Web Search Indicator', 'Show "Searching the web…" label', 'showSearchIndicator')}

    </div>
  `;

  return el;
}

// ── Backdrop ──────────────────────────────────────────────────────────────────

function getOrCreateBackdrop(): HTMLElement {
  let bd = document.getElementById('settingsBackdrop');
  if (!bd) {
    bd = document.createElement('div');
    bd.id = 'settingsBackdrop';
    bd.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,0.2);backdrop-filter:blur(2px);z-index:59;display:none;';
    document.body.appendChild(bd);
    bd.addEventListener('click', closeSettings);
  }
  return bd;
}

export function closeSettings(): void {
  const panel = document.getElementById('settingsPanel');
  const bd = document.getElementById('settingsBackdrop');
  if (panel) panel.style.transform = 'translateX(100%)';
  if (bd) bd.style.display = 'none';
}

function openSettings(): void {
  const panel = document.getElementById('settingsPanel') as HTMLElement | null;
  const bd = getOrCreateBackdrop();
  if (!panel) return;
  refreshPanel(panel, settings);
  panel.style.transform = 'translateX(0)';
  bd.style.display = 'block';
}

// ── Init ──────────────────────────────────────────────────────────────────────

export function initSettings(): void {
  const panel = buildPanel();
  document.body.appendChild(panel);

  panel.querySelector('#btnCloseSettings')?.addEventListener('click', closeSettings);

  panel.querySelectorAll<HTMLElement>('.toggle-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.key as keyof AppSettings;
      const next = { ...settings, [key]: !settings[key] };
      applySettings(next);
      refreshPanel(panel, next);
    });
  });

  panel.querySelectorAll<HTMLElement>('.size-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const size = btn.dataset.size as AppSettings['textSize'];
      const next = { ...settings, textSize: size };
      applySettings(next);
      refreshPanel(panel, next);
    });
  });

  document.getElementById('btnOpenSettings')?.addEventListener('click', openSettings);

  applySettings(settings);
}
