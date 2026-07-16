import { useState, useMemo } from "react";
import type { HistoryEntry } from "@/lib/types";
import { getHistory, deleteHistoryEntry } from "@/lib/history";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import QualityBadge from "@/components/QualityBadge";

interface HistoryDrawerProps {
  open: boolean;
  onClose: () => void;
}

export default function HistoryDrawer({ open, onClose }: HistoryDrawerProps) {
  const [refreshKey, setRefreshKey] = useState(0);
  const [selected, setSelected] = useState<HistoryEntry | null>(null);

  // Re-derive entries from localStorage when the drawer opens or refreshKey changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const entries = useMemo(() => (open ? getHistory() : []), [open, refreshKey]);

  function handleDelete(id: string) {
    deleteHistoryEntry(id);
    setRefreshKey((k) => k + 1);
    if (selected?.id === id) setSelected(null);
  }

  if (!open) return null;

  return (
    <div className="history-drawer-overlay" onClick={onClose}>
      <div className="history-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-white/10">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            {selected ? "PRD Details" : "Version History"}
          </h2>
          <button
            type="button"
            onClick={selected ? () => setSelected(null) : onClose}
            className="text-gray-400 hover:text-white"
          >
            {selected ? (
              <span className="text-sm">&larr; Back</span>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            )}
          </button>
        </div>

        <div className="p-4 overflow-y-auto flex-1">
          {selected ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Product</h3>
                <p className="text-gray-900 dark:text-white">{selected.intake.product_name}</p>
              </div>
              <div className="flex gap-4">
                <div className="flex items-center gap-1">
                  <span className="text-xs text-gray-400">Quality:</span>
                  <QualityBadge score={selected.evaluation.quality_score} />
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-xs text-gray-400">Confidence:</span>
                  <QualityBadge score={selected.evaluation.confidence_score} />
                </div>
              </div>
              <MarkdownRenderer content={selected.prd_markdown} />
            </div>
          ) : entries.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">No PRDs generated yet.</p>
          ) : (
            <div className="space-y-2">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 cursor-pointer transition-colors"
                  onClick={() => setSelected(entry)}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {entry.intake.product_name}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(entry.timestamp).toLocaleDateString()} {new Date(entry.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-3">
                    <QualityBadge score={entry.evaluation.quality_score} />
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); handleDelete(entry.id); }}
                      className="text-gray-400 hover:text-red-400 p-1"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M18 6L6 18M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
