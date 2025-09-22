// api.js
const API_BASE_URL = "http://127.0.0.1:5000";

export const detect = async (formData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/detect`, {
      method: "POST",
      body: formData, // FormData will auto-set Content-Type to multipart/form-data
    });

    if (!response.ok) {
      return {
        success: false,
        prediction: null,
        distance: null,
        error: `HTTP ${response.status} - ${response.statusText}`,
      };
    }

    const data = await response.json();
    console.log(data)
    return { success: true, ...data };
  } catch (err) {
    console.error("API error:", err);
    return {
      success: false,
      prediction: null,
      distance: null,
      error: err.message,
    };
  }
};
