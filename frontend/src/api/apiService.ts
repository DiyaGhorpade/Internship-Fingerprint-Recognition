const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface PredictionResult {
  predicted_class: string;
  confidence: number;
  all_probabilities?: Record<string, number>;
  details?: {
    Rh_factor?: string;
    antigens_detected?: string[];
  };
}

/**
 * Predict fingerprint pattern (Arc, Loop, Whorl)
 */
export const predictFingerprint = async (file: File): Promise<PredictionResult> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/predict/fingerprint`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Network error" }));
    throw new Error(error.detail || "Failed to analyze fingerprint");
  }

  return response.json();
};

/**
 * Predict blood type (A, B, AB, O, + / -)
 */
export const predictBloodType = async (file: File): Promise<PredictionResult> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/predict/bloodtype`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Network error" }));
    throw new Error(error.detail || "Failed to analyze blood type");
  }

  return response.json();
};
