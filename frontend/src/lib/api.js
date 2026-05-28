const API_BASE = '/api'
class ApiError extends Error { constructor(m, s) { super(m); this.status = s } }
async function request(e, o = {}) {
  const u = `${API_BASE}${e}`, c = { headers: { 'Content-Type': 'application/json', ...o.headers }, ...o };
  try {
    const r = await fetch(u, c);
    if (!r.ok) { let m = `Erro ${r.status}`; try { m = (await r.json()).detail || m } catch {} throw new ApiError(m, r.status) }
    if (r.status === 204) return null; return r.json()
  } catch (e) { if (e instanceof ApiError) throw e; throw new ApiError('Backend offline.', 0) }
}
export const createTask = (style, subject, config = {}) => request('/tasks', { method: 'POST', body: JSON.stringify({ style, subject, config }) });
export const listTasks = (limit = 50) => request(`/tasks?limit=${limit}`);
export const getTask = (id) => request(`/tasks/${id}`);
export const deleteTask = (id) => request(`/tasks/${id}`, { method: 'DELETE' });
export const listStyles = () => request('/styles');
export const checkHealth = () => request('/health');
export function createTaskStream(id, onMsg, onErr, onClose) {
  const es = new EventSource(`/api/tasks/${id}/stream`);
  es.onmessage = (e) => { try { const d = JSON.parse(e.data); onMsg(d); if (d.status === 'done' || d.status === 'failed') { es.close(); if (onClose) onClose() } } catch {} };
  es.onerror = (e) => { es.close(); if (onErr) onErr(e) };
  return es
}
export const getVideoUrl = (id) => `/api/tasks/${id}/video`;
