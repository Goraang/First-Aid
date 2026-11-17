import { uploadFile } from './api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

export const analyzeSkinImage = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${API_BASE_URL}/api/dermatology/analyze`, {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to analyze image');
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || 'Skin analysis failed');
  }
};

export const getSkinConditions = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dermatology/conditions`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch conditions');
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch skin conditions');
  }
};
