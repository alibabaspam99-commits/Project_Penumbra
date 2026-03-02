import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Type definitions for PWA
interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent
  }
}

// Register PWA Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then(
      (registration) => {
        console.log('[PWA] Service Worker registered:', registration)
      },
      (error) => {
        console.error('[PWA] Service Worker registration failed:', error)
      }
    )
  })
}

// Handle PWA installation prompt
let deferredPrompt: BeforeInstallPromptEvent | null = null

window.addEventListener('beforeinstallprompt', (e: BeforeInstallPromptEvent) => {
  e.preventDefault()
  deferredPrompt = e
  console.log('[PWA] Install prompt ready')
})

// Make deferredPrompt available globally for UI to use
;(window as any).deferredPrompt = deferredPrompt

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
