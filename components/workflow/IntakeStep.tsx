import { useState, FormEvent } from "react";
import type { IntakeData } from "@/lib/types";

interface IntakeStepProps {
  onSubmit: (data: IntakeData) => void;
  loading: boolean;
  error: string | null;
}

export default function IntakeStep({ onSubmit, loading, error }: IntakeStepProps) {
  const [productName, setProductName] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [context, setContext] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit({ product_name: productName, problem_statement: problemStatement, context });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-white/5 rounded-2xl shadow-2xl border border-gray-200 dark:border-white/10 p-8">
      <div className="space-y-2">
        <label htmlFor="product-name" className="block uppercase text-xs tracking-wider font-semibold text-gray-500 dark:text-gray-400">
          Product Name
        </label>
        <input
          id="product-name"
          type="text"
          required
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 dark:bg-white/5 dark:text-white placeholder:text-gray-400"
          placeholder="Enter your product name"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="problem-statement" className="block uppercase text-xs tracking-wider font-semibold text-gray-500 dark:text-gray-400">
          Problem Statement
        </label>
        <textarea
          id="problem-statement"
          required
          rows={3}
          maxLength={500}
          value={problemStatement}
          onChange={(e) => setProblemStatement(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 dark:bg-white/5 dark:text-white placeholder:text-gray-400"
          placeholder="What problem does this product solve?"
        />
        <p className="text-xs text-gray-400 text-right">{problemStatement.length} / 500</p>
      </div>

      <div className="space-y-2">
        <label htmlFor="context" className="block uppercase text-xs tracking-wider font-semibold text-gray-500 dark:text-gray-400">
          Additional Context
        </label>
        <textarea
          id="context"
          rows={8}
          maxLength={2000}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 dark:bg-white/5 dark:text-white placeholder:text-gray-400"
          placeholder="Any additional details — target users, key features, constraints, etc."
        />
        <p className="text-xs text-gray-400 text-right">{context.length} / 2000</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
      >
        {loading && (
          <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {loading ? "Analyzing Product Idea..." : "Start PRD Generation"}
      </button>
    </form>
  );
}
