"use client";

import { useRef, useState } from "react";
import { PlotSpec } from "@/lib/types";
import Plot, { Plotly } from "@/lib/plotly-component";

// NOTE: this component must only ever be rendered on the client (it is
// loaded via `next/dynamic(..., { ssr: false })` from the page), because
// plotly.js touches `window`/`document` at import time.

export function GraphPanel({ plot }: { plot: PlotSpec | null }) {
  const gdRef = useRef<any>(null);
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    if (!gdRef.current) return;
    setDownloading(true);
    try {
      await Plotly.downloadImage(gdRef.current, {
        format: "png",
        filename: "latexify-graph",
        width: 1000,
        height: 700,
      });
    } finally {
      setDownloading(false);
    }
  };

  return (
    <section className="rounded-2xl border border-ink-200/70 bg-white shadow-panel p-5 sm:p-6 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
          Interactive graph
        </h2>
        {plot && (
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="text-xs font-medium rounded-lg border border-ink-200 px-3 py-1.5 text-ink-600 hover:border-accent-300 hover:text-accent-700 transition-colors"
          >
            {downloading ? "Downloading…" : "Download PNG"}
          </button>
        )}
      </div>
      <div className="flex-1 flex items-center justify-center min-h-[380px]">
        {plot ? (
          <Plot
            data={plot.data}
            layout={{ autosize: true, margin: { t: 48, r: 24, b: 48, l: 56 }, ...plot.layout }}
            useResizeHandler
            style={{ width: "100%", height: "100%", minHeight: 380 }}
            config={{ responsive: true, displaylogo: false }}
            onInitialized={(_fig: any, gd: any) => (gdRef.current = gd)}
            onUpdate={(_fig: any, gd: any) => (gdRef.current = gd)}
          />
        ) : (
          <p className="text-sm text-ink-400 text-center px-6">
            No visualization yet — solve a problem to generate an interactive graph.
          </p>
        )}
      </div>
      {plot?.caption && (
        <p className="mt-3 text-xs text-ink-500 text-center italic">{plot.caption}</p>
      )}
    </section>
  );
}
