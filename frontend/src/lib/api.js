const API_BASE = '/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      let message;
      try {
        const json = JSON.parse(text);
        message = json.detail || json.message || `Erro ${response.status}`;
      } catch {
        message = text || `Erro ${response.status}`;
      }
      throw new ApiError(message, response.status);
    }

    if (response.status === 204) return null;

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new ApiError('Servidor offline. Verifique se o backend está rodando.', 0);
    }
    throw new ApiError('Erro de conexão com o servidor.', 0);
  }
}

export async function fetchTasks() {
  return request('/tasks');
}

export async function fetchTask(id) {
  return request(`/tasks/${id}`);
}

export async function createTask(data) {
  return request('/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteTask(id) {
  return request(`/tasks/${id}`, {
    method: 'DELETE',
  });
}

export async function fetchStyles() {
  return request('/styles');
}

export async function previewScript(data) {
  return request('/preview', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function getVideoUrl(outputPath) {
  if (!outputPath) return null;
  // If it's already a full URL, return as-is
  if (outputPath.startsWith('http')) return outputPath;
  // If it starts with /, use as path relative to API base
  if (outputPath.startsWith('/')) return `${API_BASE}${outputPath}`;
  // Otherwise, assume it's a relative path
  return `${API_BASE}/videos/${outputPath}`;
}

export function createEventSource(taskId) {
  return new EventSource(`${API_BASE}/tasks/${taskId}/stream`);
}
