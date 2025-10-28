import { AlertCircle } from "lucide-react";

interface AlertProps {
  message: string;
}

const Alert = ({ message }: AlertProps) => {
  return (
    <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4 flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
      <p className="text-sm text-destructive">{message}</p>
    </div>
  );
};

export default Alert;
