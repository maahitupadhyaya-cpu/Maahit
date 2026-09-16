"use client";

import { Step } from "@/lib/types";
import { MathBlock } from "./MathBlock";

export function StepsPanel({ steps, summary }: { steps: Step[]; summary: string }) {
  return (
    <section className="rounded-2xl border border-ink-200/70 bg-white shadow-panel p-5 sm:p-6 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
          Step-by-step derivation
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto scroll-thin max-h-[520px] pr-1 space-y-4">
        {steps.map((step, i) => (
          <div key={i} className="relative pl-9">
            <div className="absolute left-0 top-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-accent-100 text-accent-700 text-xs font-bold">
              {i + 1}
            </div>
            <h3 className="text-[15px] font-semibold text-ink-900 leading-snug">{step.title}</h3>
            {step.description && (
              <p className="text-sm text-ink-500 mt-0.5">{step.description}</p>
            )}
            {step.latex && (
              <div className="mt-2 rounded-lg bg-ink-50/70 border border-ink-100 px-3 py-2 overflow-x-auto">
                <MathBlock latex={step.latex} />
              </div>
            )}
          </div>
        ))}
        {steps.length === 0 && (
          <p className="text-sm text-ink-400">No steps yet — solve a problem to see the derivation.</p>
        )}
      </div>
      {summary && (
        <div className="mt-4 pt-4 border-t border-ink-100">
          <p className="text-xs font-medium text-ink-400 uppercase tracking-wide mb-1">Summary</p>
          <p className="text-sm text-ink-700 font-medium">{summary}</p>
        </div>
      )}
    </section>
  );
}
