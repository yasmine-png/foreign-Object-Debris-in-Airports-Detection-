/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#faf8f5',
          100: '#f5f1eb',
          200: '#e8ddd0',
          300: '#d4c4b0',
          400: '#b8a082',
          500: '#9d8166',
          600: '#8b6f57',
          700: '#735a47',
          800: '#5f4a3c',
          900: '#4f3f33',
        },
        nude: {
          50: '#faf7f4',
          100: '#f5ede6',
          200: '#e8d5c4',
          300: '#d4b89d',
          400: '#b8956e',
          500: '#9d7a52',
          600: '#8b6a47',
          700: '#73563c',
          800: '#5f4632',
          900: '#4f3a2a',
        },
        beige: {
          50: '#fefdfb',
          100: '#fdf9f3',
          200: '#faf0e1',
          300: '#f5e2c8',
          400: '#edcca5',
          500: '#d4a574',
          600: '#b88a5a',
          700: '#9a7149',
          800: '#7d5a3d',
          900: '#684a33',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}

