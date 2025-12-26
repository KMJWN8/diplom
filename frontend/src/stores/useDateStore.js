// stores/useDateStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDateStore = defineStore('date', () => {
  // Состояние
  const dateRange = ref({
    from: getDefaultFromDate(),
    to: getDefaultToDate()
  })
  
  // Геттеры
  const formattedDateRange = computed(() => {
    return {
      from: formatDate(dateRange.value.from),
      to: formatDate(dateRange.value.to)
    }
  })
  
  const isValidDateRange = computed(() => {
    const from = new Date(dateRange.value.from)
    const to = new Date(dateRange.value.to)
    return from <= to
  })
  
  const daysDifference = computed(() => {
    const from = new Date(dateRange.value.from)
    const to = new Date(dateRange.value.to)
    const diffTime = Math.abs(to - from)
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  })
  
  // Действия
  const updateDateRange = (from, to) => {
    dateRange.value = { from, to }
    saveToLocalStorage()
  }
  
  const resetDateRange = () => {
    dateRange.value = {
      from: getDefaultFromDate(),
      to: getDefaultToDate()
    }
    saveToLocalStorage()
  }
  
  const setLast7Days = () => {
    const to = new Date()
    const from = new Date()
    from.setDate(to.getDate() - 7)
    
    dateRange.value = {
      from: formatDateForInput(from),
      to: formatDateForInput(to)
    }
    saveToLocalStorage()
  }
  
  const setLast30Days = () => {
    const to = new Date()
    const from = new Date()
    from.setDate(to.getDate() - 30)
    
    dateRange.value = {
      from: formatDateForInput(from),
      to: formatDateForInput(to)
    }
    saveToLocalStorage()
  }
  
  const setLastYear = () => {
    const to = new Date()
    const from = new Date()
    from.setFullYear(to.getFullYear() - 1)
    
    dateRange.value = {
      from: formatDateForInput(from),
      to: formatDateForInput(to)
    }
    saveToLocalStorage()
  }
  
  // Работа с localStorage
  const saveToLocalStorage = () => {
    localStorage.setItem('dateRange', JSON.stringify(dateRange.value))
  }
  
  const loadFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('dateRange')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed.from && parsed.to) {
          dateRange.value = parsed
        }
      }
    } catch (e) {
      console.error('Error loading date range from localStorage:', e)
    }
  }
  
  // Вспомогательные функции
  function getDefaultFromDate() {
    const date = new Date()
    date.setMonth(date.getMonth() - 3) // 3 месяца назад
    return formatDateForInput(date)
  }
  
  function getDefaultToDate() {
    return formatDateForInput(new Date())
  }
  
  function formatDateForInput(date) {
    return date.toISOString().split('T')[0]
  }
  
  function formatDate(dateString) {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU')
  }
  
  // Загружаем из localStorage при инициализации
  loadFromLocalStorage()
  
  return {
    // Состояние
    dateRange,
    
    // Геттеры
    formattedDateRange,
    isValidDateRange,
    daysDifference,
    
    // Действия
    updateDateRange,
    resetDateRange,
    setLast7Days,
    setLast30Days,
    setLastYear,
    loadFromLocalStorage
  }
})