import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { Loader2, CheckCircle, ArrowRight, Lightbulb, Bot, Sparkles, Target } from "lucide-react";

export default function Practice() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [practice, setPractice] = useState<any>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [results, setResults] = useState<any>(null);
  const [sessionStartTime, setSessionStartTime] = useState<number>(0);
  
  // AI Features
  const [aiHint, setAiHint] = useState<string | null>(null);
  const [hintLoading, setHintLoading] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [explainLoading, setExplainLoading] = useState(false);

  useEffect(() => {
    const startPractice = async () => {
      try {
        const response = await api.post("/practice/generate", {
          topic_id: parseInt(topicId || "1"),
          num_questions: 6
        });
        setPractice(response.data);
        setSessionStartTime(Date.now());
      } catch (error) {
        console.error("Failed to generate practice", error);
      } finally {
        setLoading(false);
      }
    };
    startPractice();
  }, [topicId]);

  const currentQ = practice?.questions[currentQuestionIndex];

  const handleSelectOption = (questionId: number, option: string) => {
    setAnswers({ ...answers, [questionId]: option });
  };

  const handleNext = () => {
    if (currentQuestionIndex < practice.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setAiHint(null); // Reset hint for next question
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setAiHint(null);
    }
  };

  const getHint = async () => {
    if (!currentQ) return;
    setHintLoading(true);
    try {
      const response = await api.post("/ai/hint", {
        question_id: currentQ.id,
        student_answer: answers[currentQ.id] || null
      });
      setAiHint(response.data.hint);
    } catch (error) {
      setAiHint("Could not generate hint at this time.");
    } finally {
      setHintLoading(false);
    }
  };

  const getExplanation = async () => {
    setExplainLoading(true);
    try {
      const response = await api.post("/ai/explain", {
        topic_id: parseInt(topicId || "1"),
        action: "explain"
      });
      setAiExplanation(response.data.content);
    } catch (error) {
      setAiExplanation("Could not generate explanation at this time.");
    } finally {
      setExplainLoading(false);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const timeTakenSeconds = Math.round((Date.now() - sessionStartTime) / 1000);

      const formattedAnswers = Object.entries(answers).map(([qId, ans]) => ({
        question_id: parseInt(qId),
        student_answer: ans,
        time_taken_seconds: timeTakenSeconds > 0 ? timeTakenSeconds : 1
      }));

      const response = await api.post("/practice/submit", {
        session_id: practice.session_id,
        topic_id: parseInt(topicId || "1"),
        answers: formattedAnswers
      });
      setResults(response.data);
    } catch (error) {
      console.error("Failed to submit practice", error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-slate-400">
        <Sparkles size={48} className="animate-pulse text-violet-500 mb-4" />
        <p>Curating targeted practice session...</p>
      </div>
    );
  }

  if (results) {
    return (
      <div className="max-w-2xl mx-auto py-12 animate-fade-in text-center">
        <div className="inline-flex items-center justify-center p-4 bg-emerald-500/10 rounded-full text-emerald-500 mb-6">
          <CheckCircle size={48} />
        </div>
        <h1 className="text-3xl font-outfit font-bold text-white mb-2">Session Complete!</h1>
        <p className="text-slate-400 mb-8">{results.message}</p>
        
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="surface-panel p-6 rounded-2xl">
            <div className="text-sm text-slate-400 mb-1">Score</div>
            <div className="text-3xl font-bold text-white">{Math.round(results.session_score)}%</div>
            <div className="text-xs text-slate-500 mt-1">{results.questions_correct} of {results.questions_attempted} correct</div>
          </div>
          <div className="surface-panel p-6 rounded-2xl">
            <div className="text-sm text-slate-400 mb-1">New Mastery</div>
            <div className="text-3xl font-bold text-white flex items-center justify-center gap-2">
              {Math.round(results.mastery_after)}%
              {results.mastery_delta > 0 && (
                <span className="text-sm text-emerald-400">+{results.mastery_delta.toFixed(1)}</span>
              )}
            </div>
            <div className="text-xs text-slate-500 mt-1">+{results.xp_earned} XP earned</div>
          </div>
        </div>

        <button 
          onClick={() => navigate("/student")}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors shadow-lg shadow-blue-500/20"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  if (!practice) return <div>Failed to load practice.</div>;

  const isLastQuestion = currentQuestionIndex === practice.questions.length - 1;
  const allAnswered = Object.keys(answers).length === practice.questions.length;

  return (
    <div className="max-w-5xl mx-auto py-8 animate-fade-in flex gap-6">
      {/* Main Question Area */}
      <div className="flex-1">
        <div className="flex justify-between items-center mb-6 text-sm font-medium text-slate-400">
          <div className="flex items-center gap-2">
            <Target size={16} className="text-violet-400"/> Targeted Practice: {practice.topic_name}
          </div>
          <div>Question {currentQuestionIndex + 1} of {practice.questions.length}</div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-slate-800 rounded-full h-1.5 mb-8 overflow-hidden">
          <div 
            className="bg-violet-500 h-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex) / practice.questions.length) * 100}%` }}
          ></div>
        </div>

        <div className="surface-panel p-8 rounded-2xl mb-6 min-h-[350px] flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div className="text-xs font-medium px-2 py-1 bg-slate-800 text-slate-300 rounded">
              Difficulty: <span className="capitalize text-white">{currentQ.difficulty}</span>
            </div>
          </div>
          
          <h2 className="text-xl font-medium text-white mb-8 leading-relaxed">
            {currentQ.question_text}
          </h2>

          <div className="space-y-3 mt-auto">
            {currentQ.options?.map((option: string, i: number) => {
              const isSelected = answers[currentQ.id] === option;
              return (
                <button
                  key={i}
                  onClick={() => handleSelectOption(currentQ.id, option)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    isSelected 
                      ? "bg-violet-600/20 border-violet-500 text-violet-50" 
                      : "bg-slate-800/50 border-slate-700 text-slate-300 hover:bg-slate-700 hover:border-slate-600"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                      isSelected ? "border-violet-500" : "border-slate-600"
                    }`}>
                      {isSelected && <div className="w-2.5 h-2.5 bg-violet-500 rounded-full"></div>}
                    </div>
                    <span>{option}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="px-6 py-2.5 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>

          {isLastQuestion ? (
            <button
              onClick={handleSubmit}
              disabled={!allAnswered || submitting}
              className="flex items-center gap-2 px-8 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-violet-500/20"
            >
              {submitting ? <Loader2 className="animate-spin" size={18} /> : "Complete Session"}
            </button>
          ) : (
            <button
              onClick={handleNext}
              disabled={!answers[currentQ.id]}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next <ArrowRight size={18} />
            </button>
          )}
        </div>
      </div>

      {/* AI Assistant Sidebar */}
      <div className="w-80 flex flex-col gap-4">
        {/* AI Hint Box */}
        <div className="surface-panel p-5 rounded-2xl border-blue-500/30">
          <h3 className="font-semibold text-blue-400 mb-3 flex items-center gap-2">
            <Lightbulb size={18} /> AI Hint
          </h3>
          {aiHint ? (
            <div className="text-sm text-slate-300 leading-relaxed p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
              {aiHint}
            </div>
          ) : (
            <div className="text-sm text-slate-400 mb-4">Stuck on this question? Get a gentle nudge in the right direction without revealing the answer.</div>
          )}
          
          {!aiHint && (
            <button 
              onClick={getHint}
              disabled={hintLoading}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-blue-400 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {hintLoading ? <Loader2 className="animate-spin" size={16} /> : "Request Hint"}
            </button>
          )}
        </div>

        {/* AI Explain Topic */}
        <div className="surface-panel p-5 rounded-2xl border-emerald-500/30 flex-1 flex flex-col">
          <h3 className="font-semibold text-emerald-400 mb-3 flex items-center gap-2">
            <Bot size={18} /> AI Tutor
          </h3>
          
          {aiExplanation ? (
            <div className="text-sm text-slate-300 leading-relaxed overflow-y-auto pr-2 custom-scrollbar">
              {aiExplanation.split('\n').map((line, i) => (
                <p key={i} className="mb-2">{line}</p>
              ))}
            </div>
          ) : (
            <>
              <div className="text-sm text-slate-400 mb-4">
                Need a refresher on <strong>{practice.topic_name}</strong>? Ask the AI Tutor for a quick breakdown.
              </div>
              <button 
                onClick={getExplanation}
                disabled={explainLoading}
                className="w-full mt-auto py-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {explainLoading ? <Loader2 className="animate-spin" size={16} /> : "Explain Topic"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
