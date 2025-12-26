// stores/useChartStore.js - полное исправление
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { postsApi } from '@/api/endpoints'

const TOPIC_TRANSLATIONS = {
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

// Создаем обратный словарь для перевода с русского на английский
const REVERSE_TRANSLATIONS = Object.entries(TOPIC_TRANSLATIONS).reduce((acc, [eng, rus]) => {
  acc[rus] = eng
  return acc
}, {})

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
  const selectedTopic = ref('') // Храним АНГЛИЙСКОЕ название
  const selectedDate = ref('')
  
  // Простое кэширование для предотвращения повторных запросов
  const lastLoadedDateRange = ref({ from: '', to: '' })
  
  // Добавляем ref для оригинальных тем
  const originalTopics = ref([])
  
  // Геттеры
  const currentChartData = computed(() => {
    return chartType.value === 'topics' ? topicsChartData.value : datesChartData.value
  })
  
  const hasSelection = computed(() => !!selectedTopic.value || !!selectedDate.value)
  
  // Функция перевода с английского на русский
  const translateTopic = (topic) => {
    return TOPIC_TRANSLATIONS[topic] || topic
  }
  
  // Функция обратного перевода с русского на английский
  const reverseTranslateTopic = (russianTopic) => {
    return REVERSE_TRANSLATIONS[russianTopic] || russianTopic
  }
  
  // Получение английского названия темы (для API)
  const getOriginalTopicName = (russianTopic) => {
    // Сначала ищем в сохраненных оригинальных темах
    const originalTopic = originalTopics.value.find(
      topic => translateTopic(topic) === russianTopic
    )
    
    if (originalTopic) return originalTopic
    
    // Если не нашли, используем обратный перевод
    return reverseTranslateTopic(russianTopic)
  }
  
  const setChartType = async (type, dateRange) => {
    if (['topics', 'dates'].includes(type) && chartType.value !== type) {
      chartType.value = type
      // Загружаем данные при переключении типа
      await loadChartData(dateRange)
    }
  }
  
  // Исправляем setSelection - сохраняем только английские названия
  const setSelection = (type, translatedValue) => {
    if (type === 'topic') {
      // Всегда сохраняем английское название
      const englishTopic = getOriginalTopicName(translatedValue)
      console.log('setSelection - русская:', translatedValue, 'английская:', englishTopic)
      
      selectedTopic.value = englishTopic
      selectedDate.value = ''
      updateChartColors()
    } else if (type === 'date') {
      selectedDate.value = translatedValue
      selectedTopic.value = ''
      updateChartColors()
    }
  }

  // Геттер для получения переведенной выбранной темы (для UI)
  const translatedSelectedTopic = computed(() => {
    return selectedTopic.value ? translateTopic(selectedTopic.value) : ''
  })
  
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
    
    // Сохраняем оригинальные темы
    if (isTopics) {
      originalTopics.value = labels
    }

    // Переводим labels для отображения
    const translatedLabels = isTopics ? labels.map(topic => translateTopic(topic)) : labels
    
    // Для сравнения используем selectedTopic.value (который всегда на английском)
    const selectedValue = isTopics ? selectedTopic.value : selectedDate.value
    
    const chartData = {
      labels: translatedLabels,
      datasets: [{
        label: 'Количество постов',
        data: counts,
        // labels - это английские названия, сравниваем с selectedTopic.value (английское)
        backgroundColor: labels.map((originalLabel, index) => {
          return originalLabel === selectedValue ? 'rgba(255, 99, 132, 0.8)' : 
                 (isTopics ? 'rgba(75, 192, 192, 0.5)' : 'rgba(54, 162, 235, 0.5)')
        }),
        borderColor: labels.map((originalLabel, index) => {
          return originalLabel === selectedValue ? 'rgba(255, 99, 132, 1)' : 
                 (isTopics ? 'rgba(75, 192, 192, 1)' : 'rgba(54, 162, 235, 1)')
        }),
        borderWidth: labels.map(originalLabel => {
          return originalLabel === selectedValue ? 3 : 1
        }),
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
        // Здесь проблема! Нужно передать оригинальные темы, не переведенные
        // Но originalTopics уже должны быть сохранены
        if (originalTopics.value.length > 0) {
          updateChartData('topics', originalTopics.value, datasets[0].data)
        }
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
    selectedTopic, // ВСЕГДА английское!
    selectedDate,
    
    // Геттеры
    currentChartData,
    hasSelection,
    translatedSelectedTopic, // Для UI - русская версия
    
    // Действия
    setChartType,
    setSelection,
    resetSelection,
    loadChartData,
    shouldLoadData,
    updateChartColors,

    // Функции перевода
    translateTopic,
    reverseTranslateTopic,
    getOriginalTopicName,
    
    // Для отладки
    originalTopics
  }
})