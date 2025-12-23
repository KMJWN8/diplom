import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'

export function usePostSelection() {
  const toast = useToast()
  const selectedPosts = ref([])
  
  const selectionStats = computed(() => {
    const channels = new Set(selectedPosts.value.map(p => p.channel_name))
    const topics = new Set(selectedPosts.value.map(p => p.topic))
    const dates = selectedPosts.value.map(p => new Date(p.date))
    
    const minDate = dates.length ? new Date(Math.min(...dates)) : null
    const maxDate = dates.length ? new Date(Math.max(...dates)) : null
    
    return {
      total: selectedPosts.value.length,
      channels: channels.size,
      topics: topics.size,
      dateRange: minDate && maxDate 
        ? `${minDate.toLocaleDateString()} - ${maxDate.toLocaleDateString()}`
        : '-'
    }
  })
  
  const togglePostSelection = (post) => {
    const index = selectedPosts.value.findIndex(p => p.id === post.id)
    
    if (index > -1) {
      selectedPosts.value.splice(index, 1)
      toast.add({
        severity: 'info',
        summary: 'Пост удален',
        detail: 'Пост удален из выборки',
        life: 2000
      })
    } else {
      selectedPosts.value.push(post)
      toast.add({
        severity: 'success',
        summary: 'Пост добавлен',
        detail: 'Пост добавлен в отчет',
        life: 2000
      })
    }
  }
  
  const clearSelection = () => {
    selectedPosts.value = []
    toast.add({
      severity: 'warn',
      summary: 'Выборка очищена',
      detail: 'Все посты удалены из выборки',
      life: 3000
    })
  }
  
  return {
    selectedPosts,
    selectionStats,
    togglePostSelection,
    clearSelection
  }
}