// Settings panel — slide-in drawer from the right

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

export function saveSettings(s: AppSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

export let settings: AppSettings = loadSettings();

// ── Apply settings to the DOM ─────────────────────────────────────────────────

export function applySettings(s: AppSettings): void {
  settings = s;
  saveSettings(s);

  // Dark mode
  document.documentElement.classList.toggle('dark', s.darkMode);

  // Text size on chat feed
  const feed = document.getElementById('chatFeed');
  if (feed) {
    feed.classList.remove('text-sm', 'text-base', 'text-lg');
    feed.classList.add(`text-${s.textSize}`);
  }

  // Compact messages
  document.body.classList.toggle('forgeai-compact', s.compactMessages);

  // Quick mode — sync with footer toggle button state
  syncQuickModeButton(s.quickMode);
}

function syncQuickModeButton(on: boolean): void {
  const btn = document.getElementById('btnQuickMode');
  const icon = document.getElementById('quickModeIcon');
  if (!btn || !icon) return;
  if (on) {
    btn.classList.replace('bg-white', 'bg-emerald-500');
    btn.classList.replace('border-slate-200', 'border-emerald-500');
    btn.classList.replace('text-slate-500', 'text-white');
    btn.classList.replace('hover:border-slate-300', 'hover:border-emerald-600');
    icon.classList.replace('text-slate-400', 'text-white');
  } else {
    btn.classList.replace('bg-emerald-500', 'bg-white');
    btn.classList.replace('border-emerald-500', 'border-slate-200');
    btn.classList.replace('text-white', 'text-slate-500');
    btn.classList.replace('hover:border-emerald-600', 'hover:border-slate-300');
    icon.classList.replace('text-white', 'text-slate-400');
  }
}

// ── Panel HTML ────────────────────────────────────────────────────────────────

function buildPanel(): HTMLElement {
  const el = document.createElement('div');
  el.id = 'settingsPanel';
  el.className = [
    'fixed top-0 right-0 h-full w-80 bg-white border-l border-slate-200 shadow-2xl z-[60]',
    'flex flex-col translate-x-full transition-transform duration-300 ease-in-out',
  ].join(' ');

  el.innerHTML = `
    <div class="flex items-center justify-between px-5 py-4 border-b border-slate-200 shrink-0">
      <div class="flex items-center space-x-2">
        <i class="fa-solid fa-sliders text-indigo-500 text-sm"></i>
        <span class="font-semibold text-slate-800 text-sm">Settings</span>
      </div>
      <button id="btnCloseSettings" class="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100 transition">
        <i class="fa-solid fa-xmark text-sm"></i>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-5 py-4 space-y-6">

      <!-- Appearance -->
      <section>
        <p class="text-[10px] font-semibold uppercase tracking-widest text-slate-400 mb-3">Appearance</p>
        <div class="space-y-3">

          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-slate-700">Dark Mode</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Switch to dark theme</p>
            </div>
            <button class="toggle-btn" data-key="darkMode"></button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-slate-700">Compact Messages</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Reduce padding between messages</p>
            </div>
            <button class="toggle-btn" data-key="compactMessages"></button>
          </div>

          <div>
            <p class="text-xs font-medium text-slate-700 mb-2">Text Size</p>
            <div class="flex space-x-2" id="textSizePicker">
              <button data-size="sm"  class="size-btn flex-1 py-1.5 rounded-lg border text-[11px] font-medium transition">Small</button>
              <button data-size="base" class="size-btn flex-1 py-1.5 rounded-lg border text-[11px] font-medium transition">Normal</button>
              <button data-size="lg"  class="size-btn flex-1 py-1.5 rounded-lg border text-[11px] font-medium transition">Large</button>
            </div>
          </div>

        </div>
      </section>

      <!-- Behaviour -->
      <section>
        <p class="text-[10px] font-semibold uppercase tracking-widest text-slate-400 mb-3">Behaviour</p>
        <div class="space-y-3">

          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-slate-700">Streaming Text</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Animate words as they appear</p>
            </div>
            <button class="toggle-btn" data-key="streamingText"></button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-slate-700">Quick Mode</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Short, direct answers only</p>
            </div>
            <button class="toggle-btn" data-key="quickMode"></button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-slate-700">Typing Shimmer</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Show shimmer while waiting</p>
            </div>
            <button class="toggle-btn" data-key="showTypingShimmer"></button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-slate-700">Web Search Indicator</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Show "Searching the web…" label</p>
            </div>
            <button class="toggle-btn" data-key="showSearchIndicator"></button>
          </div>

        </div>
      </section>

      <!-- Danger zone -->
      <section>
        <p class="text-[10px] font-semibold uppercase tracking-widest text-slate-400 mb-3">Data</p>
        <button id="btnClearHistory" class="w-full py-2 rounded-lg border border-red-200 text-red-500 hover:bg-red-50 text-xs font-medium transition">
          Clear all chat history
        </button>
      </section>

    </div>
  `;

  return el;
}

// ── Toggle button style helpers ───────────────────────────────────────────────

function styleToggle(btn: HTMLElement, on: boolean): void {
  if (on) {
    btn.className = 'toggle-btn relative w-9 h-5 rounded-full bg-indigo-500 transition-colors duration-200 shrink-0';
    btn.innerHTML = '<span class="absolute top-0.5 left-5 w-4 h-4 bg-white rounded-full shadow transition-all duration-200"></span>';
  } else {
    btn.className = 'toggle-btn relative w-9 h-5 rounded-full bg-slate-200 transition-colors duration-200 shrink-0';
    btn.innerHTML = '<span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-all duration-200"></span>';
  }
}

function styleSizeButtons(panel: HTMLElement, active: string): void {
  panel.querySelectorAll<HTMLElement>('.size-btn').forEach((b) => {
    const isActive = b.dataset.size === active;
    b.className = `size-btn flex-1 py-1.5 rounded-lg border text-[11px] font-medium transition ${
      isActive
        ? 'bg-indigo-500 border-indigo-500 text-white'
        : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
    }`;
  });
}

function refreshPanel(panel: HTMLElement, s: AppSettings): void {
  panel.querySelectorAll<HTMLElement>('.toggle-btn[data-key]').forEach((btn) => {
    const key = btn.dataset.key as keyof AppSettings;
    styleToggle(btn, Boolean(s[key]));
  });
  styleSizeButtons(panel, s.textSize);
}

// ── Overlay backdrop ──────────────────────────────────────────────────────────

function getOrCreateBackdrop(): HTMLElement {
  let bd = document.getElementById('settingsBackdrop');
  if (!bd) {
    bd = document.createElement('div');
    bd.id = 'settingsBackdrop';
    bd.className = 'fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-[59] hidden';
    document.body.appendChild(bd);
    bd.addEventListener('click', closeSettings);
  }
  return bd;
}

// ── Open / close ──────────────────────────────────────────────────────────────

function closeSettings(): void {
  const panel = document.getElementById('settingsPanel');
  const bd = document.getElementById('settingsBackdrop');
  panel?.classList.add('translate-x-full');
  bd?.classList.add('hidden');
}

function openSettings(): void {
  const panel = document.getElementById('settingsPanel') as HTMLElement | null;
  const bd = getOrCreateBackdrop();
  if (!panel) return;
  refreshPanel(panel, settings);
  panel.classList.remove('translate-x-full');
  bd.classList.remove('hidden');
}

// ── Init ──────────────────────────────────────────────────────────────────────

export function initSettings(): void {
  // Build and mount panel
  const panel = buildPanel();
  document.body.appendChild(panel);

  // Close button
  panel.querySelector('#btnCloseSettings')?.addEventListener('click', closeSettings);

  // Toggle buttons
  panel.querySelectorAll<HTMLElement>('.toggle-btn[data-key]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.key as keyof AppSettings;
      const next = { ...settings, [key]: !settings[key] };
      applySettings(next);
      // Sync quick mode to state
      if (key === 'quickMode') {
        // Import state lazily to avoid circular deps
        import('../state').then(({ state: appState }) => {
          appState.quickMode = next.quickMode;
        });
      }
      refreshPanel(panel, next);
    });
  });

  // Text size picker
  panel.querySelectorAll<HTMLElement>('.size-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const size = btn.dataset.size as AppSettings['textSize'];
      const next = { ...settings, textSize: size };
      applySettings(next);
      refreshPanel(panel, next);
    });
  });

  // Clear history
  panel.querySelector('#btnClearHistory')?.addEventListener('click', () => {
    if (!confirm('Clear all chat history? This cannot be undone.')) return;
    localStorage.removeItem('forgeai_sessions');
    location.reload();
  });

  // Header "Settings" button
  document.getElementById('btnOpenSettings')?.addEventListener('click', openSettings);

  // Apply saved settings on load
  applySettings(settings);
}
