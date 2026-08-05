export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#0A1324',
          950: '#04070E',
          900: '#070C18',
          850: '#0A1324',
          800: '#0E1A30',
          750: '#132340',
          700: '#1A2E52',
        },
        gold: {
          100: '#FBF3D6',
          200: '#F3E4AE',
          300: '#E9D287',
          400: '#DBBB5E',
          500: '#C8A24A',
          600: '#A67E33',
          700: '#7E5F26',
        },
        azure: {
          100: '#D6E8FB',
          200: '#AECFF3',
          300: '#7FB2E8',
          400: '#4A90D9',
          500: '#2E6FBF',
          600: '#22548F',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      letterSpacing: { luxe: '0.22em' },
      backgroundImage: {
        'gold-sheen': 'linear-gradient(135deg, #FBF3D6 0%, #E9D287 35%, #DBBB5E 55%, #A67E33 100%)',
      },
      boxShadow: {
        glass: 'inset 0 1px 0 0 rgba(255,255,255,0.06), 0 24px 50px -28px rgba(0,0,0,0.75)',
        'gold-glow': '0 0 0 1px rgba(219,187,94,0.30), 0 10px 34px -10px rgba(219,187,94,0.40)',
        'azure-glow': '0 0 0 1px rgba(74,144,217,0.30), 0 10px 34px -10px rgba(74,144,217,0.35)',
        panel: '0 30px 60px -30px rgba(0,0,0,0.85)',
      },
      keyframes: {
        'float-glow': {
          '0%,100%': { opacity: '0.45', transform: 'translateY(0)' },
          '50%': { opacity: '0.75', transform: 'translateY(-10px)' },
        },
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'float-glow': 'float-glow 9s ease-in-out infinite',
        'fade-up': 'fade-up 0.5s ease-out both',
      },
    },
  },
  plugins: [],
};
