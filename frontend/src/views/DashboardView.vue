<script setup>
import Button from 'primevue/button';
import ToggleButton from 'primevue/togglebutton';
import MessageListArea from '@/components/MessageListArea.vue';
import PostsChart from '@/components/PostsChart.vue';
import { ref, onMounted, watch } from 'vue';
import { postsApi } from '@/api/endpoints';

const checked = ref(false);

// Диаграмма по темам
const topicsChartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Количество постов',
      data: [],
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1,
      borderRadius: 5,
    }
  ]
})

// Диаграмма по датам
const datesChartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Количество постов',
      data: [],
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1,
      borderRadius: 5,
    }
  ]
})

const posts = ref([])
const loading = ref(false)
const chartLoading = ref(false)
const selectedDate = ref('')
const selectedTopic = ref('')

const dateRange = ref({
  from: '2024-01-01',
  to: '2025-01-01'
})

// Опция переключения между диаграммами
const activeChart = ref('topics') // 'topics' или 'dates'

// Обновление цветов с выделением выбранной темы
const updateTopicsChartColors = (topics, counts, selectedTopic) => {
  
  return {
    labels: topics,
    datasets: [
      {
        label: 'Количество постов',
        data: counts,
        backgroundColor: topics.map((topic, index) => 
          topic === selectedTopic ? 'rgba(255, 99, 132, 0.8)' : 'rgba(54, 162, 235, 0.5)'
        ),
        borderColor: topics.map((topic, index) => 
          topic === selectedTopic ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'
        ),
        borderWidth: topics.map(topic => 
          topic === selectedTopic ? 3 : 1
        ),
        borderRadius: 5,
      }
    ]
  }
}

// Обновление цветов с выделением выбранной даты
const updateDatesChartColors = (dates, counts, selectedDate) => {
  return {
    labels: dates,
    datasets: [
      {
        label: 'Количество постов',
        data: counts,
        backgroundColor: dates.map(date => 
          date === selectedDate ? 'rgba(255, 99, 132, 0.8)' : 'rgba(54, 162, 235, 0.5)'
        ),
        borderColor: dates.map(date => 
          date === selectedDate ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'
        ),
        borderWidth: dates.map(date => 
          date === selectedDate ? 3 : 1
        ),
        borderRadius: 5,
      }
    ]
  }
}

// Загрузка данных для диаграммы по темам
const loadTopicsChartData = async () => {
  chartLoading.value = true
  try {
    const response = await postsApi.getPostsCountByTopic(
      dateRange.value.from, 
      dateRange.value.to
    )
    
    const data = response.data
    
    if (data.topics && data.counts) {
      topicsChartData.value = updateTopicsChartColors(
        data.topics, 
        data.counts,
        selectedTopic.value
      )
    }
  }
  catch (error) {
    console.error('Topics chart data fetch error:', error)
  }
  finally {
    chartLoading.value = false
  }
}

// Загрузка данных для диаграммы по датам
const loadDatesChartData = async () => {
  chartLoading.value = true
  try {
    const response = await postsApi.getPostsByDate(
      dateRange.value.from, 
      dateRange.value.to
    )
    
    const data = response.data
    
    if (data.dates && data.counts) {
      datesChartData.value = updateDatesChartColors(
        data.dates, 
        data.counts,
        selectedDate.value
      )
    }
  }
  catch (error) {
    console.error('Dates chart data fetch error:', error)
  }
  finally {
    chartLoading.value = false
  }
}

// Загрузка постов для конкретной даты
const getPostsByDate = async (date) => {
  loading.value = true
  selectedDate.value = date
  selectedTopic.value = '' // Сбрасываем выбор темы
  
  try {
    const response = await postsApi.getPostsBySpecificDate(date)
    posts.value = response.data
    
    // Обновляем цвета на диаграмме дат
    if (datesChartData.value.labels.length > 0) {
      datesChartData.value = updateDatesChartColors(
        datesChartData.value.labels, 
        datesChartData.value.datasets[0].data,
        selectedDate.value
      )
    }
  }
  catch (error) {
    console.error('Posts fetch error:', error)
    posts.value = []
  }
  finally {
    loading.value = false
  }
}

// Загрузка постов по теме
const getPostsByTopic = async (topic) => {
  selectedTopic.value = topic
  selectedDate.value = '' // Сбрасываем выбор даты
  
  loading.value = true
  // Обновляем цвета на диаграмме тем
  if (topicsChartData.value.labels.length > 0) {
    topicsChartData.value = updateTopicsChartColors(
      topicsChartData.value.labels, 
      topicsChartData.value.datasets[0].data,
      selectedTopic.value
    )
  }

  try {
    // Если есть API для постов по теме, используем его
    if (postsApi.getPostsByTopic) {
      const response = await postsApi.getPostsByTopic(
        topic,
        dateRange.value.from,
        dateRange.value.to
      )
      posts.value = response.data
    } else {
      // Иначе показываем сообщение
      console.warn('API для постов по теме не реализован')
      posts.value = []
    }
    
  }
  catch (error) {
    console.error('Posts by topic fetch error:', error)
    posts.value = []
  }
  finally {
    loading.value = false
  }
}

// Обработчик клика по диаграмме
const handleChartClick = (data) => {
  if (activeChart.value === 'topics') {
    handleTopicClick(data)
  } else {
    handleDateClick(data)
  }
}

const handleTopicClick = (topic) => {
  getPostsByTopic(topic)
}

const handleDateClick = (date) => {
  getPostsByDate(date)
}

// Сброс выбора
const resetSelection = () => {
  if (activeChart.value === 'topics') {
    selectedTopic.value = ''
    // Обновляем диаграмму без выделения
    if (topicsChartData.value.labels.length > 0) {
      topicsChartData.value = updateTopicsChartColors(
        topicsChartData.value.labels, 
        topicsChartData.value.datasets[0].data,
        ''
      )
    }
  } else {
    selectedDate.value = ''
    // Обновляем диаграмму без выделения
    if (datesChartData.value.labels.length > 0) {
      datesChartData.value = updateDatesChartColors(
        datesChartData.value.labels, 
        datesChartData.value.datasets[0].data,
        ''
      )
    }
  }
  posts.value = []
}

// Переключение между диаграммами
const toggleChart = (type) => {
  activeChart.value = type
  if (type === 'topics') {
    loadTopicsChartData()
  } else {
    loadDatesChartData()
  }
  // Сбрасываем выбор при переключении
  resetSelection()
}

// Загрузка данных при монтировании
onMounted(() => {
  loadTopicsChartData()
})

// Следим за изменением дат
watch(dateRange, () => {
  if (activeChart.value === 'topics') {
    loadTopicsChartData()
  } else {
    loadDatesChartData()
  }
  resetSelection()
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
          @click="activeChart === 'topics' ? loadTopicsChartData() : loadDatesChartData()" 
          :disabled="chartLoading"
          label="Обновить график" 
        />
        <Button 
          v-if="(selectedTopic || selectedDate) && posts.length > 0"
          @click="resetSelection" 
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
      :chart-data="activeChart === 'topics' ? topicsChartData : datesChartData"
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