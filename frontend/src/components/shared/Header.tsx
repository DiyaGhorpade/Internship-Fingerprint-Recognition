import { Activity, BarChart2 } from "lucide-react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-primary" />
          <h1 className="text-2xl font-bold">DactyloAI</h1>
        </div>

        <nav className="flex gap-4">
          <Link to="/" className="text-sm font-medium hover:underline">
            Home
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
