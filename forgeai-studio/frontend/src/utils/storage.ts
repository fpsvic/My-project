import type { Session, Mode, Workspace } from '../types';

const SESSIONS_KEY = 'forgeai_sessions';
const MODE_KEY = 'forgeai_active_mode';
const WORKSPACE_KEY = 'forgeai_active_workspace';

export function loadSessions(): Session[] {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY);
    if (!raw) return [];
    const sessions = JSON.parse(raw) as Session[];
    // Back-compat: assign workspace to legacy sessions that don't have one
    return sessions.map(s => ({ ...s, workspace: s.workspace ?? 'chat' }));
  } catch {
    return [];
  }
}

export function saveSessions(sessions: Session[]): void {
  try {
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
  } catch {}
}

export function loadActiveMode(): Mode | null {
  return (localStorage.getItem(MODE_KEY) as Mode) || null;
}

export function saveActiveMode(mode: Mode): void {
  try {
    localStorage.setItem(MODE_KEY, mode);
  } catch {}
}

export function loadActiveWorkspace(): Workspace {
  return (localStorage.getItem(WORKSPACE_KEY) as Workspace) || 'chat';
}

export function saveActiveWorkspace(ws: Workspace): void {
  try {
    localStorage.setItem(WORKSPACE_KEY, ws);
  } catch {}
}
