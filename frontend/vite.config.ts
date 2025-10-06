import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/chat': {
        target: 'https://uiuc.chat',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => {
          const newPath = path.replace(/^\/api\/chat/, '/api/chat-api/chat');
          console.log(`Proxying ${path} -> ${newPath}`);
          return newPath;
        },
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log('Proxy request:', req.method, req.url, '-> https://uiuc.chat' + proxyReq.path);
          });
        }
      }
    }
  }
})
