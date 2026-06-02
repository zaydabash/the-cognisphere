/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Signature accent: warm amber/gold (lamplight / emergence).
        primary: {
          50: '#fbf7ee',
          100: '#f5ecd5',
          200: '#ead5a6',
          300: '#ddbb6e',
          400: '#d4a24a',
          500: '#c5862a',
          600: '#a96a20',
          700: '#874f1d',
          800: '#6f3f1d',
          900: '#5d351c',
          950: '#351c0d',
        },
        // Warm-neutral near-black base (not default slate).
        secondary: {
          50: '#f7f6f4',
          100: '#ecebe6',
          200: '#d8d5cd',
          300: '#b6b2a7',
          400: '#8d887c',
          500: '#6b665b',
          600: '#534f47',
          700: '#3b3833',
          800: '#272521',
          900: '#1a1815',
          950: '#100f0d',
        },
        // Secondary accent: muted teal, used sparingly for data states.
        accent: {
          50: '#eefcf9',
          100: '#d4f7ef',
          200: '#aeede2',
          300: '#79dccd',
          400: '#42c2b2',
          500: '#26a596',
          600: '#1c857a',
          700: '#1b6a63',
          800: '#1a5550',
          900: '#194743',
          950: '#082b29',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
