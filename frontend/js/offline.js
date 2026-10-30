if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(console.warn);
}

// Cache offline simples dos dados
window.addEventListener('online', () => console.log('Online'));
window.addEventListener('offline', () => alert('Você está offline. Algumas funções podem ficar indisponíveis.'));