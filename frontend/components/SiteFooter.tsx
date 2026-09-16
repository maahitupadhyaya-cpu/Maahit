import Link from "next/link";
import { CATEGORIES, solveHref } from "@/lib/categories";

export function SiteFooter() {
  return (
    <footer className="border-t border-ink-200/70 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-6">
        <div>
          <p className="text-sm font-semibold text-ink-900">LaTeXify</p>
          <p className="mt-1 text-xs text-ink-500 max-w-sm">
            Enter a problem, then solve, explain, LaTeXify, visualize, and export.
          </p>
        </div>
        <nav className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-ink-500">
          <Link href="/" className="hover:text-accent-700">
            Home
          </Link>
          {CATEGORIES.map((c) => (
            <Link key={c.id} href={solveHref(c.id)} className="hover:text-accent-700">
              {c.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
