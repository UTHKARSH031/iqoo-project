import { Link } from "react-router-dom";
import { ArrowRight, BookOpen, BarChart3, ShieldCheck, Check } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)] font-sans bg-[#09090b] text-zinc-100">
      {/* Hero Section */}
      <section className="border-b border-[#27272a] py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-zinc-900 border border-[#27272a] text-zinc-400 text-xs font-medium mb-6">
            <span>LearnLens AI Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-bold tracking-tight text-zinc-50 mb-6 leading-tight">
            Adaptive Learning Assessment &amp; Mastery Analytics
          </h1>

          <p className="text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto mb-8 font-normal leading-relaxed">
            Continuous diagnostic testing, automated mastery scoring, and real-time class performance insights designed for modern education.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/login"
              className="w-full sm:w-auto px-6 py-2.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-colors flex items-center justify-center gap-2"
            >
              Get Started <ArrowRight size={16} />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-6 py-2.5 rounded-md bg-[#18181b] hover:bg-[#27272a] text-zinc-200 font-medium text-sm border border-[#27272a] transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Core Platform Capabilities */}
      <section className="py-16 px-6 border-b border-[#27272a]">
        <div className="max-w-5xl mx-auto">
          <div className="mb-12">
            <h2 className="text-xl font-bold text-zinc-100 mb-2">Platform Capabilities</h2>
            <p className="text-zinc-400 text-sm">Key features for students and instructors.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="surface-panel p-6">
              <div className="w-10 h-10 rounded-md bg-blue-500/10 text-blue-500 flex items-center justify-center mb-4">
                <BookOpen size={20} />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">Diagnostic Assessments</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Adaptive evaluations that measure baseline knowledge across subject topics without static question ordering.
              </p>
            </div>

            <div className="surface-panel p-6">
              <div className="w-10 h-10 rounded-md bg-blue-500/10 text-blue-500 flex items-center justify-center mb-4">
                <BarChart3 size={20} />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">Mastery Scoring Engine</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Weighted performance calculation considering historical accuracy, attempt frequency, and topic difficulty.
              </p>
            </div>

            <div className="surface-panel p-6">
              <div className="w-10 h-10 rounded-md bg-blue-500/10 text-blue-500 flex items-center justify-center mb-4">
                <ShieldCheck size={20} />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">Instructor Roster Analytics</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Aggregate class reports identifying topic-level weakness trends and automated intervention alerts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Breakdown Table / List */}
      <section className="py-16 px-6 border-b border-[#27272a]">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-2xl font-bold text-zinc-100 mb-4">Built for Structured Progression</h2>
              <p className="text-zinc-400 text-sm mb-6 leading-relaxed">
                LearnLens replaces subjective grading with deterministic mastery metrics. Students receive target practice sets tailored to their identified knowledge gaps.
              </p>

              <div className="space-y-3 text-xs text-zinc-300">
                <div className="flex items-center gap-2.5">
                  <Check size={16} className="text-blue-500 shrink-0" />
                  <span>Topic-level accuracy tracking</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Check size={16} className="text-blue-500 shrink-0" />
                  <span>Dynamic practice question generation</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Check size={16} className="text-blue-500 shrink-0" />
                  <span>Exportable class roster metrics</span>
                </div>
              </div>
            </div>

            <div className="surface-panel p-6">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-4">System Overview</h4>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-2 border-b border-[#27272a]">
                  <span className="text-zinc-400">Supported Subjects</span>
                  <span className="text-zinc-200 font-medium">Computer Science &amp; DSA</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#27272a]">
                  <span className="text-zinc-400">Evaluation Model</span>
                  <span className="text-zinc-200 font-medium">Weighted Difficulty Engine</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#27272a]">
                  <span className="text-zinc-400">Assessment Types</span>
                  <span className="text-zinc-200 font-medium">Diagnostic &amp; Adaptive Practice</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer with TOS and Privacy Policy */}
      <footer className="py-8 px-6 text-xs text-zinc-500 border-t border-[#27272a]">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>&copy; {new Date().getFullYear()} LearnLens AI. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link to="/terms" className="hover:text-zinc-300 transition-colors">Terms of Service</Link>
            <Link to="/privacy" className="hover:text-zinc-300 transition-colors">Privacy Policy</Link>
            <Link to="/contact" className="hover:text-zinc-300 transition-colors">Contact</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
