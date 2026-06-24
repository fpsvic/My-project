import { escapeHTML } from '../utils/helpers';

function renderCard(type: string, content: string): string {
  const parts = content.split('|').reduce<Record<string, string>>((acc, part) => {
    const idx = part.indexOf(':');
    if (idx !== -1) {
      acc[part.slice(0, idx).trim()] = part.slice(idx + 1).trim();
    }
    return acc;
  }, {});

  if (type === 'MATH_CARD') {
    const { formula = '', result = '', style = 'indigo' } = parts;
    if (style === 'emerald') {
      return `<div class="bg-emerald-50/60 border border-emerald-100/50 rounded-xl p-4 my-3 text-center shadow-sm max-w-sm mx-auto">
        <div class="text-2xl font-bold text-emerald-600 font-mono">${result}</div>
      </div>`;
    }
    return `<div class="bg-indigo-50/60 border border-indigo-100/50 rounded-xl p-5 my-4 text-center shadow-sm max-w-md mx-auto">
      <div class="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1">Formula</div>
      <div class="text-sm font-mono text-slate-600 mb-2">${formula}</div>
      <div class="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1">Result</div>
      <div class="text-3xl font-bold text-indigo-600 font-mono">${result}</div>
    </div>`;
  }

  if (type === 'COSMIC_CARD') {
    const { formula = '', result = '', style = 'indigo' } = parts;
    const isEmerald = style === 'emerald';
    const border = isEmerald ? 'border-emerald-500/30' : 'border-indigo-500/30';
    const bg = isEmerald ? 'bg-emerald-950/20' : 'bg-indigo-950/20';
    const text = isEmerald ? 'text-emerald-500' : 'text-indigo-500';
    return `<div class="${bg} border-2 ${border} rounded-2xl p-5 my-4 text-center max-w-md mx-auto">
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1 flex items-center justify-center space-x-1">
        <i class="fa-solid fa-satellite-dish animate-pulse"></i><span>Telemetry constant</span>
      </div>
      <div class="text-xs font-mono text-slate-500 mb-3">${formula}</div>
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1">Observation value</div>
      <div class="text-3xl font-bold ${text} font-mono tracking-tight">${result}</div>
    </div>`;
  }

  if (type === 'EARTH_CARD') {
    const { topic = '', value = '', style = 'emerald' } = parts;
    const styleMap: Record<string, [string, string, string]> = {
      emerald: ['border-emerald-500/30', 'bg-emerald-950/10', 'text-emerald-600'],
      indigo: ['border-indigo-500/30', 'bg-indigo-950/10', 'text-indigo-600'],
      rose: ['border-rose-500/30', 'bg-rose-950/10', 'text-rose-600'],
      sky: ['border-sky-500/30', 'bg-sky-950/10', 'text-sky-600'],
      amber: ['border-amber-500/30', 'bg-amber-950/10', 'text-amber-600'],
    };
    const [border, bg, textCls] = styleMap[style] ?? styleMap['emerald'];
    return `<div class="${bg} border-2 ${border} rounded-2xl p-5 my-4 text-center max-w-md mx-auto">
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1 flex items-center justify-center space-x-1.5">
        <i class="fa-solid fa-earth-americas animate-pulse"></i><span>Geological Lithosphere Log</span>
      </div>
      <div class="text-xs font-mono text-slate-500 mb-3">${topic}</div>
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1">Observed Classification</div>
      <div class="text-2xl font-bold ${textCls} font-mono tracking-tight">${value}</div>
    </div>`;
  }

  if (type === 'SCIENCE_CARD') {
    const { topic = '', value = '', style = 'violet' } = parts;
    const styleMap: Record<string, [string, string, string, string]> = {
      violet:  ['border-violet-500/30',  'bg-violet-950/10',  'text-violet-600',  'fa-atom'],
      fuchsia: ['border-fuchsia-500/30', 'bg-fuchsia-950/10', 'text-fuchsia-600', 'fa-dna'],
      amber:   ['border-amber-500/30',   'bg-amber-950/10',   'text-amber-600',   'fa-flask'],
      rose:    ['border-rose-500/30',    'bg-rose-950/10',    'text-rose-600',    'fa-fire-burner'],
      sky:     ['border-sky-500/30',     'bg-sky-950/10',     'text-sky-600',     'fa-temperature-quarter'],
      emerald: ['border-emerald-500/30', 'bg-emerald-950/10', 'text-emerald-600', 'fa-infinity'],
    };
    const [border, bg, textCls, icon] = styleMap[style] ?? styleMap['violet'];
    return `<div class="${bg} border-2 ${border} rounded-2xl p-5 my-4 text-center max-w-md mx-auto">
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1 flex items-center justify-center space-x-1.5">
        <i class="fa-solid ${icon} animate-pulse"></i><span>Quantum &amp; Fundamental Telemetry</span>
      </div>
      <div class="text-xs font-mono text-slate-500 mb-3">${topic}</div>
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1">Constant / Value</div>
      <div class="text-2xl font-bold ${textCls} font-mono tracking-tight">${value}</div>
    </div>`;
  }

  if (type === 'HISTORY_CARD') {
    const { topic = '', value = '' } = parts;
    return `<div class="bg-amber-50/60 border-2 border-amber-600/20 rounded-2xl p-5 my-4 text-center max-w-md mx-auto">
      <div class="text-[9px] font-mono text-amber-800 uppercase tracking-widest mb-1 flex items-center justify-center space-x-1.5">
        <i class="fa-solid fa-scroll animate-pulse"></i><span>Presidential &amp; Constitutional Archives</span>
      </div>
      <div class="text-xs font-mono text-slate-500 mb-3">${topic}</div>
      <div class="text-[9px] font-mono text-slate-400 uppercase tracking-widest mb-1">Precedent Established</div>
      <div class="text-xl font-bold text-amber-900 font-mono tracking-tight">${value}</div>
    </div>`;
  }

  return '';
}

export function formatMarkdown(text: string): string {
  let out = escapeHTML(text);
  const blocks: string[] = [];

  // Extract code blocks
  out = out.replace(/```(\w*)\n([\s\S]*?)```/g, (_match, lang, code) => {
    const ph = `__BLOCK_${blocks.length}__`;
    const displayLang = lang ? lang.toUpperCase() : 'SOURCE CODE';
    const cleanCode = code.trim();
    const isGame =
      displayLang === 'HTML' &&
      (cleanCode.includes('gameCanvas') ||
        cleanCode.includes('birdY') ||
        cleanCode.includes('ballDX') ||
        cleanCode.includes('makeMove'));

    const isApp =
      !isGame &&
      displayLang === 'HTML' &&
      (cleanCode.includes('<!DOCTYPE html>') || cleanCode.includes('<html'));

    const playBtn = isGame
      ? `<button type="button" onclick="window.openSandboxFromCode(this)"
           class="hover:text-white text-indigo-400 font-semibold transition flex items-center space-x-1.5 border border-indigo-500/30 hover:border-indigo-400/50 bg-indigo-950/20 px-2.5 py-1 rounded-md">
           <i class="fa-solid fa-gamepad text-[10px]"></i><span class="text-[9px]">Play Game</span>
         </button>`
      : isApp
      ? `<button type="button" onclick="window.openSandboxFromCode(this)"
           class="hover:text-white text-emerald-400 font-semibold transition flex items-center space-x-1.5 border border-emerald-500/30 hover:border-emerald-400/50 bg-emerald-950/20 px-2.5 py-1 rounded-md">
           <i class="fa-solid fa-rocket text-[10px]"></i><span class="text-[9px]">Launch App</span>
         </button>`
      : '';

    blocks.push(`<div class="my-4 bg-slate-900 rounded-xl border border-slate-950 overflow-hidden font-mono text-[11px] shadow-md text-left">
      <div class="bg-slate-950/40 px-4 py-2.5 border-b border-slate-950/50 flex justify-between items-center text-slate-400">
        <span class="text-[10px] font-bold tracking-wider text-slate-500">${displayLang}</span>
        <div class="flex items-center space-x-2">
          ${playBtn}
          <button type="button" onclick="window.copyCodeSnippet(this)"
            class="hover:text-white transition flex items-center space-x-1 border border-slate-800 bg-slate-950/40 px-2 py-1 rounded">
            <i class="fa-regular fa-copy text-[10px]"></i><span class="text-[9px]">Copy Code</span>
          </button>
        </div>
      </div>
      <pre class="p-4 overflow-x-auto text-slate-200 leading-normal"><code>${cleanCode}</code></pre>
    </div>`);
    return ph;
  });

  // Typo alert tokens
  out = out.replace(
    /\[TYPO_ALERT:\s*(.*?)\s*\|\s*(.*?)\s*\]/g,
    (_m, original, corrected) =>
      `<div class="bg-amber-50 border border-amber-200/60 rounded-xl p-3 mb-3 flex items-center space-x-2.5 text-xs text-amber-800 shadow-sm">
        <i class="fa-solid fa-wand-magic-sparkles text-amber-500 text-xs shrink-0"></i>
        <span>Auto-corrected: <span class="font-semibold font-mono underline decoration-wavy decoration-amber-500">${original}</span>
        → <span class="font-semibold font-mono text-indigo-600">${corrected}</span></span>
      </div>`,
  );

  // Special card tokens
  out = out.replace(
    /\[(MATH_CARD|COSMIC_CARD|EARTH_CARD|SCIENCE_CARD|HISTORY_CARD):\s*([\s\S]*?)\]/g,
    (_m, type, content) => renderCard(type, content),
  );

  // Restore code blocks
  blocks.forEach((html, i) => {
    out = out.replace(`__BLOCK_${i}__`, html);
  });

  // Inline formatting
  out = out
    .replace(/`([^`\n]+)`/g, '<code class="bg-slate-100 border border-slate-200/80 px-1.5 py-0.5 rounded text-indigo-600 font-mono text-xs">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-slate-900">$1</strong>')
    .replace(/### (.+)/g, '<h3 class="text-base font-bold text-slate-900 mt-4 mb-2">$1</h3>')
    .replace(/^\s*[-*]\s+(.+)$/gm, '<li class="ml-4 list-disc text-slate-600">$1</li>')
    .replace(/^\d+\.\s+(.+)$/gm, '<li class="ml-4 list-decimal text-slate-600">$1</li>')
    .replace(/\n/g, '<br>');

  return out;
}
