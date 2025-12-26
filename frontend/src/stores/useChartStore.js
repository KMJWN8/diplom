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
  
  const chartType = ref('topics') // 'topics' или 'dates'
  const selectedTopic = ref('')
  const selectedDate = ref('')
  
  // Простое кэширование для предотвращения повторных запросов
  const lastLoadedDateRange = ref({ from: '', to: '' })
  
  // Геттеры
  const currentChartData = computed(() => {
    return chartType.value === 'topics' ? topicsChartData.value : datesChartData.value
  })
  
  const hasSelection = computed(() => !!selectedTopic.value || !!selectedDate.value)
  
  // Действия
  const setChartType = async (type, dateRange) => {
    if (['topics', 'dates'].includes(type) && chartType.value !== type) {
      chartType.value = type
      // Загружаем данные при переключении типа
      await loadChartData(dateRange)
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
  const loadChartData = async (dateRange) => {
    try {
      if (chartType.value === 'topics') {
        const response = await postsApi.getPostsCountByTopic(
          dateRange.from, 
          dateRange.to
        )
        
        const data = response.data
        if (data.topics && data.counts) {
          updateChartData('topics', data.topics, data.counts)
          lastLoadedDateRange.value = { ...dateRange }
        }
        return { success: true, data: response.data }
      } else {
        const response = await postsApi.getPostsByDate(
          dateRange.from, 
          dateRange.to
        )
        
        const data = response.data
        if (data.dates && data.counts) {
          updateChartData('dates', data.dates, data.counts)
          lastLoadedDateRange.value = { ...dateRange }
        }
        return { success: true, data: response.data }
      }
    } catch (error) {
      console.error('Chart data fetch error:', error)
      return { success: false, error }
    }
  }
  
  // Проверяет, нужно ли загружать данные (если изменился диапазон дат)
  const shouldLoadData = (dateRange) => {
    const last = lastLoadedDateRange.value
    return !last.from || !last.to || 
           last.from !== dateRange.from || 
           last.to !== dateRange.to
  }
  
  // Вспомогательные функции
  const updateChartData = (type, labels, counts) => {
    const isTopics = type === 'topics'
    const selectedValue = isTopics ? selectedTopic.value : selectedDate.value
    
    const chartData = {
      labels,
      datasets: [{
        label: 'Количество постов',
        data: counts,
        backgroundColor: labels.map(label => 
          label === selectedValue ? 'rgba(255, 99, 132, 0.8)' : 
          (isTopics ? 'rgba(75, 192, 192, 0.5)' : 'rgba(54, 162, 235, 0.5)')
        ),
        borderColor: labels.map(label => 
          label === selectedValue ? 'rgba(255, 99, 132, 1)' : 
          (isTopics ? 'rgba(75, 192, 192, 1)' : 'rgba(54, 162, 235, 1)')
        ),
        borderWidth: labels.map(label => label === selectedValue ? 3 : 1),
        borderRadius: 5,
      }]
    }
    
    if (isTopics) {
      topicsChartData.value = chartData
    } else {
      datesChartData.value = chartData
    }
  }
  
  const updateChartColors = () => {
    if (chartType.value === 'topics') {
      const { labels, datasets } = topicsChartData.value
      if (labels.length > 0) {
        updateChartData('topics', labels, datasets[0].data)
      }
    } else {
      const { labels, datasets } = datesChartData.value
      if (labels.length > 0) {
        updateChartData('dates', labels, datasets[0].data)
      }
    }
  }
  
  return {
    // Состояние
    topicsChartData,
    datesChartData,
    chartType,
    selectedTopic,
    selectedDate,
    
    // Геттеры
    currentChartData,
    hasSelection,
    
    // Действия
    setChartType,
    setSelection,
    resetSelection,
    loadChartData,
    shouldLoadData,
    updateChartColors
  }
})