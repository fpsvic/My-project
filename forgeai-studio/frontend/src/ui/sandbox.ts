let _previewTimer: ReturnType<typeof setTimeout> | undefined;

export function openSandboxPreview(html: string): void {
  const modal = document.getElementById('sandboxModal');
  const frame = document.getElementById('sandboxFrame') as HTMLIFrameElement | null;
  const loading = document.getElementById('sandboxLoading');
  if (!modal || !frame) return;

  clearTimeout(_previewTimer);
  modal.classList.remove('hidden');
  loading?.classList.remove('hidden');
  frame.srcdoc = '';

  _previewTimer = setTimeout(() => {
    frame.srcdoc = html;
    loading?.classList.add('hidden');
  }, 80);
}

export function openSandboxFromCode(btn: HTMLElement): void {
  const container = btn.closest('.file-viewer') ?? btn.closest('.my-4');
  if (!container) return;

  const files: { name: string; content: string; language: string }[] = [];
  const panels = container.querySelectorAll<HTMLElement>('[data-panel-idx]');
  if (panels.length) {
    panels.forEach((panel) => {
      const idx = Number(panel.dataset.panelIdx);
      const tab = container.querySelector<HTMLElement>(`.tab-btn[data-idx="${idx}"] span`);
      const code = panel.querySelector('code');
      const name = tab?.textContent?.trim() ?? `file-${idx}`;
      if (code) {
        const lang = name.endsWith('.css') ? 'css' : name.endsWith('.html') ? 'html' : 'javascript';
        files.push({ name, content: code.textContent ?? '', language: lang });
      }
    });
  }

  if (files.length) {
    import('./fileViewer').then(({ stitchProject }) => {
      openSandboxPreview(stitchProject(files));
    });
    return;
  }

  const preCode = container.querySelector('pre code') as HTMLElement | null;
  if (preCode) {
    openSandboxPreview(preCode.innerText);
  }
}

export function closeSandbox(): void {
  const modal = document.getElementById('sandboxModal');
  const frame = document.getElementById('sandboxFrame') as HTMLIFrameElement | null;
  const loading = document.getElementById('sandboxLoading');
  clearTimeout(_previewTimer);
  if (modal && frame) {
    modal.classList.add('hidden');
    frame.srcdoc = '';
    loading?.classList.add('hidden');
  }
}
