import { useState } from "react";
import { PredictionResult, predictFingerprint } from "@/api/apiService";
import ImageUploader from "@/components/shared/ImageUploader";
import FingerprintResult from "@/components/specific/FingerprintResult";
import Alert from "@/components/shared/Alert";

const FingerprintClassifierView = () => {
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (file: File) => {
    setIsLoading(true);
    setError(null);
    setPredictionResult(null);

    try {
      const result = await predictFingerprint(file);
      setPredictionResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold mb-2">Fingerprint Pattern Classifier</h2>
        <p className="text-muted-foreground">
          Upload a fingerprint image to identify its pattern type: Arc, Whorl, or Loop
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <ImageUploader
            onAnalyze={handleAnalyze}
            isLoading={isLoading}
            title="Upload Fingerprint"
            description="Select or drag a clear fingerprint image"
          />
        </div>

        <div>
          {error && <Alert message={error} />}
          {predictionResult && <FingerprintResult result={predictionResult} />}
          {!error && !predictionResult && (
            <div className="h-full flex items-center justify-center">
              <p className="text-muted-foreground text-center">
                Results will appear here after analysis
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FingerprintClassifierView;
