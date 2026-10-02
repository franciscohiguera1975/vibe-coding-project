/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eefcfc",
          100: "#d4f5f6",
          200: "#aeeaed",
          300: "#78d9df",
          400: "#3cbdc7",
          500: "#1aa3af",
          600: "#11838d",
          700: "#126872",
          800: "#15555d",
          900: "#16474e",
          950: "#082a30",
        },
        navy: {
          50: "#eef1f8",
          100: "#dbe1ee",
          200: "#b7c0d9",
          300: "#8d98bd",
          400: "#5f6b97",
          500: "#414c74",
          600: "#2f3759",
          700: "#242a44",
          800: "#1a1f33",
          900: "#121526",
          950: "#0a0c16",
        },
        ink: {
          50: "#f6f7f9",
          100: "#eceef2",
          200: "#d5d9e2",
          300: "#b1b9c9",
          400: "#8691ab",
          500: "#67728f",
          600: "#525b77",
          700: "#434a61",
          800: "#3a3f52",
          900: "#333747",
          950: "#15161d",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
