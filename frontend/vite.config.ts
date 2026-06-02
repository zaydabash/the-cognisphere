import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "/the-cognisphere/", // Project site path for GitHub Pages
  server: {
    host: true,
    port: 5173,
    // Allow Cloudflare quick-tunnel hosts (and any host) so the dev server can
    // be exposed publicly for a shareable demo.
    allowedHosts: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@headlessui/react'],
          visualization: ['cytoscape'],
        },
      },
    },
  },
  define: {
    // Ensure environment variables are available at build time
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
})
