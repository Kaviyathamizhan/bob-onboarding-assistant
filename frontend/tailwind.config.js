/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bob: {
          bg: '#161616',
          surface: '#262626',
          primary: '#0043CE',
          accent: '#24A148',
          warning: '#F1C21B',
          text: '#F4F4F4',
          muted: '#8D8D8D',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        card: '4px',
        input: '2px',
      },
    },
  },
  plugins: [],
}
