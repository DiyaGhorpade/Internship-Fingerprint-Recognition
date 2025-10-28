import { PredictionResult } from "@/api/apiService";
import { Droplet } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface BloodTypeResultProps {
  result: PredictionResult;
}

const BloodTypeResult = ({ result }: BloodTypeResultProps) => {
  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="bg-card border border-secondary/20 rounded-xl p-6 glow-secondary">
        <div className="flex items-center gap-3 mb-4">
          <Droplet className="w-8 h-8 text-secondary" />
          <h3 className="text-xl font-semibold">Blood Type Detected</h3>
        </div>
        
        <div className="text-center mb-6">
          <p className="text-5xl font-bold text-secondary mb-2">
            {result.predicted_class}
          </p>
          <p className="text-muted-foreground">Classification Result</p>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Confidence Score</span>
            <span className="text-lg font-bold text-secondary">{confidencePercent}%</span>
          </div>
          <Progress value={confidencePercent} className="h-3" />
        </div>
      </div>

      {result.details && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h4 className="text-lg font-semibold mb-4">Analysis Details</h4>
          <div className="space-y-3">
            {result.details.Rh_factor && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Rh Factor</span>
                <span className="text-sm font-medium">{result.details.Rh_factor}</span>
              </div>
            )}
            {result.details.antigens_detected && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Antigens Detected</span>
                <span className="text-sm font-medium">
                  {result.details.antigens_detected.join(', ')}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BloodTypeResult;
