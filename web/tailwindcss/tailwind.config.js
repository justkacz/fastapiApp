/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/*.html",
            "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        'pacifico': ['Pacifico', 'sans-serif'],
        'lavishly': ["Corinthia", 'cursive'],
        'test': ["Lexend Peta", 'sans-serif'],
        'cormorant': ["Cormorant SC", 'serif'],
        'spartan': ["League Spartan", 'serif'],
        'dynalight': ['Playball', 'cursive'],
        'poiret': ['Poiret One', 'sans-serif'],
        'railway': ['EB Garamond', 'serif'],
        'revol2': ['Estonia', 'cursive'],
        'revol': ['Over the Rainbow', 'cursive']
      },
    },
  },
  plugins: [
    require('flowbite/plugin')
  ],
}

