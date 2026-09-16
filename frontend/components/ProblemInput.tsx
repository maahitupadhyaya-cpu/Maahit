"use client";

import clsx from "clsx";
import { CATEGORIES, EXAMPLES } from "@/lib/categories";
import { CategoryId } from "@/lib/types";

interface Props {
  category: CategoryId;
  onCategoryChange: (c: CategoryId) => void;
  problem: string;
  onProblemChange: (p: string) => void;
  onSolve: () => void;
  loading: boolean;
}

export function ProblemInput({
  category,
  onCategoryChange,
  problem,
  onProblemChange,
  onSolve,
  loading,
}: Props) {
  const meta = CATEGORIES.find((c) => c.id === category)!;
  const examples = EXAMPLES[category] || [];

  return (
    <section className="rounded-2xl border border-ink-200/70 bg-white shadow-panel p-5 sm:p-6">
      <div className="flex flex-wrap gap-2 mb-5">
        {CATEGORIES.map((c) => (
          <button
            key={c.id}
            onClick={() => onCategoryChange(c.id)}
            className={clsx(
              "flex items-center gap-2 rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors border",
              category === c.id
                ? "bg-accent-600 text-white border-accent-600 shadow-sm"
                : "bg-white text-ink-600 border-ink-200 hover:border-accent-300 hover:text-accent-700"
            )}
          >
            <span className="font-serif text-[13px] opacity-80">{c.icon}</span>
            {c.label}
          </button>
        ))}
      </div>

      <p className="text-sm text-ink-500 mb-3">{meta.blurb}</p>

      <textarea
        value={problem}
        onChange={(e) => onProblemChange(e.target.value)}
        placeholder={meta.placeholder}
        rows={4}
        className="w-full resize-none rounded-xl border border-ink-200 bg-ink-50/50 px-4 py-3 text-[15px] leading-relaxed text-ink-900 placeholder:text-ink-400 focus:border-accent-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-accent-100 transition-colors font-mono"
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
            e.preventDefault();
            onSolve();
          }
        }}
      />

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-ink-400 mr-1">Try:</span>
        {examples.map((ex) => (
          <button
            key={ex}
            onClick={() => onProblemChange(ex)}
            className="rounded-full border border-ink-200 bg-ink-50 px-3 py-1 text-xs text-ink-600 hover:border-accent-300 hover:bg-accent-50 hover:text-accent-700 transition-colors max-w-full truncate"
            title={ex}
          >
            {ex.length > 46 ? ex.slice(0, 44) + "…" : ex}
          </button>
        ))}
      </div>

      <div className="mt-5 flex items-center justify-between gap-3">
        <p className="text-xs text-ink-400">
          Tip: press <kbd className="rounded bg-ink-100 px-1.5 py-0.5 font-sans">⌘/Ctrl</kbd> + <kbd className="rounded bg-ink-100 px-1.5 py-0.5 font-sans">Enter</kbd> to solve
        </p>
        <button
          onClick={onSolve}
          disabled={loading || !problem.trim()}
          className={clsx(
            "inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold text-white shadow-panel transition-all",
            loading || !problem.trim()
              ? "bg-ink-300 cursor-not-allowed"
              : "bg-accent-600 hover:bg-accent-700 active:scale-[0.98]"
          )}
        >
          {loading ? (
            <>
              <span className="h-3.5 w-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
              Solving…
            </>
          ) : (
            <>Solve &amp; Visualize</>
          )}
        </button>
      </div>
    </section>
  );
}
