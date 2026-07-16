import type { GenerationSubstep } from "@/lib/types";

interface GenerationStepProps {
  substep: GenerationSubstep;
  error: string | null;
}

const SUBSTEPS: { key: GenerationSubstep; label: string; description: string }[] = [
  { key: "researching", label: "Research Agent", description: "Analyzing market context, target audience, and technical landscape" },
  { key: "writing", label: "Writer Agent", description: "Drafting comprehensive PRD with structured requirements" },
  { key: "evaluating", label: "Critic Agent", description: "Evaluating PRD quality, completeness, and actionability" },
  { key: "revising", label: "Revision Agent", description: "Applying improvements based on critic feedback" },
  { key: "done", label: "Complete", description: "PRD generation finished" },
];

export default function GenerationStep({ substep, error }: GenerationStepProps) {
  const currentIndex = SUBSTEPS.findIndex((s) => s.key === substep);

  if (error) {
    return (
      <div className="bg-white dark:bg-white/5 rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 p-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-white/5 rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 p-8">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        Generating Your PRD
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
        Our AI agents are collaborating to produce a comprehensive PRD.
      </p>

      <div className="space-y-4">
        {SUBSTEPS.filter((s) => s.key !== "done").map((step, i) => {
          let status: "completed" | "active" | "upcoming";
          if (i < currentIndex) status = "completed";
          else if (i === currentIndex) status = "active";
          else status = "upcoming";

          return (
            <div key={step.key} className={`generation-substep generation-substep--${status}`}>
              <div className="flex items-center gap-3">
                <div className={`generation-substep-icon generation-substep-icon--${status}`}>
                  {status === "completed" ? (
                    <svg width="14" height="14" viewBox="0 0 12 12" fill="none">
                      <path d="M2.5 6L5 8.5L9.5 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : status === "active" ? (
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-gray-400" />
                  )}
                </div>
                <div>
                  <p className={`font-medium ${status === "upcoming" ? "text-gray-400" : "text-gray-900 dark:text-white"}`}>
                    {step.label}
                  </p>
                  <p className={`text-xs ${status === "upcoming" ? "text-gray-500" : "text-gray-500 dark:text-gray-400"}`}>
                    {step.description}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
