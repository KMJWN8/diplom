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
      error.value = 'Нет выбранных постов для суммаризации'
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
        error.value = err.message || 'Не удалось суммаризировать текст'
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
          <title>Telegram посты</title>
          <style>
            body { 
              font-family: 'Times New Roman', Times, serif; 
              margin: 2cm; 
              font-size: 12pt; 
              line-height: 1.5;
            }
            h1 { 
              text-align: center; 
              font-size: 16pt;
              margin-bottom: 20px;
            }
            .post { 
              margin: 25px 0; 
              page-break-inside: avoid;
            }
            .post-header { 
              margin-bottom: 10px;
              border-bottom: 1px solid #cccccc;
              padding-bottom: 5px;
            }
            .post-meta { 
              font-size: 11pt; 
              color: #666666;
              margin-bottom: 8px;
            }
            .post-text { 
              margin: 10px 0; 
              line-height: 1.6;
              text-align: justify;
            }
            .divider { 
              border-top: 1px solid #cccccc; 
              margin: 20px 0;
            }
            .summary { 
              margin: 20px 0;
              font-style: italic;
            }
          </style>
        </head>
        <body>
          <h1>TELEGRAM ПОСТЫ</h1>
      `
      
      // Добавляем суммаризацию если есть
      if (summaryText || summary.value) {
        htmlContent += `
          <div class="summary">
            <strong>Суммаризация:</strong><br>
            ${summaryText || summary.value}
          </div>
        `
      }
      
      // Добавляем посты
      selectedPosts.forEach((post, index) => {
        const postText = post.message || ''
        
        htmlContent += `
          <div class="post">
            <div class="post-header">
              <div class="post-meta">
                <strong>Пост ${index + 1}</strong> | 
                Канал: ${post.channel_name || 'Неизвестно'} | 
                Дата: ${formatDate(post.date)} | 
                Тема: #${post.topic || 'Без темы'}
              </div>
            </div>
        `
        
        if (postText) {
          const paragraphs = postText.split('\n').filter(p => p.trim())
          if (paragraphs.length > 0) {
            paragraphs.forEach(paragraph => {
              htmlContent += `<div class="post-text">${paragraph}</div>`
            })
          } else {
            htmlContent += `<div class="post-text">${postText}</div>`
          }
        } else {
          htmlContent += '<div class="post-text"><em>Текст поста отсутствует</em></div>'
        }
        
        htmlContent += '</div>'
        
        if (index < selectedPosts.length - 1) {
          htmlContent += '<div class="divider"></div>'
        }
      })
      
      // Футер
      htmlContent += `
          <div style="margin-top: 40px; text-align: right; font-size: 10pt; color: #888888;">
            Сформировано: ${new Date().toLocaleDateString('ru-RU')}
          </div>
        </body>
        </html>
      `
      
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