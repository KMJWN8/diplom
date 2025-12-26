// stores/usePostsStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { postsApi } from '@/api/endpoints'

export const usePostsStore = defineStore('posts', () => {
  // Состояние
  const posts = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Геттеры
  const hasPosts = computed(() => posts.value.length > 0)
  const postsCount = computed(() => posts.value.length)
  const selectedPostsCount = computed(() => 
    posts.value.filter(post => post.isSelected).length
  )
  
  // Действия
  const clearPosts = () => {
    posts.value = []
    error.value = null
  }
  
  const getPostsByDate = async (date) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await postsApi.getPostsBySpecificDate(date)
      posts.value = response.data || []
      
      // Восстанавливаем выбор если есть в кэше
      restoreSelections()
      
      return { success: true, data: response.data }
    } catch (err) {
      console.error('Posts fetch error:', err)
      error.value = err.response?.data?.message || 'Не удалось загрузить посты'
      posts.value = []
      return { success: false, error: err }
    } finally {
      loading.value = false
    }
  }
  
  const getPostsByTopic = async (topic, dateRange) => {
    loading.value = true
    error.value = null
    
    try {
      if (!postsApi.getPostsByTopic) {
        throw new Error('API для постов по теме не реализован')
      }
      
      const response = await postsApi.getPostsByTopic(
        topic,
        dateRange.from,
        dateRange.to
      )
      posts.value = response.data || []
      
      // Восстанавливаем выбор если есть в кэше
      restoreSelections()
      
      return { success: true, data: response.data }
    } catch (err) {
      console.error('Posts by topic fetch error:', err)
      error.value = err.response?.data?.message || 'Не удалось загрузить посты по теме'
      posts.value = []
      return { success: false, error: err }
    } finally {
      loading.value = false
    }
  }
  
  // Работа с выбранными постами
  const togglePostSelection = (post) => {
    const index = posts.value.findIndex(p => p.id === post.id)
    
    if (index > -1) {
      posts.value[index].isSelected = !posts.value[index].isSelected
      saveSelections()
    }
  }
  
  const clearSelections = () => {
    posts.value.forEach(post => {
      post.isSelected = false
    })
    localStorage.removeItem('selectedPosts')
  }
  
  const getSelectedPosts = computed(() => {
    return posts.value.filter(post => post.isSelected)
  })
  
  // Сохранение выбора в localStorage
  const saveSelections = () => {
    const selectedIds = posts.value
      .filter(post => post.isSelected)
      .map(post => post.id)
    
    localStorage.setItem('selectedPosts', JSON.stringify(selectedIds))
  }
  
  const restoreSelections = () => {
    try {
      const saved = localStorage.getItem('selectedPosts')
      if (saved) {
        const selectedIds = JSON.parse(saved)
        
        posts.value.forEach(post => {
          post.isSelected = selectedIds.includes(post.id)
        })
      }
    } catch (e) {
      console.error('Error restoring selections:', e)
    }
  }
  
  // Вспомогательная функция для форматирования темы
  const formatTopicToHashtag = (topic) => {
    if (!topic) return ''
    
    // Если topic это массив
    if (Array.isArray(topic)) {
      return topic.map(t => `#${formatSingleTopic(t)}`).join(', ')
    }
    
    // Если topic это строка с массивом
    if (topic.startsWith('[') && topic.endsWith(']')) {
      try {
        const topicsArray = JSON.parse(topic)
        if (Array.isArray(topicsArray)) {
          return topicsArray.map(t => `#${formatSingleTopic(t)}`).join(', ')
        }
      } catch (e) {
        // Если не удалось распарсить, обрабатываем как строку
      }
    }
    
    // Если это обычная строка
    return `#${formatSingleTopic(topic)}`
  }
  
  const formatSingleTopic = (topic) => {
    const translations = {
      "environment": "Экология",
      "manufacture": "Производство", 
      "employment": "Занятость",
      "financesandcredit": "Финансы и кредит",
      "homeandinfrastructure": "Дом и инфраструктура",
      "healthservice": "Здравоохранение",
      "educationandsport": "Образование и спорт",
      "socialsphere": "Социальная сфера",
      "politics": "Политика",
      "criminality": "Криминалистика",
      "demographic": "Демография",
      "unclassified": "Не классифицировано"
    }
    
    let cleanTopic = String(topic).replace(/["']/g, '')
    
    if (translations[cleanTopic]) {
      return translations[cleanTopic]
    }
    
    return cleanTopic
      .replace(/([A-Z])/g, ' $1')
      .replace(/_/g, ' ')
      .replace(/and/g, ' & ')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }
  
  return {
    // Состояние
    posts,
    loading,
    error,
    
    // Геттеры
    hasPosts,
    postsCount,
    selectedPostsCount,
    getSelectedPosts,
    
    // Действия
    clearPosts,
    getPostsByDate,
    getPostsByTopic,
    togglePostSelection,
    clearSelections,
    
    // Вспомогательные
    formatTopicToHashtag,
    saveSelections,
    restoreSelections
  }
})