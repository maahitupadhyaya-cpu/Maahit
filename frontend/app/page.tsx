import Link from "next/link";
import { CATEGORIES, solveHref } from "@/lib/categories";
import { MathSymbolsField } from "@/components/MathSymbolsField";

const WORKFLOW = [
  { n: "01", title: "Enter", body: "Type a calculus, ODE, matrix, stats, or probability problem in plain math notation." },
  { n: "02", title: "Solve", body: "SymPy computes an exact symbolic result for the selected topic." },
  { n: "03", title: "Explain", body: "A numbered derivation walks through the method, not just the final line." },
  { n: "04", title: "LaTeXify", body: "Copy or download a clean LaTeX transcript of every step." },
  { n: "05", title: "Visualize", body: "An interactive Plotly graph is generated for the same problem." },
  { n: "06", title: "Export", body: "Take the .tex source and a PNG of the graph into your notes or report." },
];

const FEATURES = [
  {
    title: "Step-by-step derivation",
    body: "Each stage is titled, explained in words, and rendered with KaTeX so the algebra is readable.",
  },
  {
    title: "Publication-ready LaTeX",
    body: "The full solution is assembled as copy-pasteable source. Copy LaTeX or download a .tex file.",
  },
  {
    title: "Interactive graphs",
    body: "Functions, solution curves, eigenvectors, 3D surfaces, histograms, and probability densities, downloadable as PNG.",
  },
];

export default function HomePage() {
  return (
    <div>
      <section className="relative overflow-hidden border-b border-ink-200/70">
        <div className="pointer-events-none absolute inset-0 landing-hero" />
        <MathSymbolsField variant="home" />
        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <p className="animate-fade-up text-xs font-semibold uppercase tracking-[0.18em] text-accent-600">
            For students of mathematics
          </p>
          <h1 className="animate-fade-up mt-4 max-w-3xl font-serif text-4xl sm:text-5xl lg:text-[3.25rem] font-semibold leading-[1.15] text-ink-900" style={{ animationDelay: "80ms" }}>
            From a typed problem to a solved, explained, and visualized result.
          </h1>
          <p className="animate-fade-up mt-5 max-w-2xl text-base sm:text-lg text-ink-600 leading-relaxed" style={{ animationDelay: "160ms" }}>
            LaTeXify is a modeling workspace for calculus, differential equations, linear algebra,
            optimization, statistics, and probability. Enter a problem, then walk the path:
            solve → explain → LaTeXify → visualize → export.
          </p>
          <div className="animate-fade-up mt-8 flex flex-wrap items-center gap-3" style={{ animationDelay: "240ms" }}>
            <Link
              href={solveHref("calculus")}
              className="inline-flex items-center rounded-xl bg-accent-600 px-5 py-2.5 text-sm font-semibold text-white shadow-panel hover:bg-accent-700 transition-colors"
            >
              Start solving
            </Link>
            <a
              href="#topics"
              className="inline-flex items-center rounded-xl border border-ink-200 bg-white/80 px-5 py-2.5 text-sm font-semibold text-ink-700 hover:border-accent-300 hover:text-accent-700 transition-colors"
            >
              Browse topics
            </a>
            <Link
              href="/about"
              className="inline-flex items-center px-2 py-2.5 text-sm font-medium text-ink-500 hover:text-accent-700 transition-colors"
            >
              About us
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
        <h2 className="font-serif text-2xl sm:text-3xl text-ink-900">How it works</h2>
        <p className="mt-2 text-sm text-ink-500 max-w-2xl">
          One workspace, six steps. Use the navbar to jump straight into a topic.
        </p>
        <ol className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {WORKFLOW.map((step) => (
            <li key={step.n} className="rounded-2xl border border-ink-200/70 bg-white p-5 shadow-panel">
              <span className="text-xs font-semibold tracking-widest text-accent-600">{step.n}</span>
              <h3 className="mt-2 text-base font-semibold text-ink-900">{step.title}</h3>
              <p className="mt-1.5 text-sm text-ink-500 leading-relaxed">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="border-y border-ink-200/70 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
            <div className="max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-600">About</p>
              <h2 className="mt-3 font-serif text-2xl sm:text-3xl text-ink-900">Why this exists</h2>
              <p className="mt-4 text-base text-ink-600 leading-relaxed">
                I built LaTeXify after watching classmates and friends struggle with LaTeX and Mathematica
                graphs for assignments, hours spent on formatting instead of the math. The full story is on
                the About page.
              </p>
            </div>
            <Link
              href="/about"
              className="inline-flex shrink-0 items-center rounded-xl border border-ink-200 bg-ink-50 px-5 py-2.5 text-sm font-semibold text-ink-800 hover:border-accent-300 hover:text-accent-700 transition-colors"
            >
              Read about us →
            </Link>
          </div>
        </div>
      </section>

      <section id="topics" className="border-b border-ink-200/70 bg-ink-50/40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
          <h2 className="font-serif text-2xl sm:text-3xl text-ink-900">Topics</h2>
          <p className="mt-2 text-sm text-ink-500 max-w-2xl">
            Each section opens the same solver, preloaded with that model and a worked example.
          </p>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {CATEGORIES.map((c) => (
              <Link
                key={c.id}
                href={solveHref(c.id)}
                className="group rounded-2xl border border-ink-200/70 bg-ink-50/40 p-5 hover:border-accent-300 hover:bg-accent-50/40 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-white border border-ink-100 font-serif text-lg text-accent-700">
                    {c.icon}
                  </span>
                  <span className="text-xs font-medium text-ink-400 group-hover:text-accent-600">Open →</span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-ink-900">{c.label}</h3>
                <p className="mt-1 text-sm text-ink-500">{c.blurb}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
        <h2 className="font-serif text-2xl sm:text-3xl text-ink-900">What you take away</h2>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="rounded-2xl border border-ink-200/70 bg-white p-5 shadow-panel">
              <h3 className="text-base font-semibold text-ink-900">{f.title}</h3>
              <p className="mt-2 text-sm text-ink-500 leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
        <div className="mt-10 rounded-2xl bg-ink-900 text-white px-6 py-8 sm:px-10 sm:py-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5">
          <div>
            <h2 className="font-serif text-2xl">Ready to try a problem?</h2>
            <p className="mt-2 text-sm text-ink-300 max-w-lg">
              Open the workspace, or jump to a topic from the navbar above.
            </p>
          </div>
          <Link
            href={solveHref("calculus")}
            className="inline-flex shrink-0 items-center justify-center rounded-xl bg-accent-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-400 transition-colors"
          >
            Open workspace
          </Link>
        </div>
      </section>
    </div>
  );
}
