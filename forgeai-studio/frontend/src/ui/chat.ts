import { state } from '../state';
import { sendChat } from '../api';
import { settings } from './settings';
import { saveSessions } from '../utils/storage';
import { escapeHTML } from '../utils/helpers';
import { formatMarkdown } from './markdown';
import { showToast } from './toast';
import { renderSessionList } from './sidebar';
import { buildFileViewer } from './fileViewer';
import { showProjectInPanel } from './codePanel';
import type { ProjectFile } from '../types';

function getChatFeed(): HTMLElement {
  return document.getElementById('chatFeed') as HTMLElement;
}

export function addUserMessageUI(text: string): void {
  const feed = getChatFeed();
  const row = document.createElement('div');
  row.className = 'flex items-start justify-end space-x-3 max-w-[85%] ml-auto text-left';
  row.innerHTML = `<div class="bg-slate-100 border border-slate-200/60 text-slate-800 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm text-sm leading-relaxed">
    ${escapeHTML(text).replace(/\n/g, '<br>')}
  </div>`;
  feed.appendChild(row);
  feed.scrollTop = feed.scrollHeight;
}

export function addThinkingIndicatorUI(): HTMLElement {
  const feed = getChatFeed();
  const row = document.createElement('div');
  row.className = 'flex items-start space-x-4 max-w-[95%] text-left';
  row.innerHTML = `
    <div class="h-8 w-8 bg-slate-100 border border-slate-200 rounded-lg flex items-center justify-center shrink-0 shadow-sm">
      <i class="fa-solid fa-circle-notch text-slate-600 text-xs animate-spin"></i>
    </div>
    <div class="bg-slate-50 border border-slate-200/60 p-5 rounded-2xl rounded-tl-none w-full space-y-2">
      <div class="flex items-center space-x-2 text-slate-500 text-xs font-medium" id="thinkingLabel">
        <i class="fa-solid fa-brain text-slate-400" id="thinkingIcon"></i>
        <span id="thinkingText">Formulating system response...</span>
      </div>
      ${settings.showTypingShimmer ? '<div class="h-3 shimmer-bg rounded w-3/4"></div><div class="h-3 shimmer-bg rounded w-1/2"></div>' : ''}
    </div>`;
  feed.appendChild(row);
  feed.scrollTop = feed.scrollHeight;

  // After 700ms with no response, assume web search is happening
  const searchTimer = settings.showSearchIndicator ? setTimeout(() => {
    const icon = row.querySelector('#thinkingIcon') as HTMLElement | null;
    const text = row.querySelector('#thinkingText') as HTMLElement | null;
    if (icon) { icon.className = 'fa-solid fa-globe text-indigo-400'; }
    if (text) { text.textContent = 'Searching the web...'; }
  }, 700) : undefined;

  (row as any)._searchTimer = searchTimer;
  return row;
}

export function resolveThinkingIndicator(row: HTMLElement, webSearched: boolean): void {
  clearTimeout((row as any)._searchTimer);
  if (webSearched) {
    const icon = row.querySelector('#thinkingIcon') as HTMLElement | null;
    const text = row.querySelector('#thinkingText') as HTMLElement | null;
    if (icon) { icon.className = 'fa-solid fa-globe text-indigo-400'; }
    if (text) { text.textContent = 'Searching the web...'; }
  }
}

export function addAIProjectUI(text: string, files: ProjectFile[], kind: string): HTMLElement {
  const feed = getChatFeed();
  const row = document.createElement('div');
  row.className = 'flex items-start space-x-4 max-w-[95%] text-left';
  row.innerHTML = `
    <div class="h-8 w-8 bg-slate-900 rounded-lg flex items-center justify-center shrink-0 shadow-sm">
      <i class="fa-solid fa-wand-magic-sparkles text-white text-xs"></i>
    </div>
    <div class="bg-slate-50 border border-slate-200/40 p-5 rounded-2xl rounded-tl-none text-slate-700 leading-relaxed text-sm w-full shadow-sm">
      <div class="response-body font-normal text-slate-800 mb-3"></div>
      <div class="file-viewer-slot"></div>
    </div>`;
  feed.appendChild(row);

  const body = row.querySelector('.response-body') as HTMLElement;
  body.innerHTML = formatMarkdown(text);

  const slot = row.querySelector('.file-viewer-slot') as HTMLElement;
  slot.appendChild(buildFileViewer(files, kind));

  const distFromBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight;
  if (distFromBottom < 400) feed.scrollTop = feed.scrollHeight;

  return row;
}

export async function addAIStreamUI(fullText: string, stream = true): Promise<HTMLElement> {
  const feed = getChatFeed();
  const row = document.createElement('div');
  row.className = 'flex items-start space-x-4 max-w-[95%] text-left';
  row.innerHTML = `
    <div class="h-8 w-8 bg-slate-900 rounded-lg flex items-center justify-center shrink-0 shadow-sm">
      <i class="fa-solid fa-wand-magic-sparkles text-white text-xs"></i>
    </div>
    <div class="bg-slate-50 border border-slate-200/40 p-5 rounded-2xl rounded-tl-none text-slate-700 leading-relaxed text-sm w-full shadow-sm">
      <div class="response-body font-normal text-slate-800"></div>
    </div>`;
  feed.appendChild(row);

  const body = row.querySelector('.response-body') as HTMLElement;

  // If the response contains a code block, skip streaming — render instantly
  const hasCodeBlock = fullText.includes('```');

  if (!stream || hasCodeBlock || !settings.streamingText) {
    body.innerHTML = formatMarkdown(fullText);
    // Only scroll to bottom if user is already near the bottom
    const distFromBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight;
    if (distFromBottom < 300) feed.scrollTop = feed.scrollHeight;
    return row;
  }

  return new Promise((resolve) => {
    const words = fullText.split(' ');
    let i = 0;
    const accumulated: string[] = [];
    let userScrolled = false;

    const onScroll = () => {
      const distFromBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight;
      userScrolled = distFromBottom > 150;
    };
    feed.addEventListener('scroll', onScroll, { passive: true });

    const timer = setInterval(() => {
      if (i < words.length) {
        accumulated.push(words[i++]);
        body.innerHTML = formatMarkdown(accumulated.join(' '));
        if (!userScrolled) feed.scrollTop = feed.scrollHeight;
      } else {
        clearInterval(timer);
        feed.removeEventListener('scroll', onScroll);
        resolve(row);
      }
    }, 8);
  });
}

export function renderCurrentSessionChat(): void {
  const feed = getChatFeed();
  feed.innerHTML = '';

  const session = state.sessions.find((s) => s.id === state.currentSessionId);
  if (!session) return;

  if (session.messages.length === 0) {
    if (session.workspace === 'code') {
      feed.innerHTML = `
  <div class="flex flex-col items-center justify-center text-center py-12 px-4 max-w-2xl mx-auto space-y-8 select-none">
    <div class="space-y-1.5">
      <p class="text-[10px] text-indigo-500 font-mono uppercase tracking-widest font-semibold">Code Mode Active</p>
      <p class="text-slate-500 text-xs">Describe what to build — games, apps, tools, or anything you can imagine.</p>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg text-left">
      <button onclick="window.prefillPrompt('build me a snake game with neon theme')"
        class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
          <i class="fa-solid fa-gamepad text-indigo-500"></i><span>Arcade Games</span>
        </div>
        <p class="text-[10px] text-slate-400">Snake, Pong, Space Shooter, Platformer — fully playable.</p>
      </button>
      <button onclick="window.prefillPrompt('create a todo app with priorities and due dates')"
        class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
          <i class="fa-solid fa-list-check text-indigo-500"></i><span>Productivity Apps</span>
        </div>
        <p class="text-[10px] text-slate-400">Todo lists, habit trackers, kanban boards, planners.</p>
      </button>
      <button onclick="window.prefillPrompt('build a budget tracker with charts and category filters')"
        class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
          <i class="fa-solid fa-chart-line text-indigo-500"></i><span>Finance Tools</span>
        </div>
        <p class="text-[10px] text-slate-400">Budget trackers, expense logs, investment dashboards.</p>
      </button>
      <button onclick="window.prefillPrompt('make a password generator with strength meter')"
        class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
        <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
          <i class="fa-solid fa-screwdriver-wrench text-indigo-500"></i><span>Utility Tools</span>
        </div>
        <p class="text-[10px] text-slate-400">Calculators, converters, generators, timers.</p>
      </button>
    </div>
  </div>`;
    } else {
      feed.innerHTML = `
      <div class="flex flex-col items-center justify-center text-center py-12 px-4 max-w-2xl mx-auto space-y-8 select-none">
        <div class="space-y-1.5">
          <p class="text-[10px] text-indigo-500 font-mono uppercase tracking-widest font-semibold">Local Cognitive Core Initialized</p>
          <p class="text-slate-500 text-xs">Select a suggestion below or type a query to begin.</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg text-left">
          <button onclick="window.prefillPrompt('Whats derivative of 3x^3 + 5x^2 - 4x?')"
            class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
            <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
              <i class="fa-solid fa-infinity text-indigo-500"></i><span>Calculus &amp; Trigonometry</span>
            </div>
            <p class="text-[10px] text-slate-400">Differentiate polynomials, solve integrals, or compute trig ratios.</p>
          </button>
          <button onclick="window.prefillPrompt('what is the distance between the earth and the sun?')"
            class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
            <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
              <i class="fa-solid fa-user-astronaut text-indigo-500"></i><span>Explore Space Telemetry</span>
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Check orbital distances, cosmic constants, and planetary data.</p>
          </button>
          <button onclick="window.prefillPrompt('make a flappy bird game')"
            class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
            <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
              <i class="fa-solid fa-gamepad text-indigo-500"></i><span>Build Playable Games</span>
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Generate complete HTML5 Flappy, Pong, Snake, or Shooter games.</p>
          </button>
          <button onclick="window.prefillPrompt('tell me about underwater hydrothermal vents and ocean trenches')"
            class="p-4 bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-md rounded-xl transition text-xs space-y-1">
            <div class="font-semibold text-slate-800 flex items-center space-x-1.5">
              <i class="fa-solid fa-mountain-sun text-indigo-500"></i><span>Underwater Earth Science</span>
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Analyze Challenger Deep, mid-ocean rifts, and black smoker vents.</p>
          </button>
        </div>
      </div>`;
    }
  } else {
    session.messages.forEach((msg) => {
      if (msg.role === 'user') {
        addUserMessageUI(msg.text);
      } else if (msg.project_files && msg.project_files.length > 0) {
        const kind = msg.project_files.some(f => f.name === 'game.js') ? 'game' : 'app';
        if (session.workspace === 'code') {
          const titleMatch = msg.text.match(/\*\*(.+?)\*\*/);
          const projTitle = titleMatch ? titleMatch[1] : (kind === 'game' ? 'Game' : 'Project');
          showProjectInPanel(msg.project_files, projTitle, kind);
          addAIStreamUI(msg.text, false);
        } else {
          addAIProjectUI(msg.text, msg.project_files, kind);
        }
      } else {
        addAIStreamUI(msg.text, false);
      }
    });
  }

  feed.scrollTop = feed.scrollHeight;
}

export function initQuickToggle(): void {
  const btn = document.getElementById('btnQuickMode');
  const icon = document.getElementById('quickModeIcon');
  if (!btn || !icon) return;

  btn.addEventListener('click', () => {
    state.quickMode = !state.quickMode;
    if (state.quickMode) {
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
  });
}

export function initChatForm(): void {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('userInput') as HTMLTextAreaElement | null;

  input?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('btnSubmit')?.click();
    }
  });

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!input) return;

    const text = input.value.trim();
    if (!text) return;

    const session = state.sessions.find((s) => s.id === state.currentSessionId);
    if (!session) return;

    if (session.messages.length === 0) {
      session.title = text.length > 24 ? text.slice(0, 22) + '...' : text;
    }

    session.messages.push({ role: 'user', text });
    addUserMessageUI(text);
    input.value = '';

    const thinkingRow = addThinkingIndicatorUI();

    try {
      const res = await sendChat({
        query: text,
        mode: state.activeMode,
        history: session.messages.map((m) => ({ role: m.role, content: m.text, text: m.text, project_files: m.project_files })),
        quick_mode: state.quickMode,
        workspace: state.activeWorkspace,
      });

      resolveThinkingIndicator(thinkingRow, res.web_searched ?? false);
      thinkingRow.remove();
      session.messages.push({
        role: 'assistant',
        text: res.text,
        project_files: res.project_files?.length ? res.project_files : undefined,
      });
      saveSessions(state.sessions);
      renderSessionList();

      if (res.project_files && res.project_files.length > 0) {
        const kind = res.project_files.some(f => f.name === 'game.js') ? 'game' : 'app';
        // Extract project title from response text
        const titleMatch = res.text.match(/\*\*(.+?)\*\*/);
        const projTitle = titleMatch ? titleMatch[1] : (kind === 'game' ? 'Game' : 'Project');
        // Show in right panel if in code workspace, else inline
        if (state.activeWorkspace === 'code') {
          showProjectInPanel(res.project_files, projTitle, kind);
          await addAIStreamUI(res.text, false);
        } else {
          addAIProjectUI(res.text, res.project_files, kind);
        }
      } else {
        await addAIStreamUI(res.text, true);
      }
    } catch {
      thinkingRow.remove();
      showToast('Failed to reach the ForgeAI backend.', true);
    }
  });
}
