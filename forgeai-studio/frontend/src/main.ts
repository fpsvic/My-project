import { state, MODE_CONFIGS } from './state';
import { loadSessions, saveSessions, loadActiveMode, saveActiveMode, loadActiveWorkspace } from './utils/storage';
import { generateId } from './utils/helpers';
import { initSplash } from './ui/splash';
import { initSidebar, renderSessionList, createNewSession } from './ui/sidebar';
import { initChatForm, initQuickToggle, renderCurrentSessionChat } from './ui/chat';
import { initModeSelector, updateModeSelectorUI } from './ui/modeSelector';
import { openSandboxFromCode, closeSandbox } from './ui/sandbox';
import { initSettings, loadSettings } from './ui/settings';
import { initCodePanel } from './ui/codePanel';
import type { Mode } from './types';

// Expose globals required by inline HTML onclick attributes
declare global {
  interface Window {
    closeSandbox: () => void;
    openSandboxFromCode: (btn: HTMLElement) => void;
    prefillPrompt: (text: string) => void;
    copyCodeSnippet: (btn: HTMLElement) => void;
  }
}

window.closeSandbox = closeSandbox;
window.openSandboxFromCode = openSandboxFromCode;

window.copyCodeSnippet = (btn: HTMLElement): void => {
  const pre = btn.closest('.my-4')?.querySelector('pre code') as HTMLElement | null;
  if (!pre) return;
  navigator.clipboard.writeText(pre.innerText).catch(() => {
    // fallback for older browsers
    const ta = document.createElement('textarea');
    ta.value = pre.innerText;
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  });
};

window.prefillPrompt = (text: string): void => {
  const input = document.getElementById('userInput') as HTMLTextAreaElement | null;
  const submit = document.getElementById('btnSubmit') as HTMLButtonElement | null;
  if (!input || !submit) return;
  input.value = text;
  input.focus();
  setTimeout(() => submit.click(), 100);
};

function bootstrap(): void {
  const stored = loadSessions();
  state.sessions = stored;
  state.activeWorkspace = loadActiveWorkspace();

  // Sync quick mode from persisted settings
  const saved = loadSettings();
  state.quickMode = saved.quickMode;

  const savedMode = loadActiveMode();
  if (savedMode && MODE_CONFIGS[savedMode]) {
    state.activeMode = savedMode as Mode;
    updateModeSelectorUI(savedMode as Mode);
  }

  const workspaceSessions = state.sessions.filter(s => s.workspace === state.activeWorkspace);
  if (workspaceSessions.length === 0) {
    createNewSession();
  } else {
    state.currentSessionId = workspaceSessions[0].id;
    state.activeLanguage = workspaceSessions[0].language;
    renderSessionList();
    renderCurrentSessionChat();
  }

  initSplash();
  initSidebar();
  initChatForm();
  initQuickToggle();
  initModeSelector();
  initSettings();
  initCodePanel();
}

window.addEventListener('load', bootstrap);
