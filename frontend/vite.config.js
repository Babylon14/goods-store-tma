import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Позволяет слушать все сетевые интерфейсы внутри Docker
    port: 5173,
    strictPort: true, // Гарантирует, что Vite всегда будет на 5173
    allowedHosts: [
      'frontend',
      '.zrok.io',   // Разрешает все поддомены zrok
      'localhost',  // Разрешает локальный доступ
      '.loca.lt',    // Можно оставить на всякий случай
      '.pinggy.link',
    ]
  }
})


