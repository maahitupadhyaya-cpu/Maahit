export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      <span className="font-semibold">Couldn&apos;t solve this: </span>
      {message}
    </div>
  );
}

export function WarningBanner({ warnings }: { warnings: string[] }) {
  if (!warnings.length) return null;
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 space-y-1">
      {warnings.map((w, i) => (
        <p key={i}>⚠️ {w}</p>
      ))}
    </div>
  );
}
