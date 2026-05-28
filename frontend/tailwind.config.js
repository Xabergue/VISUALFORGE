/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      colors: {
        forge: {
          bg: '#0a0a0a', surface: '#111111', card: '#1a1a1a', border: '#2a2a2a',
          muted: '#888888', text: '#f5f5f5', purple: '#7c3aed', 'purple-light': '#8b5cf6',
          'purple-dark': '#6d28d9', blue: '#2563eb', 'blue-light': '#3b82f6',
        }
      },
    },
  },
  plugins: [],
}
