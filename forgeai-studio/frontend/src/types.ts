export type Workspace = 'chat' | 'code';

export interface Message {
  role: 'user' | 'assistant';
  text: string;
  project_files?: ProjectFile[];
}

export interface Session {
  id: string;
  title: string;
  language: string;
  workspace: Workspace;
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
  history: Array<{ role: string; text: string; content?: string; project_files?: ProjectFile[] }>;
  quick_mode?: boolean;
  workspace?: string;
}

export interface ProjectFile {
  name: string;
  content: string;
  language: string;
}

export interface ChatResponse {
  text: string;
  corrections: Array<{ original: string; corrected: string }>;
  web_searched?: boolean;
  project_files?: ProjectFile[];
}
