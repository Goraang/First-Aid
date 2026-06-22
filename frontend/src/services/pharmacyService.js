export const scanPrescription = async (prescriptionFile) => {
  try {
    const formData = new FormData();
    formData.append('prescription', prescriptionFile);

    const response = await fetch('http://localhost:5000/api/pharmacy/scan-prescription', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to scan prescription');
    }

    const data = await response.json();
    return data.extracted_text;
  } catch (error) {
    throw new Error(error.message || 'Prescription scanning failed');
  }
};

export const searchMedicines = async (query) => {
  try {
    const response = await fetch(
      `http://localhost:5000/api/pharmacy/search?q=${encodeURIComponent(query)}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to search medicines');
    }

    const data = await response.json();
    return data.results || [];
  } catch (error) {
    throw new Error(error.message || 'Medicine search failed');
  }
};

export const getMedicines = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/pharmacy/medicines', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch medicines');
    }

    const data = await response.json();
    return data.medicines || [];
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch medicines');
  }
};
