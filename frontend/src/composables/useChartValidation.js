// composables/useChartValidation.js
import { computed } from 'vue'

export function useChartValidation(props) {
  // Проверяем есть ли данные для отображения
  const hasData = computed(() => {
    const { chartData } = props
    
    // Быстрая проверка на пустоту
    if (!chartData || typeof chartData !== 'object') return false
    
    const { labels, datasets } = chartData
    
    // Проверяем labels
    if (!Array.isArray(labels) || labels.length === 0) return false
    
    // Проверяем datasets
    if (!Array.isArray(datasets) || datasets.length === 0) return false
    
    const firstDataset = datasets[0]
    if (!firstDataset || !Array.isArray(firstDataset.data)) return false
    
    // Проверяем, что количество labels совпадает с количеством данных
    if (labels.length !== firstDataset.data.length) return false
    
    // Проверяем, что есть хотя бы одно ненулевое значение
    return firstDataset.data.some(value => value > 0)
  })
  
  // Проверяем структуру данных
  const isValidData = computed(() => {
    try {
      const { chartData } = props
      
      // Базовая проверка структуры
      if (!chartData || typeof chartData !== 'object') return false
      if (!chartData.labels || !Array.isArray(chartData.labels)) return false
      if (!chartData.datasets || !Array.isArray(chartData.datasets)) return false
      
      // Проверяем каждый dataset
      return chartData.datasets.every(dataset => {
        if (!dataset || typeof dataset !== 'object') return false
        if (!dataset.data || !Array.isArray(dataset.data)) return false
        return true
      })
    } catch (error) {
      console.error('Chart data validation error:', error)
      return false
    }
  })
  
  // Получаем общее количество элементов
  const totalItems = computed(() => {
    if (!hasData.value) return 0
    return props.chartData.labels.length
  })
  
  // Получаем максимальное значение для масштабирования
  const maxValue = computed(() => {
    if (!hasData.value) return 0
    
    const datasets = props.chartData.datasets
    const allValues = datasets.flatMap(dataset => dataset.data)
    return Math.max(...allValues)
  })
  
  return {
    hasData,
    isValidData,
    totalItems,
    maxValue
  }
}