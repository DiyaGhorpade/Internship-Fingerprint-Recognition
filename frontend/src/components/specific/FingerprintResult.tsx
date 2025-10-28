import { PredictionResult } from "@/api/apiService";
import { Fingerprint } from "lucide-react";
import { Progress } from "@/components/ui/progress"; // Assuming you have shadcn progress

interface FingerprintResultProps {
  result: PredictionResult;
}

const FingerprintResult = ({ result }: FingerprintResultProps) => {
  // Helper function with safety check
  const formatClassName = (className: string | undefined): string => {
    // If className is undefined or null, return a default string
    if (!className) {
      return 'Unknown';
    }
    // Proceed with formatting if className is valid
    return className.replace(/^class\d+_/, '').replace(/_/g, ' ').toUpperCase();
  };

  // FIX: Access the 'pattern' field from the backend response
  // Use optional chaining (?.) and nullish coalescing (??) for safety
  const predictedPattern = formatClassName(result.pattern);
  const confidencePercent = Math.round((result.confidence || 0) * 100);

  // Use all_probabilities if available, otherwise fallback to probabilities
  const probabilities = result.all_probabilities || result.probabilities || {};

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Main Result Card */}
      <div className="bg-card border border-primary/20 rounded-xl p-6 shadow-glow-cyan"> {/* Match theme */}
        <div className="flex items-center gap-3 mb-4">
          <Fingerprint className="w-8 h-8 text-accent-cyan" /> {/* Match theme */}
          <h3 className="text-xl font-semibold text-text-primary">Pattern Detected</h3>
        </div>

        <div className="text-center mb-6">
          <p className="text-4xl font-bold text-accent-cyan mb-2">
            {predictedPattern}
          </p>
          <p className="text-muted-foreground">Classification Result</p>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-text-secondary">Confidence Score</span>
            <span className="text-lg font-bold text-text-primary">{confidencePercent}%</span>
          </div>
          {/* Use shadcn Progress component */}
          <Progress value={confidencePercent} className="h-3 [&>div]:bg-accent-cyan" />
        </div>
      </div>

      {/* Probability Breakdown Card */}
      {Object.keys(probabilities).length > 0 && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h4 className="text-lg font-semibold mb-4 text-text-primary">Probability Breakdown</h4>
          <div className="space-y-3">
            {Object.entries(probabilities).map(([className, probability]) => {
              const percent = Math.round((probability || 0) * 100);
              return (
                <div key={className}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-muted-foreground">
                      {formatClassName(className)}
                    </span>
                    <span className="text-sm font-medium text-text-primary">{percent}%</span>
                  </div>
                  {/* Use shadcn Progress component */}
                  <Progress value={percent} className="h-2 [&>div]:bg-accent-magenta" />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default FingerprintResult;
