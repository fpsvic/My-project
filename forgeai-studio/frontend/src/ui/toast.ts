export function showToast(message: string, isWarning = false): void {
  const el = document.getElementById('toastNotification');
  const msgEl = document.getElementById('toastMessage');
  if (!el || !msgEl) return;

  msgEl.innerText = message;
  const icon = el.querySelector('i');
  if (icon) {
    icon.className = isWarning
      ? 'fa-solid fa-circle-exclamation text-rose-500 text-xs'
      : 'fa-solid fa-circle-check text-emerald-500 text-xs';
  }

  el.classList.remove('translate-y-12', 'opacity-0');
  el.classList.add('translate-y-0', 'opacity-100');

  setTimeout(() => {
    el.classList.remove('translate-y-0', 'opacity-100');
    el.classList.add('translate-y-12', 'opacity-0');
  }, 2500);
}
