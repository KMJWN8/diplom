<!-- DashboardView.vue -->
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import Button from 'primevue/button'
import MessageListArea from '@/components/MessageListArea.vue'
import PostsChart from '@/components/PostsChart.vue'
import SelectedPostsPanel from '@/components/SelectedPostsPanel.vue'

// Импорт сторов Pinia
import { usePostsStore } from '@/stores/usePostsStore'
import { useChartStore } from '@/stores/useChartStore'
import { useDateStore } from '@/stores/useDateStore'
import { useUIStore } from '@/stores/useUIStore'

// Сторы
const postsStore = usePostsStore()
const chartStore = useChartStore()
const dateStore = useDateStore()
const uiStore = useUIStore()

// Локальные состояния
const checked = ref(false)
const activeChart = ref('topics')

// Вычисляемые свойства
const currentChartData = computed(() => chartStore.currentChartData)
const hasPosts = computed(() => postsStore.hasPosts)

// Методы компонента
const handleTopicClick = async (topic) => {
  chartStore.setSelection('topic', topic)
  await postsStore.getPostsByTopic(topic, dateStore.dateRange)
}

const handleDateClick = async (date) => {
  chartStore.setSelection('date', date)
  await postsStore.getPostsByDate(date)
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
}

const toggleChart = async (type) => {
  chartStore.setChartType(type)
  await loadChartData()
  resetAll()
}

const loadChartData = async () => {
  uiStore.setLoading('chart', true)
  await chartStore.loadChartData(dateStore.dateRange)
  uiStore.setLoading('chart', false)
}

const refreshChart = async () => {
  await loadChartData()
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
watch(() => dateStore.dateRange, async () => {
  await loadChartData()
  resetAll()
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
          :severity="chartStore.chartType === 'topics' ? 'primary' : 'secondary'"
          label="По темам" 
        />
        <Button 
          @click="toggleChart('dates')" 
          :severity="chartStore.chartType === 'dates' ? 'primary' : 'secondary'"
          label="По датам" 
        />
      </div>
      
      <div class="date-range-controls">
        <label>Период анализа:</label>
        <input 
          type="date" 
          v-model="dateStore.dateRange.from" 
        />
        <span>по</span>
        <input 
          type="date" 
          v-model="dateStore.dateRange.to" 
        />
        <Button 
          @click="refreshChart" 
          :disabled="uiStore.loadingStates.chart"
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
          {{ chartStore.chartType === 'topics' ? 'Выберите тему из графика' : 'Выберите дату из графика' }}
        </span>
        <span>Найдено постов: <strong>{{ postsStore.postsCount }}</strong></span>
      </div>
    </div>

    <PostsChart 
      :chart-data="currentChartData"
      :loading="uiStore.loadingStates.chart"
      :chart-type="chartStore.chartType"
      @topic-click="handleTopicClick"
      @date-click="handleDateClick"
    />

    <MessageListArea 
      :posts="postsStore.posts"
      :loading="postsStore.loading"
      @toggle-selection="postsStore.togglePostSelection"
    />

    <SelectedPostsPanel 
      :selected-posts="postsStore.getSelectedPosts"
      @remove-post="(postId) => {
        const post = postsStore.posts.find(p => p.id === postId)
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

.current-selection {
  display: flex;
  gap: 20px;
  font-size: 14px;
  align-items: center;
}

.prime-buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}
</style>