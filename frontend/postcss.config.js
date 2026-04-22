// Purpose: Wire Tailwind and Autoprefixer into PostCSS pipeline.
// Callers: Vite CSS processing.
// Deps: tailwindcss, autoprefixer.
// API: Exports PostCSS plugin configuration.
// Side effects: Transforms Tailwind directives into compiled CSS.
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};