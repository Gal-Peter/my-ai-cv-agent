/**
 * Dedicated E2E Communication Hub for the AI CV Agent API
 */
const API_BASE = 'http://localhost:8000/api';

export async function uploadCvFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Data corruption during transfer');
  }

  return response.json();
}

export async function sendAgentPrompt(message) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'API socket failed to return reasoning vectors');
  }

  return response.json();
}
