/*
const CACHE = 'escola-v1';
const ARQUIVOS = [
  '/', '/login.html', '/dashboard.html',
  '/css/style.css', '/css/splash.css',
  '/js/login.js', '/js/dashboard.js', '/js/offline.js',
  '/assets/logo.svg'
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARQUIVOS)));
});
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
}); */

// Desativado temporariamente para evitar problemas de cache durante o desenvolvimento
// if ('serviceWorker' in navigator) {
//   navigator.serviceWorker.register('sw.js').catch(console.warn);
// }

window.addEventListener('online', () => console.log('Online'));
window.addEventListener('offline', () => alert('Você está offline. Algumas funções podem ficar indisponíveis.'));