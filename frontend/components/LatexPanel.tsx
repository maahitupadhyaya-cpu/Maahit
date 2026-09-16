"use client";

import { useState } from "react";

export function LatexPanel({ latex }: { latex: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(latex);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      // clipboard API unavailable — no-op
    }
  };

  const handleDownload = () => {
    const blob = new Blob([latex], { type: "text/x-tex;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "latexify-solution.tex";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-2xl border border-ink-200/70 bg-white shadow-panel p-5 sm:p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">LaTeX source</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="text-xs font-medium rounded-lg border border-ink-200 px-3 py-1.5 text-ink-600 hover:border-accent-300 hover:text-accent-700 transition-colors"
          >
            {copied ? "Copied ✓" : "Copy LaTeX"}
          </button>
          <button
            onClick={handleDownload}
            className="text-xs font-medium rounded-lg bg-accent-600 px-3 py-1.5 text-white hover:bg-accent-700 transition-colors"
          >
            Download .tex
          </button>
        </div>
      </div>
      <pre className="rounded-xl bg-ink-900 text-ink-100 text-[13px] leading-relaxed p-4 overflow-x-auto max-h-72 scroll-thin whitespace-pre-wrap break-words font-mono">
        {latex || "% Your LaTeX solution will appear here."}
      </pre>
    </section>
  );
}
