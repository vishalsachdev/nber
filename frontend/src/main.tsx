import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Enable Vercel Analytics in production builds
if (import.meta.env.PROD) {
  // Dynamically import to avoid overhead in dev
  import('@vercel/analytics').then(({ inject }) => {
    try {
      inject();
    } catch (_) {
      // no-op if analytics fails to load
    }
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
