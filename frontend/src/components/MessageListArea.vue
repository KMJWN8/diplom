<template>
  <div class="message-list-area">
    <!-- Панель управления пагинацией -->
    <div v-if="posts.length > 0" class="pagination-controls">
      <div class="pagination-info">
        <span>Показано {{ startItem }}-{{ endItem }} из {{ totalItems }}</span>
      </div>
      
      <div class="pagination-buttons">
        <Button 
          @click="prevPage" 
          :disabled="currentPage === 1"
          icon="pi pi-chevron-left"
          severity="secondary"
          text
        />
        
        <div class="page-numbers">
          <template v-for="page in visiblePages" :key="page">
            <Button 
              @click="goToPage(page)"
              :severity="currentPage === page ? 'primary' : 'secondary'"
              :text="currentPage !== page"
              :label="page.toString()"
            />
          </template>
          
          <span v-if="showEllipsis" class="ellipsis">...</span>
          
          <Button 
            v-if="totalPages > 1 && !visiblePages.includes(totalPages)"
            @click="goToPage(totalPages)"
            :severity="currentPage === totalPages ? 'primary' : 'secondary'"
            :text="currentPage !== totalPages"
            :label="totalPages.toString()"
          />
        </div>
        
        <Button 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
          icon="pi pi-chevron-right"
          severity="secondary"
          text
        />
      </div>
      
      <div class="items-per-page">
        <label>На странице:</label>
        <Select 
          v-model="itemsPerPage"
          :options="[5, 10, 20, 50, 100]"
          @change="handleItemsPerPageChange"
          class="per-page-dropdown"
        />
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="loading">Загрузка постов...</div>
    
    <!-- Пустой список -->
    <div v-else-if="posts.length === 0" class="empty">Постов не найдено</div>
    
    <!-- Список постов -->
    <div v-else class="posts-list">
      <div v-for="post in paginatedPosts" :key="post.id" class="post-card">
        <div class="post-header">
          <span class="channel-name">{{ post.channel_name }}</span>
          <span class="post-id">#{{ post.post_id }}</span>
          <span class="post-date">{{ formatDate(post.date) }}</span>
        </div>
        <div class="post-header-right">
          <Button 
            @click.stop="$emit('toggle-selection', post)"
            :icon="post.isSelected ? 'pi pi-star-fill' : 'pi pi-star'"
            :severity="post.isSelected ? 'warning' : 'secondary'"
            text
            rounded
            :title="post.isSelected ? 'Убрать из отчета' : 'Добавить в отчет'"
          />
        </div>
        <div class="post-message">{{ post.message }}</div>
        <div class="post-stats">
          <span>👁️ {{ post.views }}</span>
          <span>💬 {{ post.comments_count }}</span>
          <span class="topic">{{ postsStore.formatTopicToHashtag(post.topic) }}</span>
        </div>
      </div>
    </div>

    <!-- Упрощенная пагинация снизу -->
    <div v-if="posts.length > 0" class="pagination-bottom">
      <div class="pagination-summary">
        <span>Страница {{ currentPage }} из {{ totalPages }}</span>
      </div>
      
      <div class="pagination-nav">
        <Button 
          @click="prevPage" 
          :disabled="currentPage === 1"
          label="Предыдущая"
          severity="secondary"
          outlined
        />
        
        <span class="page-counter">{{ currentPage }}/{{ totalPages }}</span>
        
        <Button 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
          label="Следующая"
          severity="secondary"
          outlined
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps } from 'vue'
import Button from 'primevue/button'
import { Select } from 'primevue'

// Импорт стора
import { usePostsStore } from '@/stores/usePostsStore'

const postsStore = usePostsStore()

const props = defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Состояния пагинации
const currentPage = ref(1)
const itemsPerPage = ref(5)

// Вычисляемые свойства
const totalItems = computed(() => props.posts.length)
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))

const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return props.posts.slice(start, end)
})

const startItem = computed(() => (currentPage.value - 1) * itemsPerPage.value + 1)
const endItem = computed(() => {
  const end = currentPage.value * itemsPerPage.value
  return end > totalItems.value ? totalItems.value : end
})

const emit = defineEmits(['toggle-selection'])

// Видимые номера страниц
const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  
  if (totalPages.value <= maxVisible) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage.value <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
    } else if (currentPage.value >= totalPages.value - 2) {
      for (let i = totalPages.value - 3; i <= totalPages.value; i++) pages.push(i)
    } else {
      for (let i = currentPage.value - 1; i <= currentPage.value + 1; i++) pages.push(i)
    }
  }
  
  return pages
})

const showEllipsis = computed(() => {
  return totalPages.value > 5 && currentPage.value < totalPages.value - 2
})

// Методы пагинации
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const handleItemsPerPageChange = () => {
  currentPage.value = 1
}

// Вспомогательная функция
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Сбрасываем на первую страницу при изменении списка постов
watch(() => props.posts, () => {
  currentPage.value = 1
}, { deep: true })

// Следим за количеством страниц
watch(totalPages, (newTotal) => {
  if (currentPage.value > newTotal && newTotal > 0) {
    currentPage.value = newTotal
  }
})
</script>

<style scoped>
.message-list-area {
  margin-top: 30px;
  max-width: 1200px;
}

/* Пагинация сверху */
.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.pagination-info {
  font-size: 14px;
  color: #666;
  min-width: 150px;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 5px;
}

.page-numbers {
  display: flex;
  gap: 5px;
  align-items: center;
  flex-wrap: wrap;
}

.ellipsis {
  padding: 0 10px;
  color: #666;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 150px;
  justify-content: flex-end;
}

.items-per-page label {
  font-size: 14px;
  color: #666;
}

.per-page-dropdown {
  width: 85px;
}

/* Стили для списка постов */
.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 400px;
}

.post-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
  gap: 10px;
}

.post-header-left {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.post-header-right {
  display: flex;
  align-items: center;
}

.channel-name {
  font-weight: bold;
  color: #333;
}

.post-message {
  line-height: 1.5;
  margin-bottom: 10px;
  white-space: pre-line;
  max-height: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
}

.post-stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
  align-items: center;
}

.topic {
  background: #e9ecef;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: auto;
}

/* Пагинация снизу */
.pagination-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.pagination-summary {
  font-size: 14px;
  color: #666;
}

.pagination-nav {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-counter {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

/* Адаптивность */
@media (max-width: 768px) {
  .pagination-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pagination-info,
  .items-per-page {
    justify-content: center;
    text-align: center;
  }
  
  .pagination-buttons {
    justify-content: center;
  }
  
  .pagination-bottom {
    flex-direction: column;
    gap: 15px;
  }
  
  .pagination-nav {
    width: 100%;
    justify-content: center;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .post-stats {
    flex-wrap: wrap;
  }
  
  .topic {
    margin-left: 0;
  }
}
</style>