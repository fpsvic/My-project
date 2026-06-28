import { showToast } from './toast';

export function initSplash(): void {
  const splash = document.getElementById('splashScreen');
  const enterBtn = document.getElementById('btnEnterStudio') as HTMLButtonElement | null;
  const returnBtn = document.getElementById('btnReturnToSplash');
  const progressBar = document.getElementById('splashProgressBar');

  if (progressBar) progressBar.style.width = '100%';

  if (enterBtn) {
    enterBtn.disabled = false;
    enterBtn.addEventListener('click', () => {
      splash?.classList.add('translate-y-full', 'opacity-0', 'pointer-events-none');
      showToast('Welcome to ForgeAI Studio!');
    });
  }

  if (returnBtn) {
    returnBtn.addEventListener('click', () => {
      splash?.classList.remove('translate-y-full', 'opacity-0', 'pointer-events-none');
    });
  }
}
