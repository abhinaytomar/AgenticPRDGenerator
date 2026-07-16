"use client"

import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton, useAuth } from "@clerk/nextjs";

import { callFaq, ApiError } from "@/lib/api";
import type { Citation, ChatTurn } from "@/lib/types";
import MarkdownRenderer from "@/components/MarkdownRenderer";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  used_web?: boolean;
  route_reason?: string;
}

const SUGGESTIONS = [
  "What sections should a PRD contain?",
  "How do I write good acceptance criteria?",
  "When should I use RICE vs. MoSCoW?",
  "What are common mistakes in a PRD?",
];

function FaqChat() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const ask = useCallback(
    async (question: string) => {
      const q = question.trim();
      if (!q || loading) return;

      setError(null);
      setInput("");
      // Prior turns become the memory sent to the backend.
      const history: ChatTurn[] = messages.map((m) => ({ role: m.role, content: m.content }));
      setMessages((prev) => [...prev, { role: "user", content: q }]);
      setLoading(true);

      try {
        const token = await getToken();
        const res = await callFaq({ question: q, history }, token);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: res.answer,
            citations: res.citations,
            used_web: res.used_web,
            route_reason: res.route_reason,
          },
        ]);
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [messages, loading, getToken],
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent mb-2">
        PRD & Product Management FAQ
      </h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
        Ask anything about PRDs and product management. Answers are grounded in a curated
        knowledge base (RAG) and, when needed, a live web search — every answer is cited.
      </p>

      {messages.length === 0 && (
        <div className="mb-8 grid gap-2 sm:grid-cols-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => ask(s)}
              className="text-left text-sm rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-[#111113] px-4 py-3 text-gray-600 dark:text-gray-300 hover:border-violet-400 hover:text-violet-500 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="space-y-6">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
            <div
              className={
                m.role === "user"
                  ? "max-w-[85%] rounded-2xl rounded-br-sm bg-violet-600 text-white px-4 py-2.5"
                  : "max-w-[95%] w-full rounded-2xl rounded-bl-sm bg-white dark:bg-[#111113] border border-gray-200 dark:border-gray-800 px-4 py-3"
              }
            >
              {m.role === "user" ? (
                <p className="text-sm whitespace-pre-wrap">{m.content}</p>
              ) : (
                <>
                  <MarkdownRenderer content={m.content} />
                  {typeof m.used_web === "boolean" && (
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span
                        className={
                          "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium " +
                          (m.used_web
                            ? "bg-emerald-500/10 text-emerald-500"
                            : "bg-violet-500/10 text-violet-400")
                        }
                        title={m.route_reason || ""}
                      >
                        {m.used_web ? "Knowledge base + web search" : "Knowledge base"}
                      </span>
                    </div>
                  )}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 border-t border-gray-100 dark:border-gray-800 pt-3">
                      <p className="text-xs font-semibold text-gray-400 mb-1.5">Sources</p>
                      <ol className="space-y-1">
                        {m.citations.map((c) => (
                          <li key={c.n} className="text-xs text-gray-500 dark:text-gray-400">
                            <span className="text-gray-400">[{c.n}]</span>{" "}
                            {c.kind === "web" ? (
                              <a
                                href={c.source}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-violet-400 hover:underline"
                              >
                                {c.title}
                              </a>
                            ) : (
                              <span>
                                <span className="text-gray-300 dark:text-gray-300">{c.title}</span>
                                {c.heading ? <span className="text-gray-500"> — {c.heading}</span> : null}
                                <span className="ml-1 rounded bg-gray-100 dark:bg-gray-800 px-1 text-[10px] uppercase tracking-wide">
                                  kb
                                </span>
                              </span>
                            )}
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-white dark:bg-[#111113] border border-gray-200 dark:border-gray-800 px-4 py-3">
              <div className="flex items-center gap-1.5 text-gray-400">
                <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:-0.3s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:-0.15s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400" />
                <span className="ml-2 text-xs">Retrieving and reasoning…</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="mt-4 text-sm text-red-500">{error}</p>}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        className="sticky bottom-4 mt-6 flex items-end gap-2 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-[#111113] p-2 shadow-lg"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              ask(input);
            }
          }}
          rows={1}
          placeholder="Ask about PRDs or product management…"
          className="flex-1 resize-none bg-transparent px-2 py-2 text-sm text-gray-800 dark:text-gray-100 outline-none placeholder:text-gray-400"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:opacity-40"
        >
          Ask
        </button>
      </form>
    </div>
  );
}

export default function FaqPage() {
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-[#09090b]">
      <nav className="flex items-center justify-between px-6 py-4">
        <Link href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
          &larr; Back
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/product" className="text-sm text-gray-400 hover:text-white transition-colors">
            PRD Generator
          </Link>
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>
      </nav>

      <SignedIn>
        <FaqChat />
      </SignedIn>

      <SignedOut>
        <div className="container mx-auto px-4 py-32 max-w-lg text-center">
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent mb-4">
            PRD & PM FAQ
          </h1>
          <p className="text-gray-400 mb-8">
            Sign in to ask questions about PRDs and product management, answered with cited sources.
          </p>
          <SignInButton mode="modal">
            <button className="bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200">
              Sign In to Get Started
            </button>
          </SignInButton>
        </div>
      </SignedOut>
    </main>
  );
}
