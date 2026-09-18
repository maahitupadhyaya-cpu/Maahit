type Glyph = {
  glyph: string;
  left: string;
  top: string;
  size: string;
  delay: string;
  duration: string;
  kind: "float" | "drift" | "spin";
};

const HOME_GLYPHS: Glyph[] = [
  { glyph: "∑", left: "2%", top: "10%", size: "3.2rem", delay: "0s", duration: "11s", kind: "float" },
  { glyph: "∫", left: "91%", top: "8%", size: "3.6rem", delay: "1.1s", duration: "13s", kind: "drift" },
  { glyph: "π", left: "92%", top: "74%", size: "2.5rem", delay: "0.4s", duration: "10s", kind: "float" },
  { glyph: "∞", left: "3%", top: "80%", size: "2.7rem", delay: "1.8s", duration: "12s", kind: "drift" },
  { glyph: "∂", left: "88%", top: "40%", size: "2.1rem", delay: "0.7s", duration: "9s", kind: "spin" },
  { glyph: "λ", left: "78%", top: "84%", size: "2.3rem", delay: "2.2s", duration: "14s", kind: "float" },
  { glyph: "√", left: "4%", top: "44%", size: "2.2rem", delay: "1.4s", duration: "10s", kind: "drift" },
  { glyph: "θ", left: "94%", top: "56%", size: "2rem", delay: "0.9s", duration: "11s", kind: "float" },
  { glyph: "∆", left: "1%", top: "60%", size: "2.1rem", delay: "2.6s", duration: "12s", kind: "drift" },
  { glyph: "∇", left: "82%", top: "4%", size: "2rem", delay: "1.6s", duration: "13s", kind: "spin" },
];

const ABOUT_GLYPHS: Glyph[] = [
  { glyph: "∑", left: "2%", top: "8%", size: "3.4rem", delay: "0s", duration: "12s", kind: "float" },
  { glyph: "∫", left: "90%", top: "9%", size: "3.8rem", delay: "0.8s", duration: "14s", kind: "drift" },
  { glyph: "π", left: "91%", top: "70%", size: "2.6rem", delay: "1.4s", duration: "11s", kind: "float" },
  { glyph: "∞", left: "3%", top: "76%", size: "2.8rem", delay: "2s", duration: "13s", kind: "drift" },
  { glyph: "∂", left: "87%", top: "38%", size: "2.2rem", delay: "0.5s", duration: "10s", kind: "spin" },
  { glyph: "λ", left: "76%", top: "84%", size: "2.3rem", delay: "1.7s", duration: "12s", kind: "float" },
  { glyph: "√", left: "4%", top: "42%", size: "2.3rem", delay: "1.1s", duration: "9s", kind: "drift" },
  { glyph: "θ", left: "94%", top: "52%", size: "2.1rem", delay: "2.4s", duration: "11s", kind: "float" },
  { glyph: "∆", left: "1%", top: "54%", size: "2.2rem", delay: "0.6s", duration: "12s", kind: "drift" },
  { glyph: "∇", left: "80%", top: "5%", size: "2.1rem", delay: "1.9s", duration: "13s", kind: "spin" },
  { glyph: "Ω", left: "84%", top: "86%", size: "2.3rem", delay: "2.8s", duration: "14s", kind: "drift" },
  { glyph: "φ", left: "8%", top: "16%", size: "2rem", delay: "1.3s", duration: "11s", kind: "float" },
];

export function MathSymbolsField({
  variant = "home",
}: {
  variant?: "home" | "about";
}) {
  const glyphs = variant === "about" ? ABOUT_GLYPHS : HOME_GLYPHS;
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden z-[1] hidden sm:block" aria-hidden="true">
      {glyphs.map((g, i) => (
        <span
          key={`${g.glyph}-${i}`}
          className={`math-symbol math-symbol-${g.kind} font-serif leading-none select-none`}
          style={{
            left: g.left,
            top: g.top,
            fontSize: g.size,
            animationDelay: g.delay,
            animationDuration: g.duration,
          }}
        >
          {g.glyph}
        </span>
      ))}
    </div>
  );
}
