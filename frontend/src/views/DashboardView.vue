<!-- DashboardView.vue -->
<script setup>
import { onMounted, computed, watch } from 'vue'
import Button from 'primevue/button'
import MessageListArea from '@/components/MessageListArea.vue'
import PostsChart from '@/components/PostsChart.vue'
import SelectedPostsPanel from '@/components/SelectedPostsPanel.vue'

// Импорт сторов Pinia
import { usePostsStore } from '@/stores/usePostsStore'
import { useChartStore } from '@/stores/useChartStore'
import { useDateStore } from '@/stores/useDateStore'
import { useUIStore } from '@/stores/useUIStore'
import { useSummarizationStore } from '@/stores/useSummarizationStore'

// Сторы
const postsStore = usePostsStore()
const chartStore = useChartStore()
const dateStore = useDateStore()
const uiStore = useUIStore()
const summarizationStore = useSummarizationStore()

// Вычисляемые свойства
const currentChartData = computed(() => chartStore.currentChartData)
const hasPosts = computed(() => postsStore.hasPosts)
const activeChart = computed(() => chartStore.chartType)

// Методы компонента
const handleTopicClick = async (topic) => {
  console.log('Выбрана тема:', topic)
  chartStore.setSelection('topic', topic)
  
  // Загружаем посты для выбранной темы
  uiStore.setLoading('posts', true)
  await postsStore.getPostsByTopic(topic, dateStore.dateRange)
  uiStore.setLoading('posts', false)
}

const handleDateClick = async (date) => {
  console.log('Выбрана дата:', date)
  chartStore.setSelection('date', date)
  
  // Загружаем посты для выбранной даты
  uiStore.setLoading('posts', true)
  await postsStore.getPostsByDate(date)
  uiStore.setLoading('posts', false)
}

const handleChartClick = (data) => {
  if (chartStore.chartType === 'topics') {
    handleTopicClick(data)
  } else {
    handleDateClick(data)
  }
}

const resetAll = () => {
  chartStore.resetSelection()
  postsStore.clearPosts()
  summarizationStore.clearSummary()
}

const toggleChart = async (type) => {
  if (chartStore.chartType === type) return // Не переключаем если уже выбран
  
  console.log('Переключение на тип:', type)
  
  // Сохраняем текущий выбор перед переключением
  const currentSelection = chartStore.selectedTopic || chartStore.selectedDate
  
  // Переключаем тип графика
  uiStore.setLoading('chart', true)
  await chartStore.setChartType(type, dateStore.dateRange)
  uiStore.setLoading('chart', false)
  
  // Если был выбор на предыдущем графике, сбрасываем его
  if (currentSelection) {
    chartStore.resetSelection()
  }
  
  // Очищаем посты при переключении типа графика
  postsStore.clearPosts()
}

const loadChartData = async (forceRefresh = false) => {
  uiStore.setLoading('chart', true)
  const result = await chartStore.loadChartData(dateStore.dateRange, forceRefresh)
  uiStore.setLoading('chart', false)
  
  if (result.cached) {
    console.log('Данные графика загружены из кэша')
  }
  
  return result
}

const refreshChart = async () => {
  // Принудительное обновление
  await loadChartData(true)
  
  // Сбрасываем все выборы
  resetAll()
}

// Хуки жизненного цикла
onMounted(async () => {
  uiStore.setLoading('init', true)
  
  // Восстанавливаем состояние
  postsStore.restoreSelections()
  
  // Загружаем данные графика
  await loadChartData()
  
  uiStore.setLoading('init', false)
})

// Наблюдатели
watch(() => dateStore.dateRange, async (newRange) => {
  console.log('Диапазон дат изменен:', newRange)
  
  // При изменении диапазона дат очищаем кэш и загружаем заново
  chartStore.clearCache()
  await loadChartData(true)
  
  // Очищаем посты
  postsStore.clearPosts()
  summarizationStore.clearSummary()
}, { deep: true })

// Экспортируем методы для доступа
defineExpose({
  refreshChart,
  resetAll,
  loadChartData
})
</script>

<template>
  <div class="home-page">
    <h1>Аналитика Telegram постов</h1>
    
    <div class="controls">
      <div class="chart-selector">
        <Button 
          @click="toggleChart('topics')" 
          :severity="activeChart === 'topics' ? 'primary' : 'secondary'"
          :loading="uiStore.loadingStates.chart && activeChart === 'topics'"
          label="По темам" 
        />
        <Button 
          @click="toggleChart('dates')" 
          :severity="activeChart === 'dates' ? 'primary' : 'secondary'"
          :loading="uiStore.loadingStates.chart && activeChart === 'dates'"
          label="По датам" 
        />
      </div>
      
      <div class="date-range-controls">
        <label>Период анализа:</label>
        <input 
          type="date" 
          v-model="dateStore.dateRange.from" 
          :disabled="uiStore.loadingStates.chart"
        />
        <span>по</span>
        <input 
          type="date" 
          v-model="dateStore.dateRange.to" 
          :disabled="uiStore.loadingStates.chart"
        />
        <Button 
          @click="refreshChart" 
          :disabled="uiStore.loadingStates.chart"
          :loading="uiStore.loadingStates.chart"
          label="Обновить график" 
        />
        <Button 
          v-if="chartStore.hasSelection && hasPosts"
          @click="resetAll" 
          label="Сбросить выбор" 
          severity="secondary"
        />
      </div>
      
      <div class="current-selection">
        <span v-if="chartStore.selectedTopic">
          Выбранная тема: <strong>{{ chartStore.selectedTopic }}</strong>
        </span>
        <span v-else-if="chartStore.selectedDate">
          Выбранная дата: <strong>{{ chartStore.selectedDate }}</strong>
        </span>
        <span v-else>
          {{ activeChart === 'topics' ? 'Выберите тему из графика' : 'Выберите дату из графика' }}
        </span>
        <span>Найдено постов: <strong>{{ postsStore.postsCount }}</strong></span>
        <span v-if="postsStore.selectedPostsCount > 0">
          Выбрано: <strong>{{ postsStore.selectedPostsCount }}</strong>
        </span>
      </div>
    </div>

    <PostsChart 
      :chart-data="currentChartData"
      :loading="uiStore.loadingStates.chart"
      :chart-type="activeChart"
      @topic-click="handleTopicClick"
      @date-click="handleDateClick"
    />

    <MessageListArea 
      :posts="postsStore.posts"
      :loading="uiStore.loadingStates.posts || postsStore.loading"
      @toggle-selection="postsStore.togglePostSelection"
    />

    <SelectedPostsPanel 
      :selected-posts="postsStore.getSelectedPosts"
      @remove-post="(postId) => {
        const post = postsStore.getPostById(postId)
        if (post) postsStore.togglePostSelection(post)
      }"
      @clear-selection="postsStore.clearSelections"
      @generate-report="postsStore.generateReport"
      @share-selection="postsStore.shareSelection"
    />
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.chart-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.date-range-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.date-range-controls label {
  font-weight: 500;
}

.date-range-controls input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.date-range-controls input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.current-selection {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  align-items: center;
}

.current-selection span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.prime-buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

/* Стили для состояний загрузки */
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button.p-button-loading {
  position: relative;
  color: transparent !important;
}

button.p-button-loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16px;
  height: 16px;
  margin: -8px 0 0 -8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>