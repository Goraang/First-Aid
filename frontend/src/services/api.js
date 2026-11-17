const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

export const makeRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `Request failed: ${response.statusText}`);
  }

  return response.json();
};

export const uploadFile = async (endpoint, file, additionalData = {}) => {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  
  formData.append('file', file);
  Object.keys(additionalData).forEach(key => {
    formData.append(key, additionalData[key]);
  });

  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Upload failed');
  }

  return response.json();
};
