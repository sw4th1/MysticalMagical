import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    target: 'esnext', // This enables top-level await
    rollupOptions: {
      output: {
        format: 'es'
      }
    }
  }
})