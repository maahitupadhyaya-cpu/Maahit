"use client";

import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { ProblemInput } from "@/components/ProblemInput";
import { StepsPanel } from "@/components/StepsPanel";
import { LatexPanel } from "@/components/LatexPanel";
import { ErrorBanner, WarningBanner } from "@/components/Banners";
import { solveProblem, ApiRequestError } from "@/lib/api";
import { defaultProblem, isCategoryId, solveHref } from "@/lib/categories";
import { CategoryId, SolveResponse } from "@/lib/types";

const GraphPanel = dynamic(() => import("@/components/GraphPanel").then((m) => m.GraphPanel), {
  ssr: false,
  loading: () => (
    <div className="rounded-2xl border border-ink-200/70 bg-white shadow-panel p-6 h-full min-h-[460px] flex items-center justify-center text-sm text-ink-400">
      Loading graph engine…
    </div>
  ),
});

export function SolverWorkspace() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");
  const initialCategory: CategoryId = isCategoryId(categoryParam) ? categoryParam : "calculus";

  const [category, setCategory] = useState<CategoryId>(initialCategory);
  const [problem, setProblem] = useState(defaultProblem(initialCategory));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const appliedCategory = useRef<CategoryId>(initialCategory);

  useEffect(() => {
    const next: CategoryId = isCategoryId(categoryParam) ? categoryParam : "calculus";
    if (appliedCategory.current === next) return;
    appliedCategory.current = next;
    setCategory(next);
    setProblem(defaultProblem(next));
    setResult(null);
    setError(null);
  }, [categoryParam]);

  const handleCategoryChange = (c: CategoryId) => {
    if (c === category) return;
    router.replace(solveHref(c), { scroll: false });
  };

  const handleSolve = useCallback(async () => {
    if (!problem.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await solveProblem(category, problem.trim());
      setResult(res);
    } catch (e) {
      setResult(null);
      setError(e instanceof ApiRequestError ? e.message : "Unexpected error. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [category, problem, loading]);

  return (
    <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-accent-600">Workspace</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink-900">Solve &amp; visualize</h1>
        <p className="mt-1 text-sm text-ink-500">
          Pick a topic from the navbar or below, enter a problem, then generate steps, LaTeX, and a graph.
        </p>
      </div>

      <ProblemInput
        category={category}
        onCategoryChange={handleCategoryChange}
        problem={problem}
        onProblemChange={setProblem}
        onSolve={handleSolve}
        loading={loading}
      />

      {error && <ErrorBanner message={error} />}
      {result && <WarningBanner warnings={result.warnings} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        <StepsPanel steps={result?.steps ?? []} summary={result?.summary ?? ""} />
        <GraphPanel plot={result?.plot ?? null} />
      </div>

      <LatexPanel latex={result?.latex ?? ""} />
    </main>
  );
}
