import { useState } from "react";
import type { TicketsResponse, Epic, Story } from "@/lib/types";

interface TicketStepProps {
  result: TicketsResponse;
  onStartOver: () => void;
}

export default function TicketStep({ result, onStartOver }: TicketStepProps) {
  const { epics, total_story_count, meta } = result;

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-white dark:bg-white/5 rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Jira-Ready Tickets
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          {epics.length} epic{epics.length !== 1 ? "s" : ""} with {total_story_count} user stor{total_story_count !== 1 ? "ies" : "y"}
        </p>
        <div className="flex gap-4 text-xs text-gray-500 dark:text-gray-400">
          <span>Latency: {(meta.total_latency_ms / 1000).toFixed(1)}s</span>
          <span>Tokens: {meta.total_tokens.toLocaleString()}</span>
          <span>Cost: ${meta.estimated_cost_usd.toFixed(4)}</span>
        </div>
      </div>

      {/* Epics */}
      {epics.map((epic) => (
        <EpicCard key={epic.id} epic={epic} />
      ))}

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onStartOver}
          className="flex-1 bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
        >
          Generate Another PRD
        </button>
      </div>
    </div>
  );
}

function EpicCard({ epic }: { epic: Epic }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="ticket-card">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono bg-violet-500/10 text-violet-400 px-2 py-0.5 rounded">
            {epic.id}
          </span>
          <span className="font-semibold text-gray-900 dark:text-white">{epic.title}</span>
          <span className="text-xs text-gray-400">
            {epic.stories.length} stor{epic.stories.length !== 1 ? "ies" : "y"}
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          <p className="text-sm text-gray-500 dark:text-gray-400">{epic.description}</p>
          {epic.stories.map((story) => (
            <StoryCard key={story.id} story={story} />
          ))}
        </div>
      )}
    </div>
  );
}

function StoryCard({ story }: { story: Story }) {
  const [copied, setCopied] = useState(false);

  function copyStory() {
    const text = [
      `${story.id}: ${story.title}`,
      "",
      story.description,
      "",
      "Acceptance Criteria:",
      ...story.acceptance_criteria.map(
        (ac) => `  Given ${ac.given}\n  When ${ac.when}\n  Then ${ac.then}`
      ),
      "",
      `Story Points: ${story.story_points}`,
    ].join("\n");

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="ticket-story">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">
            {story.id}
          </span>
          <span className="text-sm font-medium text-gray-900 dark:text-white">{story.title}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-gray-200 dark:bg-white/10 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded">
            {story.story_points} SP
          </span>
          <button
            type="button"
            onClick={copyStory}
            className="text-xs text-gray-400 hover:text-white border border-white/10 rounded px-2 py-0.5 transition-colors"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </div>

      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{story.description}</p>

      {story.acceptance_criteria.length > 0 && (
        <div className="space-y-1.5">
          {story.acceptance_criteria.map((ac, i) => (
            <div key={i} className="text-xs bg-gray-50 dark:bg-white/[0.03] rounded p-2 font-mono">
              <div><span className="text-green-400">Given</span> {ac.given}</div>
              <div><span className="text-blue-400">When</span> {ac.when}</div>
              <div><span className="text-violet-400">Then</span> {ac.then}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
