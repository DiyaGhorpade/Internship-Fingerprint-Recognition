import { Loader2 } from "lucide-react";

const Spinner = () => {
  return (
    <div className="flex items-center justify-center">
      <Loader2 className="w-8 h-8 animate-spin text-primary glow-primary" />
    </div>
  );
};

export default Spinner;
