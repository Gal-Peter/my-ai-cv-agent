// Ensure this base address matches your verified cloud run backend link perfectly
const API_BASE = 'https://cv-backend-brm46w76uq-uc.a.run.app';

export async function uploadCvFile(fileCollection) {
  const formData = new FormData();
  const targetFile = fileCollection[0] || fileCollection;
  formData.append('file', targetFile);

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

export async function sendAgentPrompt(message, cvText) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, cv_text: cvText }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'API socket failed');
  }
  return response.json();
}

// FIXED PAYLOAD: Enforces clean string variable mapping keys to match FastAPI schemas
export async function downloadCvFile(cvText) {
  const response = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_text: cvText }), // Map precisely to payload.cv_text
  });

  if (!response.ok) {
    throw new Error('Failed to generate PDF compilation stream from backend');
  }
  return response.blob();
}
