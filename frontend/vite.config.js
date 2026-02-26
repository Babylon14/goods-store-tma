import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'precerebroid-unpromotional-stefanie.ngrok-free.dev', // Твоя ссылка из ngrok
      '.ngrok-free.dev' // Или можно разрешить все поддомены ngrok сразу
    ],
    host: true, // Это чтобы Docker мог пробрасывать порт
    port: 5173
  }
})

