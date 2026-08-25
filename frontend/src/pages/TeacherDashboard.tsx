import { useState, useEffect } from "react";
import { api, cn } from "../lib/api";
import { 
  Users, 
  Target, 
  AlertTriangle,
  BarChart3,
  Search,
  CheckCircle2,
  TrendingUp
} from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

export default function TeacherDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get("/teacher/dashboard");
        setData(response.data);
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
      <div className="max-w-7xl mx-auto pb-12 font-sans space-y-8 animate-pulse">
        <div className="flex justify-between items-end mb-8 mt-4">
          <div className="space-y-2">
            <div className="h-8 w-48 bg-[#18181b] rounded-md"></div>
            <div className="h-4 w-72 bg-[#18181b] rounded-md"></div>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="surface-panel p-5 h-28 space-y-3">
              <div className="h-4 w-28 bg-[#18181b] rounded"></div>
              <div className="h-8 w-20 bg-[#18181b] rounded"></div>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="surface-panel p-6 h-72 bg-[#18181b]/30"></div>
          <div className="surface-panel p-6 h-72 bg-[#18181b]/30"></div>
        </div>
      </div>
    );
  }

  if (!data) return <div className="text-zinc-400 p-8 text-center">Failed to load dashboard.</div>;

  // Ensure chart data is sorted chronologically if it's dates (rudimentary sort for demo)
  const sortedTrends = [...(data.improvement_trends || [])];

  const filteredStudents = data.student_list.filter((s: any) => 
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto pb-12 animate-fade-in font-sans">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10 mt-4">
        <div>
          <h1 className="text-3xl font-bold text-zinc-50 tracking-tight mb-1">Class Analytics</h1>
          <p className="text-zinc-400 text-sm">Real-time aggregate performance and interventions.</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <Users className="text-blue-500" size={16} />
            <h3 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Total Students</h3>
          </div>
          <div className="text-3xl font-bold text-zinc-50">{data.total_students}</div>
        </div>
        
        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="text-emerald-500" size={16} />
            <h3 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Avg. Class Mastery</h3>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-zinc-50">{data.average_class_mastery}</span>
            <span className="text-zinc-500 text-sm">%</span>
          </div>
        </div>
        
        <div className="surface-panel p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <Target className="text-violet-500" size={16} />
            <h3 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Avg. Accuracy</h3>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-zinc-50">{data.average_accuracy}</span>
            <span className="text-zinc-500 text-sm">%</span>
          </div>
        </div>

        <div className="surface-panel p-5 flex flex-col justify-between bg-red-500/5 border-red-500/20">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="text-red-500" size={16} />
            <h3 className="text-xs font-medium text-red-400/80 uppercase tracking-wider">Needs Attention</h3>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-red-500">{data.students_needing_attention}</span>
            <span className="text-red-500/60 text-sm">students</span>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Topic Performance Chart */}
        <div className="surface-panel p-6 flex flex-col">
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-zinc-100">Topic Performance</h2>
            <p className="text-xs text-zinc-400 mt-1">Average mastery score across the entire class per topic.</p>
          </div>
          <div className="h-64 mt-auto">
            {data.total_students > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.topic_performance} margin={{ top: 10, right: 10, left: -25, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis 
                    dataKey="topic_name" 
                    stroke="#71717a" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false}
                    interval={0}
                    angle={-35}
                    textAnchor="end"
                    height={55}
                    tickFormatter={(val: string) => {
                      if (val === "Dynamic Programming") return "Dyn. Prog.";
                      if (val === "Heaps & Priority Queues") return "Heaps & Queues";
                      if (val === "Recursion & Backtracking") return "Backtracking";
                      if (val === "Sorting Algorithms") return "Sorting";
                      if (val === "System Architecture") return "System Arch";
                      if (val === "Bit Manipulation") return "Bit Manip.";
                      return val;
                    }}
                  />
                  <YAxis 
                    stroke="#71717a" 
                    fontSize={11} 
                    tickLine={false} 
                    axisLine={false} 
                    dx={-10}
                  />
                  <Tooltip 
                    cursor={{fill: '#27272a', opacity: 0.4}}
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#fafafa' }}
                    formatter={(value: any) => [`${value}%`, 'Class Mastery']}
                  />
                  <Bar 
                    dataKey="average_mastery" 
                    name="Mastery" 
                    fill="#3b82f6" 
                    radius={[4, 4, 0, 0]}
                    maxBarSize={32}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-zinc-500 text-xs border border-dashed border-[#27272a] rounded-lg">
                <BarChart3 size={28} className="mb-2 opacity-40" />
                <span>No student performance data collected yet.</span>
              </div>
            )}
          </div>
        </div>

        {/* Improvement Trend */}
        <div className="surface-panel p-6 flex flex-col">
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-zinc-100">Mastery Trend</h2>
            <p className="text-xs text-zinc-400 mt-1">Class average progression over recent assessments.</p>
          </div>
          <div className="h-64 mt-auto">
            {sortedTrends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sortedTrends} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorMastery" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis 
                    dataKey="date" 
                    stroke="#71717a" 
                    fontSize={11} 
                    tickLine={false} 
                    axisLine={false}
                    dy={10}
                  />
                  <YAxis 
                    stroke="#71717a" 
                    fontSize={11} 
                    tickLine={false} 
                    axisLine={false} 
                    domain={['dataMin - 5', 'dataMax + 5']}
                    dx={-10}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="avg_mastery" 
                    name="Avg Mastery" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorMastery)"
                    activeDot={{r: 4, fill: '#10b981', strokeWidth: 0}} 
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-zinc-500 text-xs border border-dashed border-[#27272a] rounded-lg">
                <TrendingUp size={28} className="mb-2 opacity-40" />
                <span>No progression data available yet.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Weakest Topics */}
        <div className="lg:col-span-1 surface-panel p-6">
          <h2 className="text-sm font-semibold text-zinc-100 mb-1 flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-500" />
            Intervention Needed
          </h2>
          <p className="text-xs text-zinc-400 mb-6">Topics where &gt;50% of the class is struggling.</p>
          
          <div className="space-y-4">
            {data.weak_topics.map((topic: any, i: number) => (
              <div key={i} className="pb-4 border-b border-[#27272a] last:border-0 last:pb-0">
                <div className="flex justify-between items-start mb-1">
                  <h4 className="font-medium text-sm text-zinc-200">{topic.topic_name}</h4>
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-red-500/10 text-red-500">
                    {topic.struggling_pct}% struggling
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs text-zinc-500 mt-2">
                  <span>Class Avg: <strong className="text-zinc-300 font-medium">{topic.average_mastery}%</strong></span>
                  <span className="flex items-center gap-1"><Users size={12}/> {topic.students_struggling} students</span>
                </div>
              </div>
            ))}
            {data.weak_topics.length === 0 && (
              <div className="text-center py-8 flex flex-col items-center text-zinc-500">
                <CheckCircle2 size={32} className="mb-2 opacity-50" />
                <p className="text-sm">No immediate interventions required.</p>
              </div>
            )}
          </div>
        </div>

        {/* Student Roster */}
        <div className="lg:col-span-2 surface-panel flex flex-col">
          <div className="p-5 border-b border-[#27272a] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-sm font-semibold text-zinc-100">Student Roster</h2>
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500" size={14} />
              <input 
                type="text" 
                placeholder="Search students..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-4 py-1.5 bg-[#18181b] border border-[#27272a] rounded-md text-xs text-zinc-200 focus:outline-none focus:border-blue-500 transition-colors w-full sm:w-64"
              />
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-zinc-500 uppercase tracking-wider bg-[#18181b]/50 border-b border-[#27272a]">
                <tr>
                  <th className="px-5 py-3 font-medium">Student Name</th>
                  <th className="px-5 py-3 font-medium">Mastery</th>
                  <th className="px-5 py-3 font-medium">Accuracy</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272a]">
                {filteredStudents.map((student: any) => (
                  <tr key={student.student_id} className="hover:bg-[#18181b] transition-colors group">
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-zinc-200">{student.name}</div>
                      <div className="text-xs text-zinc-500 mt-0.5">{student.weak_topics} weak topics</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <span className="w-8 text-xs font-medium text-zinc-300">{student.avg_mastery}%</span>
                        <div className="w-16 h-1.5 bg-[#27272a] rounded-full overflow-hidden">
                          <div 
                            className={cn(
                              "h-full rounded-full",
                              student.avg_mastery >= 70 ? "bg-emerald-500" : student.avg_mastery >= 40 ? "bg-amber-500" : "bg-red-500"
                            )} 
                            style={{width: `${Math.max(5, student.avg_mastery)}%`}}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-zinc-400 text-xs font-medium">
                      {student.avg_accuracy}%
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={cn(
                        "px-2 py-1 rounded text-[10px] font-semibold uppercase tracking-wider",
                        student.status === 'mastered' ? "bg-emerald-500/10 text-emerald-500" : 
                        student.status === 'on_track' ? "bg-blue-500/10 text-blue-500" : 
                        "bg-red-500/10 text-red-500"
                      )}>
                        {student.status.replace('_', ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredStudents.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-8 text-center text-zinc-500 text-sm">
                      No students found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
