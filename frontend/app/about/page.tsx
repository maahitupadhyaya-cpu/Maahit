import type { Metadata } from "next";
import Link from "next/link";
import { MathSymbolsField } from "@/components/MathSymbolsField";
import { solveHref } from "@/lib/categories";

export const metadata: Metadata = {
  title: "About | LaTeXify",
  description:
    "Why Maahit Upadhyaya created LaTeXify: a student workspace for solutions, LaTeX, and graphs without fighting the tools.",
};

const PILLARS = [
  { glyph: "∫", title: "Solve", body: "Get an exact result instead of hunting through a CAS notebook." },
  { glyph: "∑", title: "Explain", body: "Walk the derivation so the assignment is understood, not just submitted." },
  { glyph: "π", title: "LaTeXify", body: "Copy typeset source without wrestling braces and packages at midnight." },
  { glyph: "∞", title: "Visualize", body: "Generate the graph that matches the solution, without a Mathematica plot ritual." },
];

export default function AboutPage() {
  return (
    <div>
      <section className="relative overflow-hidden border-b border-ink-200/70">
        <div className="pointer-events-none absolute inset-0 landing-hero" />
        <MathSymbolsField variant="about" />
        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <p className="animate-fade-up text-xs font-semibold uppercase tracking-[0.18em] text-accent-600">
            About us
          </p>
          <h1 className="animate-fade-up mt-4 max-w-3xl font-serif text-4xl sm:text-5xl font-semibold leading-[1.15] text-ink-900" style={{ animationDelay: "80ms" }}>
            Built by a student, for students who were tired of fighting the tools.
          </h1>
          <p className="animate-fade-up mt-5 max-w-2xl text-base sm:text-lg text-ink-600 leading-relaxed" style={{ animationDelay: "160ms" }}>
            LaTeXify exists because the math was never the hard part. Formatting it, and drawing the graph
            that belonged with it, was.
          </p>
        </div>
      </section>

      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
            <div className="lg:col-span-4">
              <div className="rounded-3xl border border-ink-200/70 bg-white p-7 shadow-panel text-center">
                <div className="founder-mark mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-accent-600 text-white font-serif text-4xl shadow-panel">
                  M
                </div>
                <h2 className="mt-5 font-serif text-2xl text-ink-900">Maahit Upadhyaya</h2>
                <p className="mt-1 text-sm font-medium text-accent-700">Founder</p>
                <p className="mt-4 text-sm text-ink-500 leading-relaxed">
                  I started LaTeXify after watching classmates and friends lose nights to LaTeX and Mathematica
                  instead of the problem in front of them.
                </p>
              </div>
            </div>

            <div className="lg:col-span-8">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-600">Why</p>
              <h2 className="mt-3 font-serif text-2xl sm:text-3xl text-ink-900">Why I created LaTeXify</h2>
              <div className="mt-6 space-y-4 text-base text-ink-600 leading-relaxed">
                <p>
                  I built LaTeXify after watching my classmates and friends struggle, not with the math itself,
                  but with the tools around it. Assignments asked for a clean derivation, properly typeset LaTeX,
                  and a graph that actually matched the solution. Getting there meant fighting LaTeX syntax one
                  night and Mathematica plotting the next.
                </p>
                <p>
                  Hours went into formatting instead of understanding. A small mistake in a plot command, a missing
                  brace in a <span className="font-mono text-sm text-ink-800">.tex</span> file, and the whole evening
                  disappeared. I wanted a workspace where a student could type a problem and walk out with the
                  explanation, the LaTeX, and the visualization, ready for study or for the assignment.
                </p>
                <p>
                  That is LaTeXify: enter a problem, solve it, see the steps, copy the LaTeX, and generate the graph
                  in one place.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {PILLARS.map((p) => (
              <div key={p.title} className="rounded-2xl border border-ink-200/70 bg-white p-5 shadow-panel">
                <span className="font-serif text-2xl text-accent-600">{p.glyph}</span>
                <h3 className="mt-3 text-base font-semibold text-ink-900">{p.title}</h3>
                <p className="mt-1.5 text-sm text-ink-500 leading-relaxed">{p.body}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 rounded-2xl bg-ink-900 text-white px-6 py-8 sm:px-10 sm:py-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5 relative overflow-hidden">
            <div className="pointer-events-none absolute inset-0 opacity-20 font-serif text-6xl text-white">
              <span className="absolute left-6 top-4 math-symbol-float" style={{ animationDuration: "10s" }}>∫</span>
              <span className="absolute right-10 bottom-3 math-symbol-drift" style={{ animationDuration: "12s" }}>∑</span>
            </div>
            <div className="relative">
              <h2 className="font-serif text-2xl">Try the workspace</h2>
              <p className="mt-2 text-sm text-ink-300 max-w-lg">
                Type a problem. Leave with the solution, the LaTeX, and the graph.
              </p>
            </div>
            <Link
              href={solveHref("calculus")}
              className="relative inline-flex shrink-0 items-center justify-center rounded-xl bg-accent-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-400 transition-colors"
            >
              Open workspace
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
