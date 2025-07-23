import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 3000,
    maxHeaderSize: 5 * 1024 * 1024, // 增加请求头大小限制到2MB
    proxy: {
      '/db': 'http://localhost:8000',
      '/api': 'http://localhost:8000'
    }
  }
})
