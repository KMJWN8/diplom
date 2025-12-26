// stores/useChartStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { postsApi } from '@/api/endpoints'

export const useChartStore = defineStore('chart', () => {
  // Состояние
  const topicsChartData = ref({
    labels: [],
    datasets: [{
      label: 'Количество постов',
      data: [],
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1,
      borderRadius: 5,
    }]
  })
  
  const datesChartData = ref({
    labels: [],
    datasets: [{
      label: 'Количество постов',
      data: [],
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1,
      borderRadius: 5,
    }]
  })
  
  const chartLoading = ref(false)
  const chartType = ref('topics') // 'topics' или 'dates'
  const selectedTopic = ref('')
  const selectedDate = ref('')
  
  // Геттеры
  const currentChartData = computed(() => 
    chartType.value === 'topics' ? topicsChartData.value : datesChartData.value
  )
  
  const hasChartData = computed(() => {
    const data = currentChartData.value
    return data.labels.length > 0 && data.datasets[0].data.length > 0
  })
  
  const hasSelection = computed(() => !!selectedTopic.value || !!selectedDate.value)
  
  // Действия
  const setChartType = (type) => {
    if (['topics', 'dates'].includes(type)) {
      chartType.value = type
    }
  }
  
  const setSelection = (type, value) => {
    if (type === 'date') {
      selectedDate.value = value
      selectedTopic.value = ''
      updateChartColors()
    } else if (type === 'topic') {
      selectedTopic.value = value
      selectedDate.value = ''
      updateChartColors()
    }
  }
  
  const resetSelection = () => {
    selectedTopic.value = ''
    selectedDate.value = ''
    updateChartColors()
  }
  
  // Загрузка данных
  const loadTopicsChartData = async (dateRange) => {
    chartLoading.value = true
    
    try {
      const response = await postsApi.getPostsCountByTopic(
        dateRange.from, 
        dateRange.to
      )
      
      const data = response.data
      
      if (data.topics && data.counts) {
        topicsChartData.value = updateTopicsChartColors(
          data.topics, 
          data.counts,
          selectedTopic.value
        )
      }
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Topics chart data fetch error:', error)
      return { success: false, error }
    } finally {
      chartLoading.value = false
    }
  }
  
  const loadDatesChartData = async (dateRange) => {
    chartLoading.value = true
    
    try {
      const response = await postsApi.getPostsByDate(
        dateRange.from, 
        dateRange.to
      )
      
      const data = response.data
      
      if (data.dates && data.counts) {
        datesChartData.value = updateDatesChartColors(
          data.dates, 
          data.counts,
          selectedDate.value
        )
      }
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Dates chart data fetch error:', error)
      return { success: false, error }
    } finally {
      chartLoading.value = false
    }
  }
  
  // Обновление цветов
  const updateChartColors = () => {
    if (chartType.value === 'topics') {
      const { labels, datasets } = topicsChartData.value
      if (labels.length > 0) {
        topicsChartData.value = updateTopicsChartColors(
          labels,
          datasets[0].data,
          selectedTopic.value
        )
      }
    } else {
      const { labels, datasets } = datesChartData.value
      if (labels.length > 0) {
        datesChartData.value = updateDatesChartColors(
          labels,
          datasets[0].data,
          selectedDate.value
        )
      }
    }
  }
  
  // Вспомогательные функции
  const updateTopicsChartColors = (topics, counts, selectedTopic) => {
    return {
      labels: topics,
      datasets: [{
        label: 'Количество постов',
        data: counts,
        backgroundColor: topics.map(topic => 
          topic === selectedTopic ? 'rgba(255, 99, 132, 0.8)' : 'rgba(54, 162, 235, 0.5)'
        ),
        borderColor: topics.map(topic => 
          topic === selectedTopic ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'
        ),
        borderWidth: topics.map(topic => 
          topic === selectedTopic ? 3 : 1
        ),
        borderRadius: 5,
      }]
    }
  }
  
  const updateDatesChartColors = (dates, counts, selectedDate) => {
    return {
      labels: dates,
      datasets: [{
        label: 'Количество постов',
        data: counts,
        backgroundColor: dates.map(date => 
          date === selectedDate ? 'rgba(255, 99, 132, 0.8)' : 'rgba(54, 162, 235, 0.5)'
        ),
        borderColor: dates.map(date => 
          date === selectedDate ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'
        ),
        borderWidth: dates.map(date => 
          date === selectedDate ? 3 : 1
        ),
        borderRadius: 5,
      }]
    }
  }
  
  const loadChartData = async (dateRange) => {
    if (chartType.value === 'topics') {
      return await loadTopicsChartData(dateRange)
    } else {
      return await loadDatesChartData(dateRange)
    }
  }
  
  return {
    // Состояние
    topicsChartData,
    datesChartData,
    chartLoading,
    chartType,
    selectedTopic,
    selectedDate,
    
    // Геттеры
    currentChartData,
    hasChartData,
    hasSelection,
    
    // Действия
    setChartType,
    setSelection,
    resetSelection,
    loadTopicsChartData,
    loadDatesChartData,
    loadChartData,
    updateChartColors
  }
})