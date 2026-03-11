/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',  // 绿色护眼主色
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        dark: {
          50: '#4a4a4a',
          100: '#3a3a3a',
          200: '#2a2a2a',
          300: '#1e1e1e',
          400: '#1a1a1a',
          500: '#141414',
        }
      },
    },
  },
  plugins: [],
}
