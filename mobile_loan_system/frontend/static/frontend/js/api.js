/**
 * Thin wrapper around fetch() for talking to our DRF API using the
 * logged-in Django session (SessionAuthentication) + CSRF token.
 */
const API = {
  base: '/api',

  async request(path, { method = 'GET', body = null } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (method !== 'GET') headers['X-CSRFToken'] = window.CSRF_TOKEN;

    const res = await fetch(`${this.base}${path}`, {
      method,
      headers,
      credentials: 'same-origin',
      body: body ? JSON.stringify(body) : null,
    });

    let data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }

    if (!res.ok) {
      const err = new Error('API request failed');
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  },

  get(path) { return this.request(path); },
  post(path, body) { return this.request(path, { method: 'POST', body }); },
  patch(path, body) { return this.request(path, { method: 'PATCH', body }); },
  put(path, body) { return this.request(path, { method: 'PUT', body }); },
  delete(path) { return this.request(path, { method: 'DELETE' }); },
};

/** Render a friendly error string from a DRF validation error payload. */
function formatApiError(err) {
  if (!err.data) return 'Something went wrong. Please try again.';
  if (typeof err.data.detail === 'string') return err.data.detail;
  return Object.entries(err.data)
    .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
    .join(' | ');
}

function money(value) {
  const n = Number(value || 0);
  return '₹' + n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}
