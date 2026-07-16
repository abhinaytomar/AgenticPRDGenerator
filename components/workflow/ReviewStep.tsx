import { useState } from "react";
import type { GenerateResponse, StepMeta } from "@/lib/types";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import QualityBadge from "@/components/QualityBadge";

interface ReviewStepProps {
  result: GenerateResponse;
  onApprove: () => void;
  onGenerateTickets: () => void;
  onReject: () => void;
  loading: boolean;
}

export default function ReviewStep({ result, onApprove, onGenerateTickets, onReject, loading }: ReviewStepProps) {
  const [copied, setCopied] = useState(false);
  const [showIssues, setShowIssues] = useState(false);

  const { evaluation, prd_markdown, revision_applied, meta } = result;

  async function copyMarkdown() {
    await navigator.clipboard.writeText(prd_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="space-y-6">
      {/* Quality overview */}
      <div className="bg-white dark:bg-white/5 rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">PRD Evaluation</h2>
          {revision_applied && (
            <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full px-3 py-1">
              Revision applied
            </span>
          )}
        </div>

        <div className="flex gap-6 mb-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Quality</span>
            <QualityBadge score={evaluation.quality_score} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Confidence</span>
            <QualityBadge score={evaluation.confidence_score} />
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium px-2 py-0.5 rounded ${
              evaluation.readiness === "ready"
                ? "bg-green-500/10 text-green-400"
                : evaluation.readiness === "needs_revision"
                  ? "bg-amber-500/10 text-amber-400"
                  : "bg-red-500/10 text-red-400"
            }`}>
              {evaluation.readiness.replace("_", " ")}
            </span>
          </div>
        </div>

        {/* Stats */}
        <MetaStats meta={meta} />

        {/* Issues accordion */}
        {evaluation.issues.length > 0 && (
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setShowIssues(!showIssues)}
              className="text-sm text-violet-400 hover:text-violet-300 flex items-center gap-1"
            >
              <svg
                className={`w-4 h-4 transition-transform ${showIssues ? "rotate-90" : ""}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              {evaluation.issues.length} issue{evaluation.issues.length !== 1 ? "s" : ""} found
            </button>

            {showIssues && (
              <div className="mt-3 space-y-2">
                {evaluation.issues.map((issue, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm p-2 rounded bg-gray-50 dark:bg-white/[0.03]">
                    <span className={`flex-shrink-0 text-xs font-medium px-1.5 py-0.5 rounded ${
                      issue.severity === "critical"
                        ? "bg-red-500/10 text-red-400"
                        : issue.severity === "major"
                          ? "bg-amber-500/10 text-amber-400"
                          : "bg-blue-500/10 text-blue-400"
                    }`}>
                      {issue.severity}
                    </span>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">[{issue.category}] {issue.location}:</span>{" "}
                      <span className="text-gray-900 dark:text-gray-200">{issue.suggestion}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* PRD content */}
      <div className="bg-gray-50 dark:bg-white/[0.03] rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 border-t-2 border-t-violet-500 p-8">
        <div className="flex justify-end mb-4">
          <button
            type="button"
            onClick={copyMarkdown}
            className="text-xs text-gray-400 hover:text-white border border-white/10 rounded px-2 py-1 transition-colors"
          >
            {copied ? "Copied!" : "Copy Markdown"}
          </button>
        </div>
        <MarkdownRenderer content={prd_markdown} />
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onReject}
          className="px-6 py-3 border border-gray-300 dark:border-white/10 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-white/5 transition-colors"
        >
          Start Over
        </button>
        <button
          type="button"
          onClick={onApprove}
          className="px-6 py-3 border border-green-500/30 text-green-400 rounded-lg hover:bg-green-500/10 transition-colors"
        >
          Approve &amp; Save
        </button>
        <button
          type="button"
          onClick={onGenerateTickets}
          disabled={loading}
          className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {loading && (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          {loading ? "Generating Tickets..." : "Generate Jira Tickets"}
        </button>
      </div>
    </div>
  );
}

function MetaStats({ meta }: { meta: StepMeta }) {
  return (
    <div className="flex gap-4 text-xs text-gray-500 dark:text-gray-400">
      <span>Latency: {(meta.total_latency_ms / 1000).toFixed(1)}s</span>
      <span>Tokens: {meta.total_tokens.toLocaleString()}</span>
      <span>Cost: ${meta.estimated_cost_usd.toFixed(4)}</span>
      <span>Steps: {meta.steps.length}</span>
    </div>
  );
}
