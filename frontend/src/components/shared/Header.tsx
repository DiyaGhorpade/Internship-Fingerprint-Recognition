import { Activity } from "lucide-react";

const Header = () => {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-primary glow-primary" />
          <h1 className="text-2xl font-bold gradient-text">
            DactyloAI
          </h1>
          <span className="text-sm text-muted-foreground ml-2">
            Advanced Biological Analysis
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
