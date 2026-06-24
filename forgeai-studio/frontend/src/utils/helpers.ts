export function escapeHTML(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function generateId(): string {
  return 'session_' + Date.now();
}

export function getLanguageIconHTML(lang: string): string {
  const icons: Record<string, string> = {
    javascript: 'fa-brands fa-js text-yellow-500',
    typescript: 'fa-solid fa-code text-blue-500',
    java: 'fa-brands fa-java text-orange-500',
    golang: 'fa-brands fa-golang text-cyan-500',
    cpp: 'fa-solid fa-cube text-indigo-500',
    c: 'fa-solid fa-microchip text-slate-500',
    csharp: 'fa-solid fa-hashtag text-purple-500',
    kotlin: 'fa-solid fa-terminal text-purple-600',
    lua: 'fa-solid fa-moon text-blue-600',
    luau: 'fa-solid fa-star text-indigo-400',
    matlab: 'fa-solid fa-calculator text-red-600',
    python: 'fa-brands fa-python text-sky-500',
    r: 'fa-solid fa-chart-line text-blue-700',
    ruby: 'fa-solid fa-gem text-rose-500',
    rust: 'fa-solid fa-gear text-orange-600',
    swift: 'fa-brands fa-swift text-orange-500',
  };
  return `<i class="${icons[lang] ?? 'fa-regular fa-message text-slate-400'} shrink-0 text-sm"></i>`;
}
