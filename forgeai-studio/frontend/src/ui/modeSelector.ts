import { state, MODE_CONFIGS } from '../state';
import { saveActiveMode } from '../utils/storage';
import { showToast } from './toast';
import type { Mode, Workspace } from '../types';

const CHAT_FALLBACK_MODE: Mode = 'forge_thinking';
const CODE_DEFAULT_MODE: Mode = 'forge_code';

export function modeAllowedInWorkspace(mode: Mode, workspace: Workspace): boolean {
  return workspace === 'code' || mode !== 'forge_code';
}

export function ensureModeForWorkspace(workspace = state.activeWorkspace): void {
  if (!modeAllowedInWorkspace(state.activeMode, workspace)) {
    state.activeMode = CHAT_FALLBACK_MODE;
    saveActiveMode(state.activeMode);
  } else if (workspace === 'code' && state.activeMode !== CODE_DEFAULT_MODE) {
    state.activeMode = CODE_DEFAULT_MODE;
    saveActiveMode(state.activeMode);
  }
  updateModeSelectorUI(state.activeMode);
}

export function initModeSelector(): void {
  const btn = document.getElementById('btnModeSelector');
  const menu = document.getElementById('modeMenu');
  if (!btn || !menu) return;

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('hidden');
  });

  document.addEventListener('click', () => menu.classList.add('hidden'));

  menu.querySelectorAll<HTMLElement>('button').forEach((modeBtn) => {
    modeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const selectedMode = modeBtn.dataset.mode as Mode;
      if (!selectedMode) return;
      if (!modeAllowedInWorkspace(selectedMode, state.activeWorkspace)) {
        showToast('Cosmos 2.8 is only available in Code Mode');
        menu.classList.add('hidden');
        return;
      }
      state.activeMode = selectedMode;
      saveActiveMode(selectedMode);
      updateModeSelectorUI(selectedMode);
      menu.classList.add('hidden');
      showToast(`Switched to ${MODE_CONFIGS[selectedMode].text}`);
    });
  });
}

export function updateModeSelectorUI(mode: Mode): void {
  if (!modeAllowedInWorkspace(mode, state.activeWorkspace)) {
    mode = CHAT_FALLBACK_MODE;
    state.activeMode = mode;
    saveActiveMode(mode);
  }
  const config = MODE_CONFIGS[mode];
  const textEl = document.getElementById('currentModeText');
  const btn = document.getElementById('btnModeSelector');

  if (textEl) textEl.innerText = config.text;
  if (btn) {
    const icon = btn.querySelector('i.fa-solid');
    if (icon) icon.className = `fa-solid ${config.icon} text-[10px] ${config.color}`;
  }

  document.querySelectorAll<HTMLElement>('#modeMenu button').forEach((b) => {
    const mk = b.dataset.mode as Mode;
    if (!mk) return;
    const allowed = modeAllowedInWorkspace(mk, state.activeWorkspace);
    b.classList.toggle('hidden', !allowed);
    if (!allowed) return;
    const mc = MODE_CONFIGS[mk];
    b.className =
      mk === mode
        ? `w-full px-3 py-2 text-xs ${mc.color} ${mc.bg} flex items-center space-x-2.5 transition font-semibold`
        : 'w-full px-3 py-2 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-50 flex items-center space-x-2.5 transition font-medium';
  });
}
