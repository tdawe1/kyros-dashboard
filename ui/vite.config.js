import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    // Expose environment variables to the frontend
    'import.meta.env.VITE_API_MODE': JSON.stringify(process.env.VITE_API_MODE || 'demo'),
    'import.meta.env.VITE_DEFAULT_MODEL': JSON.stringify(process.env.VITE_DEFAULT_MODEL || 'gpt-4o-mini'),
  }
})
