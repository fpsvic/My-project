import type { Session, Mode } from '../types';

const SESSIONS_KEY = 'forgeai_sessions';
const MODE_KEY = 'forgeai_active_mode';

export function loadSessions(): Session[] {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY);
    return raw ? (JSON.parse(raw) as Session[]) : [];
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
