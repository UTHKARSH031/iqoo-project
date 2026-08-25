import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { BrainCircuit, LogOut, User as UserIcon } from "lucide-react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-[#27272a] bg-[#09090b]/80 backdrop-blur-md">
      <div className="container mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="text-blue-500">
            <BrainCircuit size={22} />
          </div>
          <span className="font-semibold text-lg tracking-tight text-zinc-100">
            LearnLens <span className="text-blue-500 font-normal">AI</span>
          </span>
        </Link>

        <div className="flex items-center gap-4">
          {user && (
            <>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#18181b] border border-[#27272a]">
                <UserIcon size={14} className="text-zinc-400" />
                <span className="text-xs font-medium text-zinc-200">
                  {user.full_name} <span className="text-zinc-500 ml-1 capitalize">({user.role})</span>
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="p-1.5 text-zinc-400 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors"
                title="Logout"
              >
                <LogOut size={16} />
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
