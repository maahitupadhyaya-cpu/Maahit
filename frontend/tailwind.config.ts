import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f5f6fa",
          100: "#e9ebf3",
          200: "#cfd4e4",
          300: "#a9b1cc",
          400: "#7c87ac",
          500: "#5c6690",
          600: "#454e73",
          700: "#333a58",
          800: "#22283f",
          900: "#161a2b",
        },
        accent: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
      },
      fontFamily: {
        serif: ["var(--font-serif)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15, 23, 42, 0.06), 0 8px 24px -8px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
