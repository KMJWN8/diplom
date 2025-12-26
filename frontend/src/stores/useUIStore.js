// stores/useUIStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // Состояние
  const isSidebarOpen = ref(true)
  const theme = ref('light')
  const language = ref('ru')
  const notifications = ref([])
  const loadingStates = ref({})
  
  // Геттеры
  const isLoading = computed(() => {
    return Object.values(loadingStates.value).some(state => state === true)
  })
  
  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.read).length
  })
  
  const currentTheme = computed(() => {
    return theme.value === 'dark' ? 'dark-theme' : 'light-theme'
  })
  
  // Действия
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
    saveToLocalStorage()
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme.value)
    saveToLocalStorage()
  }
  
  const setLanguage = (lang) => {
    if (['ru', 'en'].includes(lang)) {
      language.value = lang
      saveToLocalStorage()
    }
  }
  
  const setLoading = (key, isLoading) => {
    loadingStates.value[key] = isLoading
  }
  
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now(),
      message: notification.message,
      type: notification.type || 'info',
      read: false,
      timestamp: new Date().toISOString()
    }
    
    notifications.value.unshift(newNotification)
    
    // Ограничиваем количество уведомлений
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }
    
    saveToLocalStorage()
  }
  
  const markNotificationAsRead = (id) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
      saveToLocalStorage()
    }
  }
  
  const clearNotifications = () => {
    notifications.value = []
    saveToLocalStorage()
  }
  
  // Работа с localStorage
  const saveToLocalStorage = () => {
    const uiState = {
      isSidebarOpen: isSidebarOpen.value,
      theme: theme.value,
      language: language.value,
      notifications: notifications.value
    }
    
    localStorage.setItem('uiState', JSON.stringify(uiState))
  }
  
  const loadFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('uiState')
      if (saved) {
        const parsed = JSON.parse(saved)
        
        if (parsed.isSidebarOpen !== undefined) {
          isSidebarOpen.value = parsed.isSidebarOpen
        }
        
        if (parsed.theme) {
          theme.value = parsed.theme
          document.documentElement.setAttribute('data-theme', parsed.theme)
        }
        
        if (parsed.language) {
          language.value = parsed.language
        }
        
        if (parsed.notifications) {
          notifications.value = parsed.notifications
        }
      }
    } catch (e) {
      console.error('Error loading UI state from localStorage:', e)
    }
  }
  
  // Инициализация
  const initialize = () => {
    // Проверяем предпочтения системы
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark && !localStorage.getItem('uiState')) {
      theme.value = 'dark'
      document.documentElement.setAttribute('data-theme', 'dark')
    }
    
    loadFromLocalStorage()
  }
  
  // Вызываем инициализацию
  initialize()
  
  return {
    // Состояние
    isSidebarOpen,
    theme,
    language,
    notifications,
    loadingStates,
    
    // Геттеры
    isLoading,
    unreadNotifications,
    currentTheme,
    
    // Действия
    toggleSidebar,
    toggleTheme,
    setLanguage,
    setLoading,
    addNotification,
    markNotificationAsRead,
    clearNotifications,
    initialize
  }
})