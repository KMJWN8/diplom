// stores/usePostsStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { postsApi } from '@/api/endpoints'

export const usePostsStore = defineStore('posts', () => {
  // Состояние
  const posts = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Уникальный идентификатор для предотвращения дублирования
  const postIdsSet = ref(new Set())
  
  // Геттеры
  const hasPosts = computed(() => posts.value.length > 0)
  const postsCount = computed(() => posts.value.length)
  
  const selectedPostsCount = computed(() => 
    posts.value.filter(post => post.isSelected).length
  )
  
  const getSelectedPosts = computed(() => {
    return posts.value.filter(post => post.isSelected)
  })
  
  const getSelectedPostIds = computed(() => {
    return posts.value
      .filter(post => post.isSelected)
      .map(post => post.id)
  })
  
  // Действия
  const clearPosts = () => {
    posts.value = []
    postIdsSet.value.clear()
    error.value = null
  }
  
  // Проверка на дублирование
  const isDuplicate = (post) => {
    return postIdsSet.value.has(post.id)
  }
  
  // Добавление поста без дублирования
  const addPost = (post) => {
    if (!post || !post.id) return false
    
    if (!isDuplicate(post)) {
      // Добавляем уникальный идентификатор
      if (!post.uniqueId) {
        post.uniqueId = `${post.id}_${Date.now()}`
      }
      
      postIdsSet.value.add(post.id)
      posts.value.push({
        ...post,
        isSelected: post.isSelected || false
      })
      return true
    }
    return false
  }
  
  // Добавление массива постов
  const addPosts = (newPosts) => {
    let addedCount = 0
    const uniquePosts = []
    
    newPosts.forEach(post => {
      if (!isDuplicate(post)) {
        if (!post.uniqueId) {
          post.uniqueId = `${post.id}_${Date.now()}`
        }
        
        postIdsSet.value.add(post.id)
        uniquePosts.push({
          ...post,
          isSelected: post.isSelected || false
        })
        addedCount++
      }
    })
    
    posts.value.push(...uniquePosts)
    return addedCount
  }
  
  // Загрузка постов по дате
  const getPostsByDate = async (date) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await postsApi.getPostsBySpecificDate(date)
      const data = response.data || []
      
      // Очищаем текущие посты
      clearPosts()
      
      // Добавляем новые посты
      const added = addPosts(data)
      console.log(`Добавлено ${added} уникальных постов за дату ${date}`)
      
      // Восстанавливаем выбор
      restoreSelections()
      
      return { success: true, data: data, added: added }
    } catch (err) {
      console.error('Posts fetch error:', err)
      error.value = err.response?.data?.message || 'Не удалось загрузить посты'
      return { success: false, error: err }
    } finally {
      loading.value = false
    }
  }
  
  // Загрузка постов по теме
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
      
      const data = response.data || []
      
      // Очищаем текущие посты
      clearPosts()
      
      // Добавляем новые посты
      const added = addPosts(data)
      console.log(`Добавлено ${added} уникальных постов по теме "${topic}"`)
      
      // Восстанавливаем выбор
      restoreSelections()
      
      return { success: true, data: data, added: added }
    } catch (err) {
      console.error('Posts by topic fetch error:', err)
      error.value = err.response?.data?.message || 'Не удалось загрузить посты по теме'
      return { success: false, error: err }
    } finally {
      loading.value = false
    }
  }
  
  // Работа с выбранными постами
  const togglePostSelection = (post) => {
    const index = posts.value.findIndex(p => p.uniqueId === post.uniqueId || p.id === post.id)
    
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
  
  // Сохранение выбора в localStorage
  const saveSelections = () => {
    const selectedIds = posts.value
      .filter(post => post.isSelected)
      .map(post => post.uniqueId || post.id)
    
    localStorage.setItem('selectedPosts', JSON.stringify(selectedIds))
  }
  
  const restoreSelections = () => {
    try {
      const saved = localStorage.getItem('selectedPosts')
      if (saved) {
        const selectedIds = JSON.parse(saved)
        
        posts.value.forEach(post => {
          // Проверяем по uniqueId или id
          post.isSelected = selectedIds.includes(post.uniqueId) || 
                           selectedIds.includes(post.id)
        })
      }
    } catch (e) {
      console.error('Error restoring selections:', e)
    }
  }
  
  // Удаление дубликатов
  const removeDuplicates = () => {
    const seen = new Set()
    const uniquePosts = []
    
    posts.value.forEach(post => {
      const key = post.uniqueId || post.id
      if (!seen.has(key)) {
        seen.add(key)
        uniquePosts.push(post)
      }
    })
    
    posts.value = uniquePosts
    postIdsSet.value = new Set(posts.value.map(p => p.id))
    
    // Пересохраняем выбор
    saveSelections()
    
    return posts.value.length
  }
  
  // Получение поста по ID
  const getPostById = (postId) => {
    return posts.value.find(p => p.id === postId || p.uniqueId === postId)
  }
  
  // Вспомогательные функции
  const formatTopicToHashtag = (topic) => {
    if (!topic) return ''
    
    if (Array.isArray(topic)) {
      return topic.map(t => `#${formatSingleTopic(t)}`).join(', ')
    }
    
    if (topic.startsWith('[') && topic.endsWith(']')) {
      try {
        const topicsArray = JSON.parse(topic)
        if (Array.isArray(topicsArray)) {
          return topicsArray.map(t => `#${formatSingleTopic(t)}`).join(', ')
        }
      } catch (e) {
        // Если не удалось распарсить
      }
    }
    
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
  
  // Методы для работы с отчетами (заглушки)
  const generateReport = async (selectedPosts) => {
    console.log('Генерация отчета для постов:', selectedPosts)
    // Здесь будет логика генерации отчета
  }
  
  const shareSelection = (selectedPosts) => {
    console.log('Поделиться выборкой:', selectedPosts)
    // Здесь будет логика шеринга
  }
  
  return {
    // Состояние
    posts,
    loading,
    error,
    postIdsSet,
    
    // Геттеры
    hasPosts,
    postsCount,
    selectedPostsCount,
    getSelectedPosts,
    getSelectedPostIds,
    
    // Действия
    clearPosts,
    getPostsByDate,
    getPostsByTopic,
    togglePostSelection,
    clearSelections,
    saveSelections,
    restoreSelections,
    addPost,
    addPosts,
    removeDuplicates,
    getPostById,
    
    // Вспомогательные
    formatTopicToHashtag,
    
    // Методы отчетов
    generateReport,
    shareSelection
  }
})