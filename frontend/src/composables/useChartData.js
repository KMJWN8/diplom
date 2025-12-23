// composables/useChartData.js
import { ref } from 'vue'
import { postsApi } from '@/api/endpoints'

export function useChartData() {
  // Диаграмма по темам
  const topicsChartData = ref({
    labels: [],
    datasets: [
      {
        label: 'Количество постов',
        data: [],
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        borderRadius: 5,
      }
    ]
  })

  // Диаграмма по датам
  const datesChartData = ref({
    labels: [],
    datasets: [
      {
        label: 'Количество постов',
        data: [],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        borderRadius: 5,
      }
    ]
  })

  const chartLoading = ref(false)

  const updateTopicsChartColors = (topics, counts, selectedTopic) => {
    return {
      labels: topics,
      datasets: [
        {
          label: 'Количество постов',
          data: counts,
          backgroundColor: topics.map((topic, index) => 
            topic === selectedTopic ? 'rgba(255, 99, 132, 0.8)' : 'rgba(54, 162, 235, 0.5)'
          ),
          borderColor: topics.map((topic, index) => 
            topic === selectedTopic ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'
          ),
          borderWidth: topics.map(topic => 
            topic === selectedTopic ? 3 : 1
          ),
          borderRadius: 5,
        }
      ]
    }
  }

  const updateDatesChartColors = (dates, counts, selectedDate) => {
    return {
      labels: dates,
      datasets: [
        {
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
        }
      ]
    }
  }

  // Загрузка данных для диаграммы по темам
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
          '' // начальное значение без выделения
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

  // Загрузка данных для диаграммы по датам
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
          '' // начальное значение без выделения
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

  // Обновление цветов для активной диаграммы
  const updateChartColors = (chartType, selectedValue) => {
    if (chartType === 'topics') {
      const { labels, datasets } = topicsChartData.value
      if (labels.length > 0) {
        topicsChartData.value = updateTopicsChartColors(
          labels,
          datasets[0].data,
          selectedValue.topic || ''
        )
      }
    } else {
      const { labels, datasets } = datesChartData.value
      if (labels.length > 0) {
        datesChartData.value = updateDatesChartColors(
          labels,
          datasets[0].data,
          selectedValue.date || ''
        )
      }
    }
  }

  return {
    topicsChartData,
    datesChartData,
    chartLoading,
    loadTopicsChartData,
    loadDatesChartData,
    updateChartColors,
    updateTopicsChartColors,
    updateDatesChartColors
  }
}