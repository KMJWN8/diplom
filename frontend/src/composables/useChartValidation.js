// composables/useChartValidation.js
import { computed } from 'vue'

export function useChartValidation(props) {
  const hasData = computed(() => {
    const { chartData } = props
    
    if (!chartData || typeof chartData !== 'object') return false
    
    const { labels, datasets } = chartData
    
    if (!Array.isArray(labels) || labels.length === 0) return false
    if (!Array.isArray(datasets) || datasets.length === 0) return false
    
    const firstDataset = datasets[0]
    if (!firstDataset || !Array.isArray(firstDataset.data)) return false
    
    if (labels.length !== firstDataset.data.length) return false
    
    return firstDataset.data.some(value => value > 0)
  })
  
  return { hasData }
}