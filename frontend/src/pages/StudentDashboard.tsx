import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api, cn } from "../lib/api";
import { 
  Target, 
  TrendingUp, 
  Zap, 
  Award, 
  ArrowRight,
  Lightbulb,
  AlertTriangle,
  PlayCircle,
  BarChart3,
  CheckCircle2,
  BookOpen
} from "lucide-react";

export default function StudentDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [defaultSubjectId, setDefaultSubjectId] = useState<number>(1);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [dashboardRes, subjectsRes] = await Promise.all([
          api.get("/student/dashboard"),
          api.get("/student/subjects")
        ]);
        setData(dashboardRes.data);
        if (subjectsRes.data && subjectsRes.data.length > 0) {
          setDefaultSubjectId(subjectsRes.data[0].id);
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto pb-12 font-sans space-y-8 animate-pulse">
        <div className="flex justify-between items-end mb-8 mt-4">
          <div className="space-y-2">
            <div className="h-8 w-40 bg-[#18181b] rounded-md"></div>
            <div className="h-4 w-64 bg-[#18181b] rounded-md"></div>
          </div>
          <div className="h-10 w-36 bg-[#18181b] rounded-md"></div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="surface-panel p-5 h-28 space-y-3">
              <div className="h-4 w-24 bg-[#18181b] rounded"></div>
              <div className="h-8 w-16 bg-[#18181b] rounded"></div>
            </div>
          ))}
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="surface-panel p-4 h-24 space-y-2">
              <div className="h-4 w-32 bg-[#18181b] rounded"></div>
              <div className="h-3 w-48 bg-[#18181b] rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center text-center p-8 text-zinc-400">
        <p className="text-base font-semibold text-zinc-200 mb-2">Session Expired or Failed to Load</p>
        <p className="text-xs text-zinc-500 mb-6">Your authentication token may have expired after the database reset.</p>
        <button 
          onClick={() => { localStorage.clear(); window.location.href = "/login"; }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-md transition-colors"
        >
          Sign In Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto pb-12 animate-fade-in font-sans">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-8 mt-2">
        <div>
          <h1 className="text-3xl font-bold text-zinc-50 tracking-tight mb-1">Overview</h1>
          <p className="text-zinc-400 text-sm">Welcome back, {data.user.full_name.split(' ')[0]}. Here's where you stand.</p>
        </div>
        <Link 
          to={`/assessment/${defaultSubjectId}`}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-zinc-100 hover:bg-white text-zinc-900 text-sm font-semibold rounded-lg transition-colors shadow-sm"
        >
          <Target size={16} />
          Diagnostic Test
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 bg-blue-500/10 rounded-md text-blue-500">
              <BarChart3 size={16} />
            </div>
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Overall Mastery</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-zinc-50">{data.overall_mastery.toFixed(1)}</span>
            <span className="text-zinc-500 text-sm">%</span>
          </div>
        </div>

        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 bg-amber-500/10 rounded-md text-amber-500">
              <Zap size={16} />
            </div>
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Day Streak</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-zinc-50">{data.current_streak}</span>
            <span className="text-zinc-500 text-sm">days</span>
          </div>
        </div>

        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 bg-violet-500/10 rounded-md text-violet-500">
              <Award size={16} />
            </div>
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Total XP</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-zinc-50">{data.total_xp}</span>
            <span className="text-zinc-500 text-sm">xp</span>
          </div>
        </div>

        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 bg-emerald-500/10 rounded-md text-emerald-500">
              <TrendingUp size={16} />
            </div>
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Current Level</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-zinc-50">{data.level}</span>
          </div>
        </div>
      </div>

      {/* AI Insights - Horizontal Banner Style */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-zinc-100 mb-4 flex items-center gap-2">
          <Lightbulb size={16} className="text-amber-500" />
          AI Analysis
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.insights.map((insight: any, i: number) => (
            <div key={i} className="surface-panel p-4 flex gap-3 items-start">
              <div className="mt-0.5 shrink-0">
                {insight.insight_type === 'strength' && <CheckCircle2 size={16} className="text-emerald-500" />}
                {insight.insight_type === 'weakness' && <AlertTriangle size={16} className="text-red-500" />}
                {insight.insight_type === 'trend' && <TrendingUp size={16} className="text-blue-500" />}
                {insight.insight_type === 'action' && <Target size={16} className="text-violet-500" />}
              </div>
              <div>
                <h4 className="text-sm font-medium text-zinc-200 mb-1 leading-tight">{insight.title}</h4>
                <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">{insight.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column (Topics - Takes up 2/3) */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-zinc-100 flex items-center gap-2 mb-2">
            <BookOpen size={16} className="text-blue-500" />
            Topic Progress
          </h2>

          <div className="grid sm:grid-cols-2 gap-4">
            {data.topic_mastery.map((topic: any) => (
              <div key={topic.topic_id} className="surface-panel p-5 flex flex-col group hover:border-[#3f3f46] transition-colors">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h4 className="font-medium text-zinc-200 text-sm mb-1">{topic.topic_name}</h4>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={cn(
                        "w-2 h-2 rounded-full",
                        topic.mastery_score >= 80 ? "bg-emerald-500" :
                        topic.mastery_score >= 60 ? "bg-blue-500" :
                        topic.mastery_score >= 40 ? "bg-amber-500" : "bg-red-500"
                      )} />
                      <span className="text-zinc-400 capitalize font-medium">{topic.mastery_level.replace('_', ' ')}</span>
                    </div>
                  </div>
                  <div className="text-lg font-bold text-zinc-100">
                    {Math.round(topic.mastery_score)}<span className="text-xs text-zinc-500 font-normal">%</span>
                  </div>
                </div>
                
                {/* Progress bar */}
                <div className="w-full bg-[#27272a] rounded-full h-1.5 mb-5 overflow-hidden">
                  <div 
                    className={cn(
                      "h-full rounded-full transition-all duration-1000 ease-out",
                      topic.mastery_score >= 80 ? "bg-emerald-500" :
                      topic.mastery_score >= 60 ? "bg-blue-500" :
                      topic.mastery_score >= 40 ? "bg-amber-500" : "bg-red-500"
                    )}
                    style={{ width: `${Math.max(2, topic.mastery_score)}%` }}
                  ></div>
                </div>
                
                <div className="mt-auto flex items-center justify-between pt-1">
                  <div className="text-xs font-medium text-zinc-500">
                    Acc: {Math.round(topic.accuracy)}%
                  </div>
                  <Link 
                    to={`/practice/${topic.topic_id}`}
                    className="flex items-center gap-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                  >
                    Practice <ArrowRight size={14} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
          
          {data.topic_mastery.length === 0 && (
            <div className="surface-panel p-12 flex flex-col items-center justify-center text-zinc-500">
              <Target size={32} className="mb-4 opacity-50" />
              <p className="text-sm">No topic data available yet.</p>
              <Link to={`/assessment/${defaultSubjectId}`} className="mt-4 text-blue-500 text-sm font-medium hover:underline">Take a diagnostic test</Link>
            </div>
          )}
        </div>

        {/* Right Column (Recommendations - Takes up 1/3) */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-sm font-semibold text-zinc-100 flex items-center gap-2 mb-2">
            <Target size={16} className="text-violet-500" />
            Up Next
          </h2>
          <div className="surface-panel p-1 border-none bg-transparent shadow-none">
            <div className="space-y-3">
              {data.recommendations.map((rec: any, i: number) => (
                <div key={i} className="surface-panel p-4 hover:border-[#3f3f46] transition-colors group">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-sm text-zinc-200">{rec.topic_name}</h4>
                    <span className={cn(
                      "text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-md font-bold",
                      rec.urgency === 'high' ? "bg-red-500/10 text-red-500" :
                      rec.urgency === 'medium' ? "bg-amber-500/10 text-amber-500" :
                      "bg-blue-500/10 text-blue-500"
                    )}>
                      {rec.urgency}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mb-4 leading-relaxed line-clamp-2">{rec.reason}</p>
                  <Link 
                    to={`/practice/${rec.topic_id}`}
                    className="inline-flex items-center gap-1.5 px-3 py-2 bg-[#27272a] group-hover:bg-zinc-100 group-hover:text-zinc-900 text-zinc-300 text-xs font-semibold rounded-md transition-all w-full justify-center"
                  >
                    <PlayCircle size={14} className="group-hover:text-zinc-900" /> Start Session
                  </Link>
                </div>
              ))}
              {data.recommendations.length === 0 && (
                <div className="surface-panel p-6 text-center">
                  <p className="text-xs text-zinc-500">No pending recommendations.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
