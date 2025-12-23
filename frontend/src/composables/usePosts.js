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

  return {
    posts,
    loading,
    clearPosts,
    getPostsByDate,
    getPostsByTopic
  }
}