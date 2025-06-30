// Use relative URLs in development to leverage Vite proxy, relative URLs in production for same-origin deployment
const BASE = import.meta.env.DEV ? '' : (import.meta.env.VITE_BACKEND_URL || '');
const json = r => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)));

export const getHouseSystems = () =>
  fetch(`${BASE}/api/house-systems`).then(json);

export const calculateChart = body =>
  fetch(`${BASE}/api/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(json);
