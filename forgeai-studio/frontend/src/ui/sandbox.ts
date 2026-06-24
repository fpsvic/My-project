export function openSandboxFromCode(btn: HTMLElement): void {
  const container = btn.closest('.my-4');
  if (!container) return;
  const preCode = container.querySelector('pre code') as HTMLElement | null;
  if (!preCode) return;

  const modal = document.getElementById('sandboxModal');
  const frame = document.getElementById('sandboxFrame') as HTMLIFrameElement | null;
  if (modal && frame) {
    modal.classList.remove('hidden');
    frame.srcdoc = preCode.innerText;
  }
}

export function closeSandbox(): void {
  const modal = document.getElementById('sandboxModal');
  const frame = document.getElementById('sandboxFrame') as HTMLIFrameElement | null;
  if (modal && frame) {
    modal.classList.add('hidden');
    frame.srcdoc = '';
  }
}
