// Purpose: Define Tailwind scan paths and project design tokens.
// Callers: Tailwind compiler during dev/build.
// Deps: tailwindcss.
// API: Exports Tailwind configuration with theme extensions.
// Side effects: Adds Linear-inspired color palette and typography defaults.
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#08090a',
        panel: '#191a1b',
        input: '#0f1011',
        cta: '#5e6ad2',
        accent: '#7170ff',
        textPrimary: '#f7f8f8',
        textSecondary: '#d0d6e0',
        textMuted: '#8a8f98',
        textSubtle: '#62666d',
        success: '#27a644'
      },
      borderColor: {
        subtle: 'rgba(255,255,255,0.05)',
        standard: 'rgba(255,255,255,0.08)'
      },
      boxShadow: {
        subtle: '0 8px 30px rgba(0,0,0,0.22)',
        insetPanel: 'inset 0 0 18px rgba(0,0,0,0.28)'
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
};