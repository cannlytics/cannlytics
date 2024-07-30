/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./website/templates/**/*.{html,js}"],
  darkMode: 'class', // or 'media' or false
  theme: {
    extend: {},
  },
  plugins: [],
  variants: {
    extend: {
      transform: ['responsive', 'hover', 'focus'],
      transitionProperty: ['responsive', 'motion-safe', 'motion-reduce'],
    },
  },
}

