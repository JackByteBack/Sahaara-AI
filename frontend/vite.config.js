import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Sahaara AI frontend dev server.
// API base defaults to http://localhost:8010 (override with VITE_API_URL).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8010', changeOrigin: true },
      '/health': { target: 'http://localhost:8010', changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
