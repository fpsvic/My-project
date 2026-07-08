const jungleStyles: string = `
body { font-family: 'Inter', system-ui, -apple-system, sans-serif; margin: 0; background-color: #0b0d10; color: #d1d5db; display: flex; height: 100vh; overflow: hidden; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0b0d10; }
::-webkit-scrollbar-thumb { background: #1b2221; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #528b74; }
.splash-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #101715 0%, #040608 100%); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 9999; transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.4s; opacity: 1; visibility: visible; }
.splash-screen.fade-out { opacity: 0; visibility: hidden; }
.splash-content { text-align: center; max-width: 500px; padding: 2rem; display: flex; flex-direction: column; align-items: center; }
.splash-logo { margin-bottom: 2.5rem; filter: drop-shadow(0 0 25px rgba(116, 168, 147, 0.35)); width: 110px !important; height: 110px !important; flex-shrink: 0 !important; }
.splash-title { font-family: 'Inter', sans-serif; font-size: 3.5rem; font-weight: 800; margin: 0 0 1rem 0; letter-spacing: -1.5px; color: #e2f1ec; }
.splash-subtitle { font-size: 1.05rem; color: #7b8e87; margin: 0 0 3rem 0; font-weight: 400; line-height: 1.6; max-width: 440px; }
.enter-btn { background-color: #2f443a; color: #e2f1ec; border: 1px solid #415c4f; padding: 14px 44px; font-size: 1rem; font-weight: 600; border-radius: 50px; cursor: pointer; box-shadow: 0 8px 24px rgba(47, 68, 58, 0.25); transition: transform 0.2s, box-shadow 0.2s, background-color 0.2s, border-color 0.2s; outline: none; }
.enter-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(47, 68, 58, 0.4); background-color: #385246; border-color: #528b74; }
.enter-btn:active { transform: translateY(1px); }
.projects-dashboard { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0b0d10; z-index: 9000; display: flex; flex-direction: column; box-sizing: border-box; padding: 40px 60px; overflow-y: auto; transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.4s; opacity: 0; visibility: hidden; }
.projects-dashboard.show { opacity: 1; visibility: visible; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; border-bottom: 1px solid #1c2321; padding-bottom: 20px; flex-wrap: wrap; gap: 20px; }
.dashboard-header-left { display: flex; align-items: center; gap: 20px; }
.dashboard-header h1 { margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #74a896 0%, #aed9cb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }
.dashboard-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; padding-bottom: 40px; }
.project-card { background-color: #111413; border: 1px solid #1c2321; border-radius: 12px; padding: 25px; cursor: pointer; position: relative; display: flex; flex-direction: column; justify-content: space-between; height: 180px; box-sizing: border-box; transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s, box-shadow 0.3s; }
.project-card:hover { transform: translateY(-5px); border-color: #74a896; box-shadow: 0 10px 25px rgba(116, 168, 150, 0.15); }
.project-card h3 { margin: 0; font-size: 1.3rem; font-weight: 700; color: #ffffff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.project-meta { font-size: 0.85rem; color: #7b8e87; display: flex; flex-direction: column; gap: 4px; }
.project-card-actions { position: absolute; top: 15px; right: 15px; display: flex; gap: 8px; opacity: 0; transition: opacity 0.2s ease; }
.project-card:hover .project-card-actions { opacity: 1; }
.new-project-card { background-color: transparent; border: 2px dashed #1c2321; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; height: 180px; transition: border-color 0.3s, background 0.3s; }
.new-project-card:hover { border-color: #74a896; background-color: rgba(116, 168, 150, 0.03); }
.new-project-card .plus-icon { font-size: 2.5rem; color: #74a896; margin-bottom: 10px; line-height: 1; }
.new-project-card span { font-weight: 600; font-size: 1rem; color: #7b8e87; }
.workspace-container { display: flex; width: 100vw; height: 100vh; overflow: hidden; }
.sidebar { width: 260px; background-color: #111413; border-right: 1px solid #1c2321; display: flex; flex-direction: column; }
.sidebar-tabs { display: flex; background-color: #161a19; }
.sidebar-tab { flex: 1; padding: 12px 15px; font-size: 0.75rem; color: #727e8c; cursor: pointer; text-transform: uppercase; letter-spacing: 1.2px; border-top: 2px solid transparent; text-align: center; transition: all 0.2s; }
.sidebar-tab.active { color: #ffffff; border-top: 2px solid #528b74; background-color: #111413; }
.sidebar-section-header { padding: 10px 15px; font-size: 0.75rem; color: #849690; text-transform: uppercase; letter-spacing: 1px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #1c2321; background-color: #141917; font-weight: 700; }
.sidebar-section-header button { background: none; border: none; color: #74a896; font-size: 1.2rem; cursor: pointer; padding: 0; display: flex; align-items: center; line-height: 1; transition: color 0.15s, transform 0.1s; }
.sidebar-section-header button:hover { color: #ffffff; transform: scale(1.1); }
.file-list { list-style: none; padding: 10px 0; margin: 0; overflow-y: auto; flex: 1; }
.file-list li { padding: 8px 15px 8px 25px; font-size: 0.9rem; color: #9ca3af; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.15s; }
.file-list li:hover { background-color: #161c1a; color: #e2f1ec; }
.file-list li.active { background-color: #1c2522; color: #ffffff; border-left: 3px solid #528b74; padding-left: 22px; }
.file-item-actions { display: none; gap: 8px; }
.file-list li:hover .file-item-actions { display: flex; }
.action-btn { background: none; border: none; color: #5c6875; cursor: pointer; padding: 0 2px; font-size: 0.85rem; transition: color 0.15s, transform 0.1s; }
.action-btn:hover { color: #ffffff; transform: scale(1.15); }
.action-btn.delete:hover { color: #cf6679; }
.main-content { flex: 1; display: flex; flex-direction: column; background-color: #0b0d10; position: relative; }
.editor-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background-color: #111413; border-bottom: 1px solid #1c2321; }
.editor-header h2 { margin: 0; font-size: 0.95rem; font-weight: 600; color: #aed9cb; }
.header-left { display: flex; align-items: center; gap: 15px; }
.header-right { display: flex; align-items: center; gap: 10px; }
.exit-hub-btn { background-color: #161c1a; color: #a4b3b0; border: 1px solid #232d2a; padding: 8px 16px; font-size: 0.85rem; font-weight: 600; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s ease; }
.exit-hub-btn:hover { background-color: #1c2522; color: #ffffff; border-color: #74a896; box-shadow: 0 0 10px rgba(116, 168, 150, 0.25); }
#loc-display { color: #849690; font-size: 0.85rem; font-family: monospace; background: #0b0d10; padding: 4px 8px; border-radius: 4px; border: 1px solid #1c2321; white-space: nowrap; }
.language-selector-wrapper { position: relative; display: inline-block; }
.language-btn { padding: 7px 12px; background-color: #161c1a; color: #a4b3b0; border: 1px solid #232d2a; border-radius: 6px; cursor: pointer; text-align: left; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center; width: 170px; gap: 5px; transition: all 0.2s; }
.language-btn:hover { background-color: #1c2522; color: #ffffff; border-color: #415c4f; }
#current-language-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
#lang-picker-screen { display: none; position: fixed; inset: 0; z-index: 300; background-color: #0d1210; flex-direction: column; }
#lang-picker-screen.visible { display: flex; }
#lang-picker-header { display: flex; align-items: center; gap: 16px; padding: 14px 20px; background-color: #111a17; border-bottom: 1px solid #1c2321; flex-shrink: 0; }
#lang-picker-back { background: none; border: 1px solid #2a3d35; color: #74a896; padding: 7px 14px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: all 0.15s; }
#lang-picker-back:hover { background-color: #1c2522; color: #aed9cb; }
#lang-picker-title { font-size: 1rem; font-weight: 700; color: #aed9cb; letter-spacing: 0.5px; white-space: nowrap; }
#lang-picker-search { flex: 1; background-color: #0d1210; border: 1px solid #232d2a; border-radius: 6px; color: #c8ddd8; padding: 7px 12px; font-size: 0.85rem; outline: none; font-family: inherit; transition: border-color 0.2s; }
#lang-picker-search:focus { border-color: #528b74; }
#lang-picker-grid { flex: 1; overflow-y: auto; padding: 20px; display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.lang-picker-card { background-color: #111a17; border: 1px solid #1c2321; border-radius: 10px; padding: 18px 14px; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 10px; transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s; }
.lang-picker-card:hover { border-color: #528b74; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
.lang-picker-card.selected { border-color: #74a896; background-color: #13201b; }
.lang-picker-icon { font-size: 2rem; line-height: 1; }
.lang-picker-name { font-size: 0.85rem; font-weight: 600; color: #aed9cb; text-align: center; }
.editor-wrapper { display: flex; flex: 1; position: relative; overflow: hidden; background-color: #0b0d10; }
#line-gutter { padding: 20px 10px 20px 15px; background-color: #080a0d; color: #35453e; font-family: 'Fira Code', 'Consolas', monospace; font-size: 14px; line-height: 22px; text-align: right; user-select: none; border-right: 1px solid #1c2321; min-width: 45px; white-space: pre; overflow: hidden; box-sizing: border-box; }
#editor-container { position: relative; flex: 1; height: 100%; overflow: hidden; }
#highlight-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; margin: 0; padding: 20px; box-sizing: border-box; font-family: 'Fira Code', 'Consolas', monospace; font-size: 14px; line-height: 22px; white-space: pre; overflow: hidden; pointer-events: none; color: #d1d5db; background: transparent; z-index: 1; tab-size: 4; word-wrap: normal; }
#code-editor { position: absolute; top: 0; left: 0; width: 100%; height: 100%; margin: 0; padding: 20px; box-sizing: border-box; background: transparent; color: transparent !important; -webkit-text-fill-color: transparent !important; caret-color: #74a896; font-family: 'Fira Code', 'Consolas', monospace; font-size: 14px; line-height: 22px; border: none; resize: none; outline: none; tab-size: 4; overflow-y: auto; overflow-x: auto; white-space: pre; z-index: 2; word-wrap: normal; }
#code-editor::-webkit-scrollbar { width: 10px; height: 10px; }
#code-editor::-webkit-scrollbar-track { background: #080a0d; }
#code-editor::-webkit-scrollbar-thumb { background: #1c2522; border: 2px solid #080a0d; border-radius: 5px; }
#code-editor::-webkit-scrollbar-thumb:hover { background: #528b74; }
.token-keyword { color: #FFB86C; }
.token-string { color: #06CF7A; }
.token-comment { color: #6272A4; font-style: italic; }
.token-number { color: #FF79C6; }
.token-type { color: #8BE9FD; }
.token-fn { color: #f1fa8c; }
.token-builtin { color: #bd93f9; }
.token-op { color: #FF5555; }
.token-punct { color: #7f848e; }
.token-attr { color: #FFB86C; }
.token-tag { color: #FF79C6; }
.token-property { color: #FFB86C; }
.token-value { color: #FFB86C; }
.token-decorator { color: #bd93f9; font-style: italic; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.85); display: none; justify-content: center; align-items: center; z-index: 10000; backdrop-filter: blur(6px); }
.modal-overlay.show { display: flex; }
.modal-card { background-color: #111413; border: 1px solid #232d2a; border-radius: 12px; width: 360px; padding: 25px; box-shadow: 0 15px 40px rgba(0,0,0,0.8); animation: modalScale 0.2s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes modalScale { from { transform: scale(0.92); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.modal-card h3 { margin: 0; font-size: 1.25rem; font-weight: 700; color: #74a896; }
.modal-body-text { font-size: 0.9rem; color: #94a3b8; margin-bottom: 15px; line-height: 1.5; }
.modal-card input { width: 100%; background-color: #0b0d10; border: 1px solid #232d2a; border-radius: 6px; padding: 10px 12px; color: #ffffff; font-size: 0.9rem; outline: none; box-sizing: border-box; margin-bottom: 20px; }
.modal-card input:focus { border-color: #74a896; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.modal-btn { padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600; border: none; outline: none; transition: all 0.2s; }
.modal-btn.cancel { background-color: #161c1a; color: #a4b3b0; }
.modal-btn.cancel:hover { background-color: #232d2a; color: #ffffff; }
.modal-btn.confirm { background-color: #4b7a69; color: #ffffff; }
.modal-btn.confirm:hover { background-color: #385c4f; }
#template-panel { display: flex; flex-direction: column; flex-shrink: 0; }
#template-panel-body { display: flex; gap: 12px; background-color: #0d1210; border-bottom: 1px solid #1c2321; overflow-x: auto; max-height: 0; overflow: hidden; transition: max-height 0.3s cubic-bezier(0.4,0,0.2,1), padding 0.3s; padding: 0 16px; }
#template-panel-body.open { max-height: 160px; padding: 14px 16px; }
.template-card { flex: 0 0 180px; background-color: #111a17; border: 1px solid #1c2321; border-radius: 10px; padding: 14px; cursor: pointer; transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s; }
.template-card:hover { border-color: #528b74; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(82,139,116,0.2); }
.template-card-icon { font-size: 1.5rem; margin-bottom: 6px; }
.template-card-name { font-size: 0.9rem; font-weight: 700; color: #aed9cb; margin-bottom: 4px; }
.template-card-desc { font-size: 0.75rem; color: #5c7a6e; line-height: 1.4; }
#toast-container { position: fixed; bottom: 25px; right: 25px; z-index: 10005; display: flex; flex-direction: column; gap: 10px; pointer-events: none; }
.jungle-toast { background-color: #111413; border: 1px solid #4b7a69; color: #e2f1ec; padding: 12px 24px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; box-shadow: 0 8px 24px rgba(0,0,0,0.5); transform: translateY(50px); opacity: 0; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); pointer-events: auto; }
.jungle-toast.show { transform: translateY(0); opacity: 1; }
#terminal-view-container { flex: 1; display: none; flex-direction: column; background-color: #06090c; font-family: 'Fira Code', 'Consolas', monospace; padding: 24px; box-sizing: border-box; overflow: hidden; cursor: text; }
#terminal-view-header { color: #528b74; font-size: 0.8rem; letter-spacing: 1.5px; border-bottom: 1px solid #14201b; padding-bottom: 12px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
#terminal-view-body { margin: 0; color: #9cb5a9; font-size: 14px; line-height: 22px; white-space: pre-wrap; word-break: break-all; flex: 1; overflow-y: auto; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.flex-1 { flex: 1; }
.shrink-0 { flex-shrink: 0; }
.hidden { display: none; }
.gap-2 { gap: 0.5rem; }
.gap-4 { gap: 1rem; }
.ml-2 { margin-left: 0.5rem; }
.ml-4 { margin-left: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.pl-3 { padding-left: 0.75rem; }
.pr-16 { padding-right: 4rem; }
.pt-2 { padding-top: 0.5rem; }
.border-t { border-top-width: 1px; border-top-style: solid; }
.border-l { border-left-width: 1px; border-left-style: solid; }
.border-none { border: none; }
.bg-transparent { background-color: transparent; }
.outline-none { outline: none; }
.font-mono { font-family: 'Fira Code', 'Consolas', monospace; }
.font-bold { font-weight: 700; }
.uppercase { text-transform: uppercase; }
.text-sm { font-size: 0.875rem; }
.select-none { user-select: none; }
.cursor-pointer { cursor: pointer; }
.overflow-hidden { overflow: hidden; }
.truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pointer-events-auto { pointer-events: auto; }
.text-rose-500 { color: #f43f5e; }
.text-emerald-400 { color: #34d399; }
.text-teal-300 { color: #5eead4; }
.animate-pulse { animation: junglePulse 1.6s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes junglePulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.55; } }
.bg-\\[\\#1c2522\\] { background-color: #1c2522; }
.text-\\[\\#74a896\\] { color: #74a896; }
.text-\\[\\#aed9cb\\] { color: #aed9cb; }
.text-\\[10px\\] { font-size: 10px; }
.border-\\[\\#528b74\\] { border-color: #528b74; }
.border-\\[\\#14201b\\] { border-color: #14201b; }
.border-\\[\\#2e3c37\\] { border-color: #2e3c37; }
.hover\\:bg-\\[\\#1a2320\\]:hover { background-color: #1a2320; }
`;

function installJungleStyles(cssText: string): void {
    const styleElement = document.createElement('style');
    styleElement.setAttribute('data-source', 'styles.ts');
    styleElement.textContent = cssText;
    document.head.appendChild(styleElement);
}

installJungleStyles(jungleStyles);
