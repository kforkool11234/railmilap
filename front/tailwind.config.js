/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", 'sans-serif'],
        display: ["Outfit", 'sans-serif'],
      },
      colors: {
        brand: {
          light: '#e0f2fe',
          DEFAULT: '#38bdf8',
          dark: '#0284c7',
        },
        dark: {
          bg: '#0f172a',
          card: '#1e293b',
          border: '#334155',
        }
      }
    },
  },
  plugins: [],
}
