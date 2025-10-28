import { useState } from 'react';

interface PredictionResponse {
  blood_type: string;
  confidence: number;
  probabilities: Record<string, number>;
}

const BloodType = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [bloodType, setBloodType] = useState<string>('Not Found');
  const [confidence, setConfidence] = useState<number>(0);
  const [filename, setFilename] = useState<string>('');

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedImage(file);
    setFilename(file.name);
    setPreview(URL.createObjectURL(file));
  };

  const handleAnalyzeImage = async () => {
    if (!selectedImage) return;

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);

      const response = await fetch('http://localhost:8000/predict/blood', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }

      const data: PredictionResponse = await response.json();
      setBloodType(data.blood_type || 'Not Found');
      setConfidence(data.confidence * 100); // Convert to percentage
    } catch (error) {
      console.error('Error:', error);
      setBloodType('Not Found');
      setConfidence(0);
    }
  };

  return (
    <div className="relative h-screen">
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
        <h1 className="text-4xl font-bold mb-8">Blood Type Classifier</h1>
        <p className="mb-8 text-gray-400">Upload a fingerprint image to identify the blood type</p>

        <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 mb-8 w-full max-w-md">
          {preview && (
            <img 
              src={preview} 
              alt="Selected" 
              className="max-w-full h-auto mb-4 rounded-lg"
            />
          )}
          
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="w-full text-sm text-gray-400 cursor-pointer
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-cyan-500 file:text-white
              hover:file:bg-cyan-600"
          />
          {filename && (
            <p className="mt-2 text-gray-400 text-sm">
              Selected: {filename}
            </p>
          )}
        </div>

        <button
          onClick={handleAnalyzeImage}
          disabled={!selectedImage}
          className="w-full max-w-md bg-cyan-500 text-white py-3 rounded-lg 
            hover:bg-cyan-600 disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          Analyze Image
        </button>

        <div className="mt-8 text-center">
          <h3 className="text-2xl font-bold text-cyan-500">{bloodType}</h3>
          {confidence > 0 && (
            <p className="text-gray-400 mt-2">
              Confidence: {confidence.toFixed(2)}%
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default BloodType;