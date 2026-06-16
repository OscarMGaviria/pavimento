/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary:   '#0F172A', // Slate 900
        secondary: '#4F46E5', // Indigo 600
        accent:    '#F59E0B', // Amber 500
        surface:   '#F8FAFC', // Slate 50
        panel:     '#FFFFFF',
      },
      fontFamily: {
        sans: ['Fira Sans', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
