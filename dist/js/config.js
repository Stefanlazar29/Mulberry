/**
 * API base pentru Mulberry. Pe domeniul de producție indică backend-ul Railway.
 */
(function () {
  function resolveMulberryApiBase() {
    var host =
      typeof window !== 'undefined' && window.location && window.location.hostname
        ? String(window.location.hostname).toLowerCase()
        : '';

    if (host.includes('mulberry.autos')) {
      return 'https://mulberry-production-d9db.up.railway.app';
    }

    return 'http://127.0.0.1:9000';
  }

  window.Config = window.Config || {};
  window.Config.apiBaseUrl = resolveMulberryApiBase();
})();
