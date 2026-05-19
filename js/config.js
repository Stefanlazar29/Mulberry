/**
 * API base pentru Mulberry.
 * Producție (mulberry.autos) → Railway.
 * Localhost                  → FastAPI local pe portul 9000.
 * Altele (incl. Hetzner)     → același origin → nginx proxiază intern la api:10000.
 */
(function () {
  function resolveMulberryApiBase() {
    const host = window.location.hostname;

    if (host.includes('mulberry.autos')) {
      return 'https://mulberry-production-d9db.up.railway.app';
    }

    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://127.0.0.1:9000';
    }

    return window.location.origin;
  }

  window.Config = window.Config || {};
  window.Config.apiBaseUrl = resolveMulberryApiBase();
})();
