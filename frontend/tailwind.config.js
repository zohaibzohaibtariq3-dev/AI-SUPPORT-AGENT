/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0F111A",
          900: "#151826",
          800: "#1E2233",
          700: "#2A2F45",
          600: "#3C4262",
        },
        paper: {
          50: "#FAFAF8",
          100: "#F3F2EE",
          200: "#E8E6DF",
        },
        signal: {
          DEFAULT: "#4C5FD5",
          light: "#EEF0FC",
          dark: "#3946A8",
        },
        amber: {
          DEFAULT: "#C77D2E",
          light: "#FBF1E4",
        },
        moss: {
          DEFAULT: "#3E7A5B",
          light: "#EAF3EE",
        },
      },
      fontFamily: {
        display: ["Manrope", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15, 17, 26, 0.04), 0 8px 24px rgba(15, 17, 26, 0.06)",
      },
    },
  },
  plugins: [],
};
