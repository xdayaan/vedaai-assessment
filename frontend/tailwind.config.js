/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          orange: '#FF5623',
          'orange-light': '#FF934F',
          'orange-dark': '#C03409',
          'orange-subtle': '#FFF6E5',
          'orange-glow': '#FF8C35',
          dark: '#171717',
          'dark-card': '#262626',
          'dark-border': '#2F2F2F',
          'dark-surface': '#2A2A2A',
          charcoal: '#2F2F2F',
          'gray-text': '#5D5D5D',
          'gray-light': '#F6F6F6',
          'gray-border': '#CDCDCD',
          'gray-muted': '#A9A9A9',
          green: '#33AC15',
          'green-light': '#45B529',
          'green-bg': '#EAF8E6',
          'green-highlight': '#5DFF35',
        },
      },
      fontFamily: {
        bricolage: ['var(--font-bricolage)', 'Bricolage Grotesque', 'sans-serif'],
        sans: ['var(--font-bricolage)', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0px 4px 20px rgba(0, 0, 0, 0.05)',
        'card-hover': '0px 10px 30px rgba(0, 0, 0, 0.1)',
        'glow-orange': '0 0 40px rgba(255, 86, 35, 0.25)',
        'glow-green': '0 0 30px rgba(93, 255, 53, 0.3)',
      },
    },
  },
  plugins: [],
};
