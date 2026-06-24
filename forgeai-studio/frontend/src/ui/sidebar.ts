import { state } from '../state';
import { saveSessions, loadSessions } from '../utils/storage';
import { generateId, getLanguageIconHTML } from '../utils/helpers';
import { showToast } from './toast';
import { renderCurrentSessionChat } from './chat';

export function renderSessionList(): void {
  const container = document.getElementById('sessionListContainer');
  if (!container) return;
  container.innerHTML = '';

  state.sessions.forEach((session) => {
    const isActive = session.id === state.currentSessionId;
    const card = document.createElement('div');
    card.className = [
      'group relative flex items-center justify-between mx-1.5 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 cursor-pointer',
      isActive
        ? 'bg-slate-200/60 text-slate-900 border border-slate-200/80 shadow-sm'
        : 'hover:bg-slate-100 text-slate-600 hover:text-slate-900',
    ].join(' ');

    const textContainer = document.createElement('div');
    textContainer.className = 'flex items-center space-x-2.5 truncate w-full pr-12';
    textContainer.innerHTML = `${getLanguageIconHTML(session.language)}<span class="truncate text-slate-800 font-medium">${session.title}</span>`;
    card.appendChild(textContainer);

    const actions = document.createElement('div');
    actions.className =
      'absolute right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150';
    actions.innerHTML = `
      <button class="rename-btn text-slate-400 hover:text-slate-700 p-1 rounded-md hover:bg-white/80 border border-transparent hover:border-slate-200/40 transition-colors">
        <i class="fa-solid fa-pen text-[9px]"></i>
      </button>
      <button class="delete-btn text-slate-400 hover:text-rose-500 p-1 rounded-md hover:bg-white/80 border border-transparent hover:border-slate-200/40 transition-colors">
        <i class="fa-solid fa-trash-can text-[9px]"></i>
      </button>`;
    card.appendChild(actions);

    let isRenaming = false;
    const titleSpan = textContainer.querySelector('span')!;

    actions.querySelector('.rename-btn')!.addEventListener('click', (e) => {
      e.stopPropagation();
      if (isRenaming) return;
      isRenaming = true;

      const input = document.createElement('input');
      input.type = 'text';
      input.value = session.title;
      input.className =
        'w-full bg-white border border-slate-300 focus:border-slate-400 focus:outline-none rounded px-1.5 py-0.5 text-xs text-slate-800 font-medium font-sans';
      textContainer.replaceChild(input, titleSpan);
      actions.classList.add('hidden');
      input.focus();
      input.select();

      const commit = () => {
        const val = input.value.trim();
        if (val && val !== session.title) {
          session.title = val;
          saveSessions(state.sessions);
          showToast('Session renamed!');
        }
        isRenaming = false;
        renderSessionList();
      };

      input.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') { ev.preventDefault(); commit(); }
        if (ev.key === 'Escape') { ev.preventDefault(); isRenaming = false; renderSessionList(); }
      });
      input.addEventListener('blur', commit);
      input.addEventListener('click', (ev) => ev.stopPropagation());
    });

    actions.querySelector('.delete-btn')!.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteSession(session.id);
    });

    card.addEventListener('click', () => { if (!isRenaming) selectSession(session.id); });
    container.appendChild(card);
  });
}

export function createNewSession(): void {
  const id = generateId();
  state.sessions.unshift({ id, title: 'New Code Session', language: 'javascript', messages: [] });
  state.currentSessionId = id;
  state.activeLanguage = 'javascript';
  saveSessions(state.sessions);
  renderSessionList();
  renderCurrentSessionChat();
  showToast('Created a new code session!');
}

export function deleteSession(id: string): void {
  state.sessions = state.sessions.filter((s) => s.id !== id);
  if (state.currentSessionId === id) {
    if (state.sessions.length > 0) {
      state.currentSessionId = state.sessions[0].id;
      state.activeLanguage = state.sessions[0].language;
    } else {
      createNewSession();
      return;
    }
  }
  saveSessions(state.sessions);
  renderSessionList();
  renderCurrentSessionChat();
  showToast('Session removed', true);
}

export function selectSession(id: string): void {
  const session = state.sessions.find((s) => s.id === id);
  if (!session) return;
  state.currentSessionId = id;
  state.activeLanguage = session.language;
  renderSessionList();
  renderCurrentSessionChat();

  const sidebar = document.getElementById('sidebarPanel');
  const backdrop = document.getElementById('sidebarBackdrop');
  sidebar?.classList.remove('open');
  backdrop?.classList.add('hidden');
}

export function initSidebar(): void {
  document.getElementById('btnNewSession')?.addEventListener('click', createNewSession);

  document.getElementById('btnMobileSidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebarPanel')?.classList.add('open');
    document.getElementById('sidebarBackdrop')?.classList.remove('hidden');
  });

  const closeDrawer = () => {
    document.getElementById('sidebarPanel')?.classList.remove('open');
    document.getElementById('sidebarBackdrop')?.classList.add('hidden');
  };

  document.getElementById('btnMobileSidebarClose')?.addEventListener('click', closeDrawer);
  document.getElementById('sidebarBackdrop')?.addEventListener('click', closeDrawer);
}
