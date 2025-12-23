<template>
  <div v-if="selectedPosts.length > 0" class="selected-posts-panel">
    <!-- Заголовок панели -->
    <div class="panel-header">
      <div class="header-left">
        <i class="pi pi-folder-open" />
        <h3>Выбранные посты для отчета ({{ selectedPosts.length }})</h3>
      </div>
      <div class="header-right">
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

    <!-- Содержимое панели -->
    <div class="panel-content">

      <!-- Список выбранных постов -->
      <div class="selected-posts-list">
        <div v-for="post in selectedPosts" :key="post.id" class="selected-post-item">
          <div class="post-item-header">
            <div class="post-info">
              <span class="channel-badge">{{ post.channel_name }}</span>
              <span class="post-id">#{{ post.post_id }}</span>
            </div>
            <div class="post-actions">
              <Button 
                @click="$emit('remove-post', post.id)"
                icon="pi pi-times"
                severity="danger"
                text
                size="small"
                :title="'Удалить из отчета'"
              />
            </div>
          </div>
          
          <div class="post-date">
            {{ formatDate(post.date) }}
          </div>
          
          <div class="post-preview">
            {{ truncateText(post.message, 100) }}
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

      <!-- Действия с выбранными постами -->
      <div class="panel-actions">
        <Button 
          @click="$emit('generate-report', selectedPosts)"
          icon="pi pi-file-word"
          label="Сгенерировать отчет"
          severity="warning"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Button from 'primevue/button'
import { usePosts } from '@/composables/usePosts'

const props = defineProps({
  selectedPosts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'remove-post',
  'clear-selection',
  'generate-report',
  'export-excel'
])

const { formatTopicToHashtag } = usePosts()

// Вычисляемые свойства
const uniqueChannels = computed(() => {
  const channels = props.selectedPosts.map(post => post.channel_name)
  return new Set(channels).size
})

const uniqueTopics = computed(() => {
  const topics = props.selectedPosts.map(post => post.topic)
  return new Set(topics).size
})

const dateRange = computed(() => {
  if (props.selectedPosts.length === 0) return '-'
  
  const dates = props.selectedPosts.map(post => new Date(post.date))
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  
  if (minDate.toDateString() === maxDate.toDateString()) {
    return minDate.toLocaleDateString('ru-RU')
  }
  
  return `${minDate.toLocaleDateString('ru-RU')} - ${maxDate.toLocaleDateString('ru-RU')}`
})

// Вспомогательные функции
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text || ''
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.selected-posts-panel {
  background: var(--white);
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: var(--primary-light);
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

.panel-content {
  padding: 20px;
}

.selected-posts-list {
  max-height: 300px;
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

.panel-actions {
  display: flex;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

.header-action-btn {
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #f44336 !important;
  border-color: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(5px);
  font-weight: 600;
}

.header-action-btn:hover {
  background-color: white !important;
  border-color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
}

.header-action-btn:active {
  transform: translateY(0);
}

.header-action-btn .pi {
  color: #f44336 !important;
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
  
  .panel-actions {
    flex-direction: column;
  }
  
  .panel-actions button {
    width: 100%;
  }
}
</style>