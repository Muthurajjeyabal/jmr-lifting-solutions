/* JMR PWA registration + install prompt handler
   Loaded on every page. Safe: no-ops if SW unsupported. */
(function () {
  'use strict';

  // Only register on HTTPS or localhost (SW requirement)
  if (!('serviceWorker' in navigator)) return;

  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then(function (reg) {
        // Auto-update: check for new SW every 60 min while tab is open
        setInterval(function () {
          reg.update().catch(function () {});
        }, 60 * 60 * 1000);

        // If a new SW is waiting, activate it silently on next navigation
        if (reg.waiting) reg.waiting.postMessage('SKIP_WAITING');
        reg.addEventListener('updatefound', function () {
          var newWorker = reg.installing;
          if (!newWorker) return;
          newWorker.addEventListener('statechange', function () {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              newWorker.postMessage('SKIP_WAITING');
            }
          });
        });
      })
      .catch(function (err) {
        console.warn('[JMR] SW registration failed:', err);
      });
  });

  // Reload once when the controlling SW changes (silent update)
  var refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (refreshing) return;
    refreshing = true;
    // Only reload if the user has been idle for a moment
    // to avoid disrupting active interactions.
    if (document.visibilityState === 'hidden') window.location.reload();
  });

  /* --- Optional: capture install prompt so we can show a subtle install
         button in the future. For now we just prevent Chrome's default
         mini-infobar from appearing on desktop. --- */
  window.addEventListener('beforeinstallprompt', function (e) {
    // Stash so it can be triggered by a page CTA in a later iteration
    window.__jmrDeferredInstall = e;
  });
})();
