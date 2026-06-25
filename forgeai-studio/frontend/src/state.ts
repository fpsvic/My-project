import type { Session, Mode, ModeConfig } from './types';

export const MODE_CONFIGS: Record<Mode, ModeConfig> = {
  forge_code: {
    text: 'Cosmos 2.8',
    icon: 'fa-code',
    color: 'text-indigo-500',
    bg: 'bg-indigo-50/40',
  },
  forge_thinking: {
    text: 'Solar 2.6',
    icon: 'fa-brain',
    color: 'text-amber-500',
    bg: 'bg-amber-50/40',
  },
  forge_instant: {
    text: 'Sprint 2.6',
    icon: 'fa-bolt',
    color: 'text-emerald-500',
    bg: 'bg-emerald-50/40',
  },
};

export const state = {
  sessions: [] as Session[],
  currentSessionId: '',
  activeMode: 'forge_code' as Mode,
  activeLanguage: 'javascript',
  quickMode: false,
};
