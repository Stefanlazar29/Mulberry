/**
 * API base pentru Mulberry.
 * Producție (mulberry.autos) → Railway.
 * Hetzner (46.225.100.151)   → FastAPI expus direct pe portul 9000.
 * Localhost                  → FastAPI local pe portul 9000.
 * Altele                     → același origin (nginx reverse-proxy).
 */
(function () {
  function resolveMulberryApiBase() {
    const host = window.location.hostname;

    if (host.includes('mulberry.autos')) {
      return 'https://mulberry-production-d9db.up.railway.app';
    }

    if (host === '46.225.100.151') {
      return 'http://46.225.100.151:9000';
    }

    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://127.0.0.1:9000';
    }

    return window.location.origin;
  }

  window.Config = window.Config || {};
  window.Config.apiBaseUrl = resolveMulberryApiBase();
})();
