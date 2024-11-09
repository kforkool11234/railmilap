/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        custom: ["Jersey 25", 'sans-serif'], // replace with your font name and fallbacks
      },
    },
  },
  plugins: [],
}

