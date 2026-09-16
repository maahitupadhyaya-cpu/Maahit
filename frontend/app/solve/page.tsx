import { Suspense } from "react";
import type { Metadata } from "next";
import { SolverWorkspace } from "@/components/SolverWorkspace";

export const metadata: Metadata = {
  title: "Solve — LaTeXify",
  description: "Solve a mathematical problem with step-by-step derivation, LaTeX, and an interactive graph.",
};

export default function SolvePage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-7xl px-4 py-16 text-sm text-ink-400">Loading workspace…</main>
      }
    >
      <SolverWorkspace />
    </Suspense>
  );
}
