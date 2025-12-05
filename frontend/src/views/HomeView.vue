<script setup>
import Button from 'primevue/button';
import ToggleButton from 'primevue/togglebutton';
import MessageListArea from '@/components/MessageListArea.vue';
import PostsChart from '@/components/PostsChart.vue';
import { ref, onMounted } from 'vue';
import { postsApi } from '@/api/endpoints';

const checked = ref(false);

const posts = ref([])
const chartData = ref({
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
const loading = ref(false)
const chartLoading = ref(false)
const selectedDate = ref('2025-01-01') // Выбранная дата для выделения
const dateRange = ref({
  from: '2024-01-01',
  to: '2025-01-01'
})

// Функция для обновления цветов с выделением
const updateChartColors = (dates, counts) => {
  return {
    labels: dates,
    datasets: [
      {
        label: 'Количество постов',
        data: counts,
        backgroundColor: dates.map(date => 
          date === selectedDate.value ? 'rgba(255, 99, 132, 0.8)' : 'rgba(54, 162, 235, 0.5)'
        ),
        borderColor: dates.map(date => 
          date === selectedDate.value ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'
        ),
        borderWidth: dates.map(date => 
          date === selectedDate.value ? 3 : 1
        ),
        borderRadius: 5,
      }
    ]
  }
}

// Загрузка данных для диаграммы
const loadChartData = async () => {
  chartLoading.value = true
  try {
    const response = await postsApi.getPostsByDate(
      dateRange.value.from, 
      dateRange.value.to
    )
    
    const data = response.data
    
    if (data.dates && data.counts) {
      chartData.value = updateChartColors(data.dates, data.counts)
    }
  }
  catch (error) {
    console.error('Chart data fetch error:', error)
  }
  finally {
    chartLoading.value = false
  }
}

// Загрузка постов для конкретной даты
const getPostsByDate = async (date) => {
  loading.value = true

  await new Promise(resolve => setTimeout(resolve, 200));

  selectedDate.value = date
  
  try {
    const response = await postsApi.getPostsBySpecificDate(date)
    posts.value = response.data
    
    // Обновляем цвета на диаграмме
    if (chartData.value.labels.length > 0) {
      chartData.value = updateChartColors(
        chartData.value.labels, 
        chartData.value.datasets[0].data
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

// Обработчик клика по диаграмме
const handleDateClick = (date) => {
  getPostsByDate(date)
}

// Загрузка данных при монтировании
onMounted(() => {
  loadChartData()
  getPostsByDate(selectedDate.value)
})
</script>

<template>
  <div class="home-page">
    <h1>Аналитика Telegram постов</h1>
    
    <div class="controls">
      <div class="date-range-controls">
        <label>Период анализа:</label>
        <input 
          type="date" 
          v-model="dateRange.from" 
          @change="loadChartData"
        />
        <span>по</span>
        <input 
          type="date" 
          v-model="dateRange.to" 
          @change="loadChartData"
        />
        <Button 
          @click="loadChartData" 
          :disabled="chartLoading"
          label="Обновить график" 
        />
      </div>
      
      <div class="current-selection">
        <span>Выбранная дата: <strong>{{ selectedDate }}</strong></span>
        <span>Найдено постов: <strong>{{ posts.length }}</strong></span>
      </div>
    </div>

    <PostsChart 
      :chart-data="chartData"
      :loading="chartLoading"
      @date-click="handleDateClick"
    />

    <div class="prime-buttons">
      <Button label="Profile" icon="pi pi-user" severity="info" />
      <ToggleButton v-model="checked" class="w-24" onLabel="On" offLabel="Off" />
    </div>

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
}

.current-selection {
  display: flex;
  gap: 20px;
  font-size: 14px;
}

.prime-buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}
</style>