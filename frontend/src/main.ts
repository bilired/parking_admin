import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'mapbox-gl/dist/mapbox-gl.css'
import '@mapbox/mapbox-gl-directions/dist/mapbox-gl-directions.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus, { size: 'default', zIndex: 3000 })

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Initialize auth state before mounting
const authStore = useAuthStore()
authStore.init().finally(() => {
  app.mount('#app')
})
