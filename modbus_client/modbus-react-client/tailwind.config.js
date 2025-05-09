/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        digital: ['"Digital7"', 'sans-serif'], // or '', etc
      },
    }
  
  },
  plugins: [],
}

