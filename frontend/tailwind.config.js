/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vf: {
          bg: '#0a0a0a',
          card: '#111111',
          'card-hover': '#1a1a1a',
          purple: '#7c3aed',
          'purple-light': '#8b5cf6',
          blue: '#2563eb',
          text: '#f5f5f5',
          'text-secondary': '#888888',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
