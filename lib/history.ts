/** localStorage CRUD for PRD version history. */

import type { HistoryEntry } from "./types";

const STORAGE_KEY = "prd_history";
const MAX_ENTRIES = 20;

function readAll(): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as HistoryEntry[]) : [];
  } catch {
    return [];
  }
}

function writeAll(entries: HistoryEntry[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

export function getHistory(): HistoryEntry[] {
  return readAll().sort((a, b) => b.timestamp - a.timestamp);
}

export function addToHistory(entry: HistoryEntry): void {
  const entries = readAll();
  entries.unshift(entry);
  // Keep only the most recent entries
  writeAll(entries.slice(0, MAX_ENTRIES));
}

export function getHistoryEntry(id: string): HistoryEntry | undefined {
  return readAll().find((e) => e.id === id);
}

export function deleteHistoryEntry(id: string): void {
  writeAll(readAll().filter((e) => e.id !== id));
}

export function generateId(): string {
  return `prd_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}
