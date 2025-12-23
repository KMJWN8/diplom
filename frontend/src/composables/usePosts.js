// composables/usePosts.js
import { ref } from 'vue'
import { postsApi } from '@/api/endpoints'

export function usePosts() {
  const posts = ref([])
  const loading = ref(false)

  const clearPosts = () => {
    posts.value = []
  }

  const getPostsByDate = async (date) => {
    loading.value = true
    try {
      const response = await postsApi.getPostsBySpecificDate(date)
      posts.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Posts fetch error:', error)
      posts.value = []
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }

  const getPostsByTopic = async (topic, dateRange) => {
    loading.value = true
    try {
      // Проверяем наличие метода API
      if (!postsApi.getPostsByTopic) {
        console.warn('API для постов по теме не реализован')
        posts.value = []
        return { success: false, error: 'API not implemented' }
      }

      const response = await postsApi.getPostsByTopic(
        topic,
        dateRange.from,
        dateRange.to
      )
      posts.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Posts by topic fetch error:', error)
      posts.value = []
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }

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

    
    // Удаляем кавычки
    let cleanTopic = String(topic).replace(/["']/g, '')
    
    // Пытаемся найти перевод
    if (translations[cleanTopic]) {
      return translations[cleanTopic]
    }
    
    // Или форматируем автоматически
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
    posts,
    loading,
    clearPosts,
    getPostsByDate,
    getPostsByTopic,
    formatTopicToHashtag
  }
}