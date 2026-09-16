"use client";

import { BlockMath, InlineMath } from "react-katex";

function renderError(latex: string | null | undefined) {
  return () => (
    <code className="text-sm text-red-500 break-all">{latex ?? ""}</code>
  );
}

export function MathBlock({ latex, className }: { latex?: string | null; className?: string }) {
  if (!latex) return null;
  return (
    <div className={className}>
      <BlockMath
        math={latex}
        errorColor="#dc2626"
        renderError={renderError(latex) as any}
      />
    </div>
  );
}

export function MathInline({ latex }: { latex: string }) {
  return <InlineMath math={latex} errorColor="#dc2626" renderError={renderError(latex) as any} />;
}
