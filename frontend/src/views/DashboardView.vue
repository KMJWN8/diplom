<script setup>
import Button from 'primevue/button';
import MessageListArea from '@/components/MessageListArea.vue';
import PostsChart from '@/components/PostsChart.vue';
import { ref, onMounted, watch, computed } from 'vue';

import { usePosts } from '@/composables/usePosts'
import { useChartData } from '@/composables/useChartData'
import { useSelection } from '@/composables/useSelection'
import { useDateRange } from '@/composables/useDateRange'


const { posts, loading, clearPosts, getPostsByDate, getPostsByTopic } = usePosts()
const { selectedDate, selectedTopic, setSelection, resetSelection } = useSelection()
const { dateRange } = useDateRange()
const { 
  topicsChartData, 
  datesChartData, 
  chartLoading, 
  loadTopicsChartData, 
  loadDatesChartData,
  updateChartColors 
} = useChartData()

// Локальные состояния компонента
const checked = ref(false)
const activeChart = ref('topics') // 'topics' или 'dates'

// Вычисляемые свойства
const currentChartData = computed(() => 
  activeChart.value === 'topics' ? topicsChartData.value : datesChartData.value
)

const hasPosts = computed(() => posts.value.length > 0)

// Методы компонента
const handleTopicClick = async (topic) => {
  setSelection('topic', topic)
  await updateChartColors(activeChart.value, { topic })
  await getPostsByTopic(topic, dateRange.value)
}

const handleDateClick = async (date) => {
  setSelection('date', date)
  await updateChartColors(activeChart.value, { date })
  await getPostsByDate(date)
}

const handleChartClick = (data) => {
  if (activeChart.value === 'topics') {
    handleTopicClick(data)
  } else {
    handleDateClick(data)
  }
}

const resetAll = () => {
  resetSelection()
  clearPosts()
  updateChartColors(activeChart.value, { 
    [activeChart.value === 'topics' ? 'topic' : 'date']: '' 
  })
}

const toggleChart = async (type) => {
  activeChart.value = type
  await loadChartData()
  resetAll()
}

const loadChartData = async () => {
  if (activeChart.value === 'topics') {
    await loadTopicsChartData(dateRange.value)
  } else {
    await loadDatesChartData(dateRange.value)
  }
}

const refreshChart = () => {
  loadChartData()
  resetAll()
}

// Хуки жизненного цикла
onMounted(() => {
  loadChartData()
})

// Наблюдатели
watch(dateRange, () => {
  loadChartData()
  resetAll()
}, { deep: true })
</script>

<template>
  <div class="home-page">
    <h1>Аналитика Telegram постов</h1>
    
    <div class="controls">
      <div class="chart-selector">
        <Button 
          @click="toggleChart('topics')" 
          :severity="activeChart === 'topics' ? 'primary' : 'secondary'"
          label="По темам" 
        />
        <Button 
          @click="toggleChart('dates')" 
          :severity="activeChart === 'dates' ? 'primary' : 'secondary'"
          label="По датам" 
        />
      </div>
      
      <div class="date-range-controls">
        <label>Период анализа:</label>
        <input 
          type="date" 
          v-model="dateRange.from" 
        />
        <span>по</span>
        <input 
          type="date" 
          v-model="dateRange.to" 
        />
        <Button 
          @click="refreshChart" 
          :disabled="chartLoading"
          label="Обновить график" 
        />
        <Button 
          v-if="(selectedTopic || selectedDate) && hasPosts"
          @click="resetAll" 
          label="Сбросить выбор" 
          severity="secondary"
        />
      </div>
      
      <div class="current-selection">
        <span v-if="activeChart === 'topics' && selectedTopic">
          Выбранная тема: <strong>{{ selectedTopic }}</strong>
        </span>
        <span v-else-if="activeChart === 'dates' && selectedDate">
          Выбранная дата: <strong>{{ selectedDate }}</strong>
        </span>
        <span v-else>
          {{ activeChart === 'topics' ? 'Выберите тему из графика' : 'Выберите дату из графика' }}
        </span>
        <span>Найдено постов: <strong>{{ posts.length }}</strong></span>
      </div>
    </div>

    <PostsChart 
      :chart-data="currentChartData"
      :loading="chartLoading"
      :chart-type="activeChart"
      @topic-click="handleTopicClick"
      @date-click="handleDateClick"
    />

    <MessageListArea 
      :posts="posts"
      :loading="loading"
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