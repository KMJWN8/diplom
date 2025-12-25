<template>
  <div v-if="selectedPosts.length > 0" class="selected-posts-panel">
    <!-- Заголовок панели -->
    <div class="panel-header">
      <div class="header-left">
        <i class="pi pi-folder-open" />
        <h3>Выбранные посты для суммаризации ({{ selectedPosts.length }})</h3>
      </div>
      <div class="header-right">
        <Button 
          @click="exportToWord"
          :disabled="selectedPosts.length === 0 || isExporting"
          :loading="isExporting"
          icon="pi pi-file-word"
          severity="help"
          outlined
          size="small"
          label="Выгрузить в Word"
          class="header-action-btn"
          :title="'Экспортировать ' + selectedPosts.length + ' постов в Word'"
        />
        <Button 
          @click="$emit('clear-selection')"
          icon="pi pi-trash"
          severity="danger"
          outlined
          size="small"
          label="Очистить выбор"
          class="header-action-btn"
        />
      </div>
    </div>

    <!-- Контент панели -->
    <div class="panel-content">
      
      <!-- Кнопка суммаризации -->
      <div class="summarization-controls">
        <div class="summarization-info">
          <span class="info-text">
            Выбрано постов: {{ selectedPosts.length }} 
            ({{ combinedTextLength }} / {{ MAX_TEXT_LENGTH }} символов)
          </span>
          <span v-if="isTextTooLong" class="error-text">
            <i class="pi pi-exclamation-triangle"></i>
            Текст превышает лимит на {{ combinedTextLength - MAX_TEXT_LENGTH }} символов
          </span>
          <span v-else-if="isTextTooShort" class="warning-text">
            <i class="pi pi-info-circle"></i>
            Текст слишком короткий для суммаризации (минимум 50 символов)
          </span>
          <span v-else class="success-text">
            <i class="pi pi-check-circle"></i>
            Текст подходит для суммаризации
          </span>
        </div>
        
        <div class="summarization-actions">
          <Button 
            @click="generateSummary"
            :loading="loading"
            :disabled="loading || selectedPosts.length === 0 || isTextTooLong || isTextTooShort || isExporting"
            icon="pi pi-compress"
            :label="buttonLabel"
            severity="primary"
            :title="buttonTooltip"
          />
        </div>
      </div>

      <!-- Превью суммаризации -->
      <div v-if="summary" class="summary-preview">
        <h4>Результат суммаризации ({{ summary.length }} символов):</h4>
        <div class="summary-text">
          {{ summary }}
        </div>
      </div>
      
      <!-- Сообщение об ошибке -->
      <div v-if="error" class="error-message">
        <i class="pi pi-exclamation-triangle"></i>
        {{ error }}
      </div>

      <!-- Информация о лимитах -->
      <div class="limits-info">
        <p><strong>Ограничения суммаризации:</strong></p>
        <ul>
          <li>Максимальная длина текста: {{ MAX_TEXT_LENGTH }} символов</li>
          <li>Минимальная длина текста: {{ MIN_TEXT_LENGTH }} символов</li>
          <li>Текущая длина: {{ combinedTextLength }} символов</li>
        </ul>
      </div>

      <!-- Список выбранных постов -->
      <div class="selected-posts-list">
        <div v-for="post in selectedPosts" :key="post.id" class="selected-post-item">
          <div class="post-item-header">
            <div class="post-info">
              <span class="channel-badge">{{ post.channel_name }}</span>
              <span class="post-id">#{{ post.post_id }}</span>
              <span class="post-length">
                {{ (post.message || '').length }} симв.
              </span>
            </div>
            <div class="post-actions">
              <Button 
                @click="$emit('remove-post', post.id)"
                icon="pi pi-times"
                severity="danger"
                text
                size="small"
                :title="'Удалить из выборки'"
              />
            </div>
          </div>
          
          <div class="post-date">
            {{ formatDate(post.date) }}
          </div>
          
          <div class="post-preview">
            {{ truncateText(post.message, 120) }}
          </div>
          
          <div class="post-meta">
            <span class="meta-item">
              <i class="pi pi-eye" /> {{ post.views }}
            </span>
            <span class="meta-item">
              <i class="pi pi-comments" /> {{ post.comments_count }}
            </span>
            <span class="topic-tag">{{ formatTopicToHashtag(post.topic) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Диалог загрузки -->
    <div v-if="loading || isExporting" class="loading-overlay">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>{{ isExporting ? 'Экспорт в Word...' : 'Суммаризация текста...' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Button from 'primevue/button'
import { usePosts } from '@/composables/usePosts'
import apiClient from '@/api/client'

const props = defineProps({
  selectedPosts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'remove-post',
  'clear-selection'
])

const { formatTopicToHashtag } = usePosts()

// Константы для ограничений
const MAX_TEXT_LENGTH = 4100
const MIN_TEXT_LENGTH = 50

// Состояния для суммаризации
const summary = ref('')
const loading = ref(false)
const isExporting = ref(false)
const error = ref(null)

// Вычисляемые свойства
const combinedTextLength = computed(() => {
  return props.selectedPosts
    .map(post => post.message || '')
    .filter(text => text.trim())
    .join('\n\n')
    .length
})

const isTextTooLong = computed(() => {
  return combinedTextLength.value > MAX_TEXT_LENGTH
})

const isTextTooShort = computed(() => {
  return combinedTextLength.value < MIN_TEXT_LENGTH
})

const buttonLabel = computed(() => {
  if (isExporting.value) return 'Экспорт в Word...'
  if (loading.value) return 'Суммаризация...'
  if (isTextTooLong.value) return 'Текст слишком длинный'
  if (isTextTooShort.value) return 'Текст слишком короткий'
  return 'Суммаризировать выбранные посты'
})

const buttonTooltip = computed(() => {
  if (isTextTooLong.value) {
    return `Уменьшите количество выбранных постов. Максимум ${MAX_TEXT_LENGTH} символов`
  }
  if (isTextTooShort.value) {
    return `Добавьте больше постов. Минимум ${MIN_TEXT_LENGTH} символов`
  }
  return `Суммаризировать ${combinedTextLength.value} символов`
})

// Функция для отправки на суммаризацию
const generateSummary = async () => {
  // Проверка лимитов перед отправкой
  if (isTextTooLong.value) {
    error.value = `Текст превышает лимит ${MAX_TEXT_LENGTH} символов. Уменьшите количество выбранных постов.`
    setTimeout(() => { error.value = null }, 5000)
    return
  }
  
  if (isTextTooShort.value) {
    error.value = `Текст слишком короткий (${combinedTextLength.value} символов). Минимум ${MIN_TEXT_LENGTH} символов.`
    setTimeout(() => { error.value = null }, 5000)
    return
  }

  loading.value = true
  error.value = null
  summary.value = ''

  try {
    // Объединяем тексты постов
    const combinedText = props.selectedPosts
      .map(post => post.message || '')
      .filter(text => text.trim())
      .join('\n\n')
    
    // Дополнительная проверка (на всякий случай)
    if (combinedText.length > MAX_TEXT_LENGTH) {
      throw new Error(`Текст превышает максимальную длину ${MAX_TEXT_LENGTH} символов`)
    }
    
    if (combinedText.length < MIN_TEXT_LENGTH) {
      throw new Error(`Текст слишком короткий для суммаризации`)
    }

    console.log(`Отправка на суммаризацию: ${combinedText.length} символов`)
    
    // Отправляем на бэкенд
    const response = await apiClient.post('/summarization/summarize', {
      summary: combinedText
    }, {
      timeout: 60000 // 60 секунд таймаут
    })

    summary.value = response.data.summary
    console.log(`Получен результат: ${summary.value.length} символов`)

  } catch (err) {
    console.error('Ошибка при суммаризации:', err)
    
    // Форматируем сообщение об ошибке
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
    
    // Показываем ошибку в течение 5 секунд
    setTimeout(() => {
      error.value = null
    }, 5000)
  } finally {
    loading.value = false
  }
}

// Функция для экспорта в Word на фронтенде (упрощенная версия)
const exportToWord = async () => {
  if (props.selectedPosts.length === 0) return
  
  isExporting.value = true
  error.value = null

  try {
    // Создаем HTML документ с минимальным форматированием
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
    if (summary.value) {
      htmlContent += `
        <div class="summary">
          <strong>Суммаризация:</strong><br>
          ${summary.value}
        </div>
      `
    }
    
    // Добавляем посты
    props.selectedPosts.forEach((post, index) => {
      const postText = post.message || ''
      
      htmlContent += `
        <div class="post">
          <div class="post-header">
            <div class="post-meta">
              <strong>Пост ${index + 1}</strong> | 
              Канал: ${post.channel_name || 'Неизвестно'} | 
              Дата: ${formatDate(post.date)} | 
              Тема: #${formatTopicToHashtag(post.topic)}
            </div>
          </div>
      `
      
      if (postText) {
        // Разбиваем текст на абзацы
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
      
      // Добавляем разделитель между постами (кроме последнего)
      if (index < props.selectedPosts.length - 1) {
        htmlContent += '<div class="divider"></div>'
      }
    })
    
    // Простой футер
    htmlContent += `
        <div style="margin-top: 40px; text-align: right; font-size: 10pt; color: #888888;">
          Сформировано: ${new Date().toLocaleDateString('ru-RU')}
        </div>
      </body>
      </html>
    `
    
    // Создаем Blob и скачиваем как .doc файл
    const blob = new Blob([htmlContent], { 
      type: 'application/msword' 
    })
    
    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Генерируем имя файла
    const dateStr = new Date().toISOString().slice(0, 10)
    const fileName = `telegram_posts_${dateStr}.doc`
    
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    
    // Очищаем
    link.remove()
    window.URL.revokeObjectURL(url)
    
    console.log(`Word документ успешно экспортирован: ${fileName}`)
    
  } catch (err) {
    console.error('Ошибка при экспорте в Word:', err)
    error.value = 'Ошибка при создании Word документа: ' + err.message
    setTimeout(() => { error.value = null }, 5000)
  } finally {
    isExporting.value = false
  }
}

// Вспомогательная функция для разбивки текста на абзацы
const splitTextIntoParagraphs = (text, maxLength = 500) => {
  if (!text) return []
  
  const paragraphs = []
  let currentIndex = 0
  
  while (currentIndex < text.length) {
    const chunk = text.slice(currentIndex, currentIndex + maxLength)
    
    // Пытаемся разбить по предложениям
    const lastPeriod = chunk.lastIndexOf('.')
    const lastExclamation = chunk.lastIndexOf('!')
    const lastQuestion = chunk.lastIndexOf('?')
    const lastNewLine = chunk.lastIndexOf('\n')
    
    const breakIndex = Math.max(lastPeriod, lastExclamation, lastQuestion, lastNewLine)
    
    if (breakIndex > 0 && currentIndex + breakIndex < text.length) {
      paragraphs.push(chunk.slice(0, breakIndex + 1))
      currentIndex += breakIndex + 1
    } else {
      paragraphs.push(chunk)
      currentIndex += maxLength
    }
  }
  
  return paragraphs
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
</script>

<style scoped>
/* Стили остаются без изменений, как у вас в коде */
.selected-posts-panel {
  background: var(--white);
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left i {
  font-size: 1.5rem;
}

.header-left h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Стили для кнопок в header */
.header-action-btn {
  transition: all 0.2s ease;
  border-width: 1px !important;
  backdrop-filter: blur(5px);
  font-weight: 600;
}

/* Стиль для кнопки Word */
.header-action-btn.p-button-help {
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #2196F3 !important;
  border-color: rgba(255, 255, 255, 0.8) !important;
}

.header-action-btn.p-button-help:hover:not(:disabled) {
  background-color: #2196F3 !important;
  color: white !important;
  border-color: #2196F3 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3) !important;
}

/* Стиль для кнопки очистки */
.header-action-btn.p-button-danger {
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #f44336 !important;
  border-color: rgba(255, 255, 255, 0.8) !important;
}

.header-action-btn.p-button-danger:hover:not(:disabled) {
  background-color: #f44336 !important;
  color: white !important;
  border-color: #f44336 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3) !important;
}

.panel-content {
  padding: 20px;
}

/* Стили для суммаризации */
.summarization-controls {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
}

.summarization-info {
  margin-bottom: 15px;
  font-size: 14px;
}

.info-text {
  font-weight: 500;
  color: #667eea;
  display: block;
  margin-bottom: 8px;
}

.error-text {
  color: #dc3545;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 5px 0;
}

.warning-text {
  color: #ffc107;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 5px 0;
}

.success-text {
  color: #28a745;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 5px 0;
}

.summarization-actions {
  display: flex;
  justify-content: center;
}

.summary-preview {
  background: #f0f7ff;
  border: 1px solid #cce5ff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.1);
}

.summary-preview h4 {
  margin: 0 0 15px 0;
  color: #0056b3;
  font-size: 16px;
  font-weight: 600;
}

.summary-text {
  line-height: 1.6;
  font-size: 15px;
  color: #333;
  padding: 15px;
  background: white;
  border-radius: 6px;
  border-left: 4px solid #0056b3;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Сообщение об ошибке */
.error-message {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  color: #c53030;
  padding: 12px 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-message i {
  font-size: 1.2rem;
}

/* Информация о лимитах */
.limits-info {
  background: #e8f4fd;
  border: 1px solid #b6e0fe;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
  font-size: 14px;
}

.limits-info p {
  margin: 0 0 10px 0;
  font-weight: 600;
  color: #0056b3;
}

.limits-info ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.limits-info li {
  margin-bottom: 5px;
}

/* Список постов */
.selected-posts-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
  border: 1px solid #eee;
  border-radius: 6px;
}

.selected-post-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  background: #fafafa;
}

.selected-post-item:last-child {
  border-bottom: none;
}

.selected-post-item:hover {
  background: #f5f5f5;
}

.post-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 5px;
}

.post-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.channel-badge {
  background: #667eea;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.post-id {
  color: #666;
  font-size: 13px;
}

.post-length {
  color: #888;
  font-size: 12px;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 10px;
}

.post-date {
  color: #888;
  font-size: 13px;
  margin-bottom: 10px;
}

.post-preview {
  line-height: 1.5;
  margin-bottom: 10px;
  color: #333;
  font-size: 14px;
}

.post-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  font-size: 13px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.topic-tag {
  background: #e9ecef;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  margin-left: auto;
}

/* Оверлей загрузки */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: 8px;
}

.loading-overlay p {
  margin-top: 15px;
  color: #667eea;
  font-weight: 500;
}

/* Адаптивность */
@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .header-left, .header-right {
    justify-content: center;
  }
  
  .header-right {
    flex-wrap: wrap;
  }
  
  .summarization-actions button {
    width: 100%;
  }
  
  .post-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .post-length {
    align-self: flex-start;
  }
}
</style>