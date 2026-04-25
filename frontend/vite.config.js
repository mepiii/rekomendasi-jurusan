// Purpose: Configure Vite React dev/build behavior for frontend app.
// Callers: npm run dev, npm run build.
// Deps: vite, @vitejs/plugin-react.
// API: Exports Vite config object.
// Side effects: Enables React plugin and default port behavior.
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    exclude: ['node_modules/**', 'dist/**', 'tests/e2e/**']
  }
});