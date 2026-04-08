/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        aegis: {
          bg: "#0a0a0f",
          surface: "#12121a",
          surfaceHover: "#1a1a26",
          border: "#2a2a3a",
          borderGlow: "#3b82f6",
          primary: "#3b82f6",
          primaryGlow: "rgba(59, 130, 246, 0.15)",
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          dangerGlow: "rgba(239, 68, 68, 0.15)",
          text: "#e2e8f0",
          textMuted: "#64748b",
          textDim: "#475569",
          covert: "#8b5cf6",
          covertGlow: "rgba(139, 92, 246, 0.15)",
          canary: "#f97316",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
        "scan": "scan 4s linear infinite",
      },
      keyframes: {
        glow: {
          "0%": { boxShadow: "0 0 5px rgba(59, 130, 246, 0.3)" },
          "100%": { boxShadow: "0 0 20px rgba(59, 130, 246, 0.6)" },
        },
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
    },
  },
  plugins: [],
};
