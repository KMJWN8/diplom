// stores/useSummarizationStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

export const useSummarizationStore = defineStore('summarization', () => {
  // Константы
  const MAX_TEXT_LENGTH = 4100
  const MIN_TEXT_LENGTH = 50
  
  // Состояние
  const summary = ref('')
  const loading = ref(false)
  const isExporting = ref(false)
  const error = ref(null)
  
  // Геттеры
  const hasSummary = computed(() => !!summary.value)
  const summaryLength = computed(() => summary.value.length)
  
  // Действия
  const generateSummary = async (selectedPosts) => {
    // Проверяем наличие постов
    if (!selectedPosts || selectedPosts.length === 0) {
      error.value = 'Нет выбранных постов для аннотации'
      return { success: false, error: error.value }
    }
    
    // Объединяем тексты постов
    const combinedText = selectedPosts
      .map(post => post.message || '')
      .filter(text => text.trim())
      .join('\n\n')
    
    // Проверяем лимиты
    if (combinedText.length > MAX_TEXT_LENGTH) {
      error.value = `Текст превышает лимит ${MAX_TEXT_LENGTH} символов. Уменьшите количество постов.`
      return { success: false, error: error.value }
    }
    
    if (combinedText.length < MIN_TEXT_LENGTH) {
      error.value = `Текст слишком короткий (${combinedText.length} символов). Минимум ${MIN_TEXT_LENGTH} символов.`
      return { success: false, error: error.value }
    }
    
    loading.value = true
    error.value = null
    summary.value = ''
    
    try {
      const response = await apiClient.post('/summarization/summarize', {
        summary: combinedText
      }, {
        timeout: 60000
      })
      
      summary.value = response.data.summary || ''
      return { success: true, summary: summary.value }
      
    } catch (err) {
      console.error('Summarization error:', err)
      
      if (err.message.includes('timeout')) {
        error.value = 'Таймаут запроса. Текст слишком длинный или сервер занят.'
      } else if (err.message.includes('Network Error')) {
        error.value = 'Ошибка сети. Проверьте соединение с сервером.'
      } else if (err.response?.data?.message) {
        error.value = err.response.data.message
      } else if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = err.message || 'Не удалось аннотировать текст'
      }
      
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const clearSummary = () => {
    summary.value = ''
    error.value = null
  }
  
  const clearError = () => {
    error.value = null
  }
  
  // Экспорт в Word (клиентский)
  const exportToWord = async (selectedPosts, summaryText = null) => {
    if (!selectedPosts || selectedPosts.length === 0) {
      error.value = 'Нет постов для экспорта'
      return false
    }
    
    isExporting.value = true
    error.value = null
    
    try {
      // Создаем HTML документ
      let htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body { 
              font-family: 'Times New Roman'; 
              margin: 0.3cm 0.5cm 0.5cm 0.5cm; 
              font-size: 14pt; 
              line-height: 1.5;
              text-align: justify;
              text-justify: inter-word;
              text-align-last: justify;
              word-spacing: normal;
              letter-spacing: normal;
              hyphens: auto;
            }
            h1 { 
              text-align: center; 
              font-size: 14pt;
              margin-bottom: 10px;
            }
          </style>
        </head>
        <body>
      `
      
      // Добавляем суммаризацию если есть
      if (summaryText || summary.value) {
        htmlContent += `
            <h1>5. Проблемы в субъекте РФ</h1>
            ${summaryText || summary.value}
        `
      }
      
      // Создаем Blob и скачиваем
      const blob = new Blob([htmlContent], { 
        type: 'application/msword' 
      })
      
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      const dateStr = new Date().toISOString().slice(0, 10)
      const fileName = `telegram_posts_${dateStr}.doc`
      
      link.setAttribute('download', fileName)
      document.body.appendChild(link)
      link.click()
      
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
      
    } catch (err) {
      console.error('Export error:', err)
      error.value = 'Ошибка при создании Word документа: ' + err.message
      return false
    } finally {
      isExporting.value = false
    }
  }
  
  // Вспомогательные функции
  const formatDate = (dateString) => {
    if (!dateString) return 'Неизвестно'
    
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }
  
  const truncateText = (text, maxLength) => {
    if (!text || text.length <= maxLength) return text || ''
    return text.substring(0, maxLength) + '...'
  }
  
  return {
    // Состояние
    summary,
    loading,
    isExporting,
    error,
    
    // Константы
    MAX_TEXT_LENGTH,
    MIN_TEXT_LENGTH,
    
    // Геттеры
    hasSummary,
    summaryLength,
    
    // Действия
    generateSummary,
    clearSummary,
    clearError,
    exportToWord,
    
    // Вспомогательные
    formatDate,
    truncateText
  }
})