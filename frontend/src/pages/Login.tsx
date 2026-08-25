import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { BrainCircuit, Loader2, AlertCircle, GraduationCap, ShieldCheck, CheckCircle2, ArrowRight } from "lucide-react";
import { AxiosError } from "axios";

export default function Login() {
  const [roleTab, setRoleTab] = useState<'student' | 'teacher'>('student');
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegisterMode) {
        // Register Flow
        const response = await api.post("/auth/register", {
          full_name: fullName,
          email: email,
          username: email,
          password: password,
          role: roleTab
        });

        login(response.data.access_token, {
          id: response.data.user_id,
          username: response.data.username,
          role: response.data.role,
          full_name: response.data.full_name,
        });

        if (response.data.role === "teacher") {
          navigate("/teacher");
        } else {
          navigate("/student");
        }
      } else {
        // Login Flow
        const response = await api.post("/auth/login", {
          username: email,
          password: password,
        });

        if (response.data.role !== roleTab) {
          setError(`This account is registered as a ${response.data.role}. Please switch to the ${response.data.role} tab.`);
          setLoading(false);
          return;
        }

        login(response.data.access_token, {
          id: response.data.user_id,
          username: response.data.username,
          role: response.data.role,
          full_name: response.data.full_name,
        });

        if (response.data.role === "teacher") {
          navigate("/teacher");
        } else {
          navigate("/student");
        }
      }
    } catch (err) {
      if (err instanceof AxiosError && err.response) {
        setError(err.response.data?.detail || "An error occurred during authentication.");
      } else {
        setError("Failed to connect to the server. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-6rem)] flex items-center justify-center py-6 px-4 font-sans">
      <div className="w-full max-w-5xl surface-panel border border-[#27272a] rounded-2xl overflow-hidden grid lg:grid-cols-12 shadow-2xl">
        
        {/* Left Side: Product Feature Panel */}
        <div className="lg:col-span-6 bg-[#18181b] p-8 lg:p-12 border-b lg:border-b-0 lg:border-r border-[#27272a] flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-blue-500 mb-8">
              <BrainCircuit size={28} />
              <span className="font-bold text-xl tracking-tight text-zinc-100">
                LearnLens <span className="text-blue-500 font-normal">AI</span>
              </span>
            </div>

            <h2 className="text-2xl lg:text-3xl font-bold text-zinc-50 tracking-tight leading-snug mb-4">
              Continuous AI Mastery Analytics for Education.
            </h2>
            <p className="text-sm text-zinc-400 leading-relaxed mb-8">
              Empowering students with adaptive practice loops and instructors with real-time class performance metrics.
            </p>

            <div className="space-y-4 text-xs text-zinc-300">
              <div className="flex items-start gap-3">
                <div className="p-1 rounded bg-blue-500/10 text-blue-400 mt-0.5">
                  <CheckCircle2 size={14} />
                </div>
                <div>
                  <div className="font-semibold text-zinc-200">Adaptive Evaluation Engine</div>
                  <div className="text-zinc-400 text-[11px] mt-0.5">Calculates topic-level mastery scores from historical question accuracy.</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-1 rounded bg-emerald-500/10 text-emerald-400 mt-0.5">
                  <CheckCircle2 size={14} />
                </div>
                <div>
                  <div className="font-semibold text-zinc-200">Instructor Roster Insights</div>
                  <div className="text-zinc-400 text-[11px] mt-0.5">Automated class weakness identification and student intervention alerts.</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-1 rounded bg-violet-500/10 text-violet-400 mt-0.5">
                  <CheckCircle2 size={14} />
                </div>
                <div>
                  <div className="font-semibold text-zinc-200">Personalized Practice Loops</div>
                  <div className="text-zinc-400 text-[11px] mt-0.5">Targeted problem sets focused on individual knowledge gaps.</div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-6 border-t border-[#27272a] text-xs text-zinc-500 flex items-center justify-between">
            <span>LearnLens Education Engine v2.4</span>
            <span className="text-zinc-400 font-medium">Enterprise Portal</span>
          </div>
        </div>

        {/* Right Side: Auth Form */}
        <div className="lg:col-span-6 p-8 lg:p-12 bg-[#09090b] flex flex-col justify-center">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-zinc-50 tracking-tight">
              {isRegisterMode ? "Create Account" : "Sign In"}
            </h3>
            <p className="text-xs text-zinc-400 mt-1">
              Select your portal below to continue
            </p>
          </div>

          {/* Role Tabs */}
          <div className="grid grid-cols-2 gap-1 p-1 bg-[#18181b] rounded-lg mb-6 border border-[#27272a]">
            <button
              type="button"
              onClick={() => {
                setRoleTab('student');
                setError("");
              }}
              className={`flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-md transition-all ${
                roleTab === 'student'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <GraduationCap size={16} />
              Student Portal
            </button>
            <button
              type="button"
              onClick={() => {
                setRoleTab('teacher');
                setError("");
              }}
              className={`flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-md transition-all ${
                roleTab === 'teacher'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <ShieldCheck size={16} />
              Teacher Portal
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2 text-red-400 text-xs">
                <AlertCircle size={16} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {isRegisterMode && (
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  className="w-full bg-[#18181b] border border-[#27272a] rounded-lg px-3.5 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="e.g. Alex Johnson"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                {roleTab === 'student' ? 'Student Email' : 'Teacher Email'}
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-[#18181b] border border-[#27272a] rounded-lg px-3.5 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                placeholder={roleTab === 'student' ? "student@learnlens.ai" : "teacher@learnlens.ai"}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-[#18181b] border border-[#27272a] rounded-lg px-3.5 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full font-semibold text-xs rounded-lg px-4 py-2.5 mt-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 ${
                roleTab === 'student'
                  ? 'bg-blue-600 hover:bg-blue-500 text-white'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white'
              }`}
            >
              {loading ? (
                <Loader2 className="animate-spin" size={16} />
              ) : isRegisterMode ? (
                <>Create {roleTab === 'student' ? 'Student' : 'Teacher'} Account <ArrowRight size={14} /></>
              ) : (
                <>Sign In to {roleTab === 'student' ? 'Student Portal' : 'Teacher Portal'} <ArrowRight size={14} /></>
              )}
            </button>
          </form>

          {/* Toggle between Sign In and Register */}
          <div className="mt-6 pt-4 border-t border-[#27272a] text-center text-xs">
            {isRegisterMode ? (
              <p className="text-zinc-400">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsRegisterMode(false);
                    setError("");
                  }}
                  className="text-blue-400 font-semibold hover:underline"
                >
                  Sign In
                </button>
              </p>
            ) : (
              <p className="text-zinc-400">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsRegisterMode(true);
                    setError("");
                  }}
                  className="text-blue-400 font-semibold hover:underline"
                >
                  Create an account
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
