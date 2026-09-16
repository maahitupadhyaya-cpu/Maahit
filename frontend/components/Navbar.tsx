"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import clsx from "clsx";
import { CATEGORIES, isCategoryId, solveHref } from "@/lib/categories";

function NavbarInner() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [open, setOpen] = useState(false);
  const activeCategory = isCategoryId(searchParams.get("category"))
    ? searchParams.get("category")
    : pathname === "/solve"
      ? "calculus"
      : null;

  const close = () => setOpen(false);

  return (
    <header className="border-b border-ink-200/70 bg-white/85 backdrop-blur sticky top-0 z-40">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        <Link href="/" className="flex items-center gap-2.5 min-w-0" onClick={close}>
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent-600 text-white font-serif text-lg shadow-panel">
            ∑
          </span>
          <span className="min-w-0">
            <span className="block text-[15px] font-semibold tracking-tight text-ink-900 leading-tight">
              LaTeXify
            </span>
            <span className="hidden sm:block text-[11px] text-ink-500 leading-tight">
              Modeling &amp; Visualization
            </span>
          </span>
        </Link>

        <nav className="hidden lg:flex items-center gap-0.5 text-sm">
          <NavLink href="/" active={pathname === "/"}>
            Home
          </NavLink>
          {CATEGORIES.map((c) => (
            <NavLink
              key={c.id}
              href={solveHref(c.id)}
              active={pathname === "/solve" && activeCategory === c.id}
              title={c.label}
            >
              {c.shortLabel}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            href={solveHref("calculus")}
            className="hidden sm:inline-flex rounded-xl bg-accent-600 px-3.5 py-2 text-sm font-semibold text-white shadow-panel hover:bg-accent-700 transition-colors"
          >
            Open workspace
          </Link>
          <button
            type="button"
            className="lg:hidden inline-flex h-10 w-10 items-center justify-center rounded-lg border border-ink-200 text-ink-700 hover:bg-ink-50"
            aria-expanded={open}
            aria-label={open ? "Close menu" : "Open menu"}
            onClick={() => setOpen((v) => !v)}
          >
            <span className="sr-only">Menu</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {open ? (
                <path d="M6 6l12 12M18 6L6 18" />
              ) : (
                <>
                  <path d="M4 7h16M4 12h16M4 17h16" />
                </>
              )}
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <div className="lg:hidden border-t border-ink-100 bg-white px-4 py-3 space-y-1 shadow-panel">
          <MobileLink href="/" active={pathname === "/"} onClick={close}>
            Home
          </MobileLink>
          {CATEGORIES.map((c) => (
            <MobileLink
              key={c.id}
              href={solveHref(c.id)}
              active={pathname === "/solve" && activeCategory === c.id}
              onClick={close}
            >
              <span className="font-serif mr-2 text-accent-600">{c.icon}</span>
              {c.label}
            </MobileLink>
          ))}
          <Link
            href={solveHref("calculus")}
            onClick={close}
            className="mt-2 flex items-center justify-center rounded-xl bg-accent-600 px-3 py-2.5 text-sm font-semibold text-white"
          >
            Open workspace
          </Link>
        </div>
      )}
    </header>
  );
}

function NavLink({
  href,
  active,
  children,
  title,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
  title?: string;
}) {
  return (
    <Link
      href={href}
      title={title}
      className={clsx(
        "rounded-lg px-2 py-1.5 font-medium transition-colors whitespace-nowrap",
        active ? "bg-accent-50 text-accent-700" : "text-ink-600 hover:bg-ink-50 hover:text-ink-900"
      )}
    >
      {children}
    </Link>
  );
}

function MobileLink({
  href,
  active,
  children,
  onClick,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={clsx(
        "flex items-center rounded-lg px-3 py-2.5 text-sm font-medium",
        active ? "bg-accent-50 text-accent-700" : "text-ink-700 hover:bg-ink-50"
      )}
    >
      {children}
    </Link>
  );
}

export function Navbar() {
  return (
    <Suspense fallback={<NavbarFallback />}>
      <NavbarInner />
    </Suspense>
  );
}

function NavbarFallback() {
  return (
    <header className="border-b border-ink-200/70 bg-white/85 backdrop-blur sticky top-0 z-40">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center">
        <span className="text-[15px] font-semibold text-ink-900">LaTeXify</span>
      </div>
    </header>
  );
}
