import type { WorkflowStep } from "@/lib/types";

const STEPS: { key: WorkflowStep; label: string }[] = [
  { key: "intake", label: "Describe" },
  { key: "clarify", label: "Clarify" },
  { key: "generate", label: "Generate" },
  { key: "review", label: "Review" },
  { key: "tickets", label: "Tickets" },
];

interface StepIndicatorProps {
  currentStep: WorkflowStep;
}

export default function StepIndicator({ currentStep }: StepIndicatorProps) {
  const currentIndex = STEPS.findIndex((s) => s.key === currentStep);

  return (
    <div className="step-indicator">
      {STEPS.map((step, i) => {
        let status: "completed" | "active" | "upcoming";
        if (i < currentIndex) status = "completed";
        else if (i === currentIndex) status = "active";
        else status = "upcoming";

        return (
          <div key={step.key} className="step-indicator-item">
            <div className={`step-indicator-dot step-indicator-dot--${status}`}>
              {status === "completed" ? (
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M2.5 6L5 8.5L9.5 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              ) : (
                <span className="step-indicator-number">{i + 1}</span>
              )}
            </div>
            <span className={`step-indicator-label step-indicator-label--${status}`}>
              {step.label}
            </span>
            {i < STEPS.length - 1 && (
              <div className={`step-indicator-connector ${i < currentIndex ? "step-indicator-connector--completed" : ""}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
