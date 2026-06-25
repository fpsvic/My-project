export interface Message {
  role: 'user' | 'assistant';
  text: string;
}

export interface Session {
  id: string;
  title: string;
  language: string;
  messages: Message[];
}

export type Mode = 'forge_code' | 'forge_thinking' | 'forge_instant';

export interface ModeConfig {
  text: string;
  icon: string;
  color: string;
  bg: string;
}

export interface ChatRequest {
  query: string;
  mode: Mode;
  history: Array<{ role: string; text: string }>;
  quick_mode?: boolean;
}

export interface ChatResponse {
  text: string;
  corrections: Array<{ original: string; corrected: string }>;
}
