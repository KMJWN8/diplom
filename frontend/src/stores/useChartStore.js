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
  
  // Кэш для загруженных данных (чтобы не грузить повторно)
  const dataCache = ref({
    topics: { data: null, lastLoaded: null },
    dates: { data: null, lastLoaded: null }
  })
  
  // Геттеры
  const currentChartData = computed(() => {
    if (chartType.value === 'topics') {
      return topicsChartData.value
    } else {
      return datesChartData.value
    }
  })
  
  const hasChartData = computed(() => {
    const data = currentChartData.value
    return data.labels.length > 0 && data.datasets[0].data.length > 0
  })
  
  const hasSelection = computed(() => !!selectedTopic.value || !!selectedDate.value)
  
  // Проверяем нужно ли обновлять данные
  const shouldReloadData = (type, dateRange) => {
    const cacheKey = `${type}_${dateRange.from}_${dateRange.to}`
    const cachedData = dataCache.value[type]
    
    if (!cachedData.data || !cachedData.lastLoaded) {
      return true
    }
    
    // Проверяем не устарели ли данные (больше 5 минут)
    const now = new Date().getTime()
    const lastLoadedTime = new Date(cachedData.lastLoaded).getTime()
    const fiveMinutes = 5 * 60 * 1000
    
    return (now - lastLoadedTime) > fiveMinutes
  }
  
  // Действия
  const setChartType = async (type, dateRange) => {
    if (['topics', 'dates'].includes(type)) {
      chartType.value = type
      
      // Загружаем данные если их еще нет в кэше
      if (shouldReloadData(type, dateRange)) {
        await loadChartData(dateRange)
      }
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
  
  // Загрузка данных с кэшированием
  const loadTopicsChartData = async (dateRange, forceRefresh = false) => {
    const cacheKey = `topics_${dateRange.from}_${dateRange.to}`
    
    // Проверяем кэш если не принудительное обновление
    if (!forceRefresh && dataCache.value.topics.data && 
        dataCache.value.topics.lastLoaded && 
        !shouldReloadData('topics', dateRange)) {
      topicsChartData.value = updateTopicsChartColors(
        dataCache.value.topics.data.topics,
        dataCache.value.topics.data.counts,
        selectedTopic.value
      )
      return { success: true, data: dataCache.value.topics.data, cached: true }
    }
    
    chartLoading.value = true
    
    try {
      const response = await postsApi.getPostsCountByTopic(
        dateRange.from, 
        dateRange.to
      )
      
      const data = response.data
      
      if (data.topics && data.counts) {
        // Сохраняем в кэш
        dataCache.value.topics = {
          data: { topics: data.topics, counts: data.counts },
          lastLoaded: new Date().toISOString()
        }
        
        topicsChartData.value = updateTopicsChartColors(
          data.topics, 
          data.counts,
          selectedTopic.value
        )
      }
      return { success: true, data: response.data, cached: false }
    } catch (error) {
      console.error('Topics chart data fetch error:', error)
      return { success: false, error }
    } finally {
      chartLoading.value = false
    }
  }
  
  const loadDatesChartData = async (dateRange, forceRefresh = false) => {
    const cacheKey = `dates_${dateRange.from}_${dateRange.to}`
    
    // Проверяем кэш
    if (!forceRefresh && dataCache.value.dates.data && 
        dataCache.value.dates.lastLoaded && 
        !shouldReloadData('dates', dateRange)) {
      datesChartData.value = updateDatesChartColors(
        dataCache.value.dates.data.dates,
        dataCache.value.dates.data.counts,
        selectedDate.value
      )
      return { success: true, data: dataCache.value.dates.data, cached: true }
    }
    
    chartLoading.value = true
    
    try {
      const response = await postsApi.getPostsByDate(
        dateRange.from, 
        dateRange.to
      )
      
      const data = response.data
      
      if (data.dates && data.counts) {
        // Сохраняем в кэш
        dataCache.value.dates = {
          data: { dates: data.dates, counts: data.counts },
          lastLoaded: new Date().toISOString()
        }
        
        datesChartData.value = updateDatesChartColors(
          data.dates, 
          data.counts,
          selectedDate.value
        )
      }
      return { success: true, data: response.data, cached: false }
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
  
  // Загрузка данных в зависимости от текущего типа
  const loadChartData = async (dateRange, forceRefresh = false) => {
    if (chartType.value === 'topics') {
      return await loadTopicsChartData(dateRange, forceRefresh)
    } else {
      return await loadDatesChartData(dateRange, forceRefresh)
    }
  }
  
  // Очистка кэша
  const clearCache = () => {
    dataCache.value = {
      topics: { data: null, lastLoaded: null },
      dates: { data: null, lastLoaded: null }
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
  
  return {
    // Состояние
    topicsChartData,
    datesChartData,
    chartLoading,
    chartType,
    selectedTopic,
    selectedDate,
    dataCache,
    
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
    updateChartColors,
    clearCache,
    shouldReloadData
  }
})