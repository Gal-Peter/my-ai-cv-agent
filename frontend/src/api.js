const API_BASE = 'https://run.app';

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
  // Sync the current local state text over the web call to the backend container
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

export async function downloadCvFile(cvText) {
  // Triggers a stateless secure download stream by passing the modified text directly
  const response = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_text: cvText }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate PDF compilation stream');
  }
  return response.blob();
}
