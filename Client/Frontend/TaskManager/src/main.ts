import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { initPerformanceMonitoring } from './utils/performance'
import { registerServiceWorker } from './utils/serviceWorker'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

// Initialize performance monitoring
initPerformanceMonitoring()

// Register service worker for offline support and caching
registerServiceWorker({
  onSuccess: () => {
    console.log('Service worker registered successfully')
  },
  onUpdate: () => {
    console.log('New content available, please refresh')
  },
  onOfflineReady: () => {
    console.log('App ready for offline use')
  }
})
