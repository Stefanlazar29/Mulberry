/**
 * config.js — Centralized API endpoint configuration
 *
 * Detects the current host and returns the appropriate API base URL:
 *   - mulberry.autos  → https://mulberry.autos  (production)
 *   - localhost / 127.0.0.1 → http://localhost:8000  (local development)
 *   - any other host  → https://<host>  (Railway preview / staging domains)
 */

function getApiBaseUrl() {
  const host = window.location.hostname;

  if (host.includes('mulberry.autos')) {
    return 'https://mulberry.autos';
  }

  if (host === 'localhost' || host === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // Fallback for Railway preview/staging domains
  return `https://${host}`;
}

// Eagerly-evaluated constant for convenience — import once, use everywhere.
const API_BASE_URL = getApiBaseUrl();
