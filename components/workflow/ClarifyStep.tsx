import { useState } from "react";
import type { ClarifyingQuestion, QuestionAnswer } from "@/lib/types";

interface ClarifyStepProps {
  questions: ClarifyingQuestion[];
  onSubmit: (answers: QuestionAnswer[]) => void;
  onBack: () => void;
  loading: boolean;
  error: string | null;
}

export default function ClarifyStep({ questions, onSubmit, onBack, loading, error }: ClarifyStepProps) {
  const [answers, setAnswers] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    questions.forEach((q) => { init[q.id] = ""; });
    return init;
  });

  function handleSubmit() {
    const qaList: QuestionAnswer[] = questions.map((q) => ({
      question_id: q.id,
      question: q.question,
      answer: answers[q.id] || q.example_answer,
    }));
    onSubmit(qaList);
  }

  const allAnswered = questions.every((q) => (answers[q.id] || "").trim().length > 0);

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-white/5 rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 p-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Clarifying Questions
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Our AI agent has identified some areas that need clarification to generate a better PRD.
          Answer as many as you can — or use the suggested answers.
        </p>

        <div className="space-y-6">
          {questions.map((q, i) => (
            <div key={q.id} className="clarify-card">
              <div className="flex items-start gap-3 mb-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-600 text-white text-xs flex items-center justify-center font-semibold">
                  {i + 1}
                </span>
                <div className="flex-1">
                  <p className="text-gray-900 dark:text-white font-medium">{q.question}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 italic">{q.rationale}</p>
                </div>
              </div>

              <textarea
                rows={2}
                value={answers[q.id]}
                onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 dark:border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 dark:bg-white/5 dark:text-white placeholder:text-gray-400 text-sm"
                placeholder={q.example_answer}
              />

              {!answers[q.id] && (
                <button
                  type="button"
                  onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: q.example_answer }))}
                  className="text-xs text-violet-400 hover:text-violet-300 mt-1 underline"
                >
                  Use suggested answer
                </button>
              )}
            </div>
          ))}
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mt-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <div className="flex gap-3 mt-8">
          <button
            type="button"
            onClick={onBack}
            disabled={loading}
            className="px-6 py-3 border border-gray-300 dark:border-white/10 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            Back
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading || !allAnswered}
            className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
          >
            {loading && (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {loading ? "Generating PRD..." : "Generate PRD"}
          </button>
        </div>
      </div>
    </div>
  );
}
