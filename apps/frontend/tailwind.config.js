/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#dbe6fe",
          200: "#bdd0fd",
          300: "#90b0fb",
          400: "#5c86f6",
          500: "#3660ef",
          600: "#2544e3",
          700: "#2135c7",
          800: "#212fa1",
          900: "#1f2a7f",
          950: "#161b4d",
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
