import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { Loader2, CheckCircle, ArrowRight, BarChart } from "lucide-react";

export default function Assessment() {
  const { subjectId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [assessment, setAssessment] = useState<any>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [results, setResults] = useState<any>(null);
  const [sessionStartTime, setSessionStartTime] = useState<number>(0);

  useEffect(() => {
    const startAssessment = async () => {
      try {
        const response = await api.post("/assessment/start", {
          subject_id: parseInt(subjectId || "1"),
          assessment_type: "diagnostic",
          num_questions: 10
        });
        setAssessment(response.data);
        setSessionStartTime(Date.now());
      } catch (error) {
        console.error("Failed to start assessment", error);
      } finally {
        setLoading(false);
      }
    };
    startAssessment();
  }, [subjectId]);

  const handleSelectOption = (questionId: number, option: string) => {
    setAnswers({ ...answers, [questionId]: option });
  };

  const handleNext = () => {
    if (currentQuestionIndex < assessment.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
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

      const response = await api.post("/assessment/submit", {
        assessment_id: assessment.assessment_id,
        answers: formattedAnswers
      });
      setResults(response.data);
    } catch (error) {
      console.error("Failed to submit assessment", error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-slate-400">
        <Loader2 size={48} className="animate-spin text-blue-500 mb-4" />
        <p>Generating adaptive diagnostic test...</p>
      </div>
    );
  }

  if (results) {
    return (
      <div className="max-w-3xl mx-auto py-12 animate-fade-in">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-4 bg-emerald-500/10 rounded-full text-emerald-500 mb-6">
            <CheckCircle size={48} />
          </div>
          <h1 className="text-4xl font-outfit font-bold text-white mb-4">Assessment Complete!</h1>
          <p className="text-xl text-slate-400">You scored <span className="text-white font-bold">{Math.round(results.score_percentage)}%</span></p>
          <div className="text-emerald-400 font-medium mt-2">+{results.xp_earned} XP Earned</div>
        </div>

        <div className="surface-panel p-8 rounded-2xl mb-8">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <BarChart className="text-blue-400" /> Topic Analysis
          </h2>
          <div className="space-y-6">
            {results.topic_results.map((tr: any) => (
              <div key={tr.topic_id} className="border-b border-slate-800 pb-4 last:border-0 last:pb-0">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-semibold text-white">{tr.topic_name}</h3>
                  <div className="text-sm font-medium">
                    {tr.mastery_delta > 0 ? (
                      <span className="text-emerald-400">+{tr.mastery_delta.toFixed(1)}%</span>
                    ) : tr.mastery_delta < 0 ? (
                      <span className="text-red-400">{tr.mastery_delta.toFixed(1)}%</span>
                    ) : (
                      <span className="text-slate-400">No Change</span>
                    )}
                  </div>
                </div>
                <div className="flex justify-between text-sm text-slate-400 mb-2">
                  <span>Accuracy: {Math.round(tr.accuracy)}% ({tr.correct_answers}/{tr.total_questions})</span>
                  <span>New Mastery: {Math.round(tr.mastery_after)}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-blue-500 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${Math.max(5, tr.mastery_after)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center">
          <button 
            onClick={() => navigate("/student")}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors shadow-lg shadow-blue-500/20"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!assessment) return <div>Failed to load assessment.</div>;

  const currentQ = assessment.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === assessment.questions.length - 1;
  const allAnswered = Object.keys(answers).length === assessment.questions.length;

  return (
    <div className="max-w-3xl mx-auto py-8 animate-fade-in">
      <div className="flex justify-between items-center mb-8 text-sm font-medium text-slate-400">
        <div>{assessment.assessment_type.toUpperCase()} - {assessment.subject_name}</div>
        <div>Question {currentQuestionIndex + 1} of {assessment.questions.length}</div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-slate-800 rounded-full h-2 mb-12 overflow-hidden">
        <div 
          className="bg-blue-500 h-full transition-all duration-300"
          style={{ width: `${((currentQuestionIndex) / assessment.questions.length) * 100}%` }}
        ></div>
      </div>

      <div className="surface-panel p-8 rounded-2xl mb-8 min-h-[400px] flex flex-col">
        <div className="mb-4 text-xs font-medium px-2 py-1 bg-slate-800 text-slate-300 rounded inline-block self-start">
          Topic: {currentQ.topic_name}
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
                    ? "bg-blue-600/20 border-blue-500 text-blue-50" 
                    : "bg-slate-800/50 border-slate-700 text-slate-300 hover:bg-slate-700 hover:border-slate-600"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                    isSelected ? "border-blue-500" : "border-slate-600"
                  }`}>
                    {isSelected && <div className="w-2.5 h-2.5 bg-blue-500 rounded-full"></div>}
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
            className="flex items-center gap-2 px-8 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-emerald-500/20"
          >
            {submitting ? <Loader2 className="animate-spin" size={18} /> : "Submit Assessment"}
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={!answers[currentQ.id]}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next <ArrowRight size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
