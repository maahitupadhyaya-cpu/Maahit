import type { Metadata } from "next";
import { Inter, Source_Serif_4 } from "next/font/google";
import "katex/dist/katex.min.css";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { SiteFooter } from "@/components/SiteFooter";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "LaTeXify — Mathematical Modeling & Visualization Platform",
  description:
    "Solve differential equations, calculus, statistics, optimization, linear algebra and probability problems with step-by-step derivations, LaTeX output and interactive graphs.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${sourceSerif.variable}`}>
      <body className="min-h-screen font-sans antialiased flex flex-col">
        <Navbar />
        <div className="flex-1">{children}</div>
        <SiteFooter />
      </body>
    </html>
  );
}
