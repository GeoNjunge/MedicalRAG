/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  theme: {
    extend: {
      fontFamily: {
        'syne': ['Syne', 'sans-serif'],
        'mono':  ['DM Mono', 'monospace'],
        'sans':  ['DM Sans', 'sans-serif'],
      },
      colors: {
        orange:  { DEFAULT: '#e8703a', bright: '#ff8c52', dim: '#c45e2a' },
        bg:      { base: '#0e0f11', card: '#16181d', card2: '#1c1f26', card3: '#22262f' },
        border:  { DEFAULT: '#2a2e38', bright: '#3a3f4d' },
        med:     { green: '#3ecf8e', blue: '#4f9ef8', red: '#f87171', yellow: '#fbbf24' },
      },
      keyframes: {
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)'    },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        blink: {
          '0%, 80%, 100%': { opacity: '0' },
          '40%':           { opacity: '1' },
        },
        progressIndeterminate: {
          '0%':   { left: '-40%' },
          '100%': { left: '110%' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.45' },
        },
      },
      animation: {
        'slide-up':              'slideUp 0.4s ease forwards',
        'fade-in':               'fadeIn 0.3s ease forwards',
        'blink':                 'blink 1.4s ease-in-out infinite',
        'progress-indeterminate':'progressIndeterminate 1.6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
