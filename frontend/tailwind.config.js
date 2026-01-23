/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Black base
        black: {
          DEFAULT: '#000000',
          light: '#0a0a0a',
        },
        // Structural purple (main purple - dark, desaturated)
        purple: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
          950: '#3b0764',
          // Custom structural purple
          structural: '#4a3f5f',
          'structural-light': '#5a4f6f',
          'structural-dark': '#3a2f4f',
        },
        // Ambient purple (glow, atmosphere)
        ambient: {
          purple: 'rgba(138, 85, 247, 0.15)',
          'purple-light': 'rgba(168, 85, 247, 0.1)',
          'purple-glow': 'rgba(147, 51, 234, 0.2)',
        },
        // Text colors
        text: {
          primary: '#ffffff',
          secondary: '#b8b3c4', // Gray with purple bias
          tertiary: '#8a8595',
          muted: '#6a6575',
        },
        // Glass colors
        glass: {
          DEFAULT: 'rgba(74, 63, 95, 0.1)',
          light: 'rgba(90, 79, 111, 0.08)',
          dark: 'rgba(58, 47, 79, 0.15)',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'ambient-glow': 'radial-gradient(circle at center, rgba(138, 85, 247, 0.15) 0%, transparent 70%)',
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        DEFAULT: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '40px',
        '3xl': '64px',
      },
      borderColor: {
        DEFAULT: 'rgba(74, 63, 95, 0.3)',
        light: 'rgba(90, 79, 111, 0.2)',
        dark: 'rgba(58, 47, 79, 0.4)',
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(138, 85, 247, 0.1)',
        'glow': '0 0 20px rgba(138, 85, 247, 0.15)',
        'glow-lg': '0 0 40px rgba(138, 85, 247, 0.2)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'inner-glow': 'inset 0 0 20px rgba(138, 85, 247, 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
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
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(138, 85, 247, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(138, 85, 247, 0.25)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      transitionDuration: {
        '0': '0ms',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '250': '250ms',
      },
    },
  },
  plugins: [],
};
