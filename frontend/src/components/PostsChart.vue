<template>
  <div class="posts-chart" :class="{ 'is-loading': loading, 'has-no-data': !hasData }">
    <!-- Состояние загрузки -->
    <div v-if="loading" class="chart-state loading">
      <div class="spinner"></div>
      <span>Загрузка диаграммы...</span>
    </div>
    
    <!-- Состояние без данных -->
    <div v-else-if="!hasData" class="chart-state empty">
      <div class="empty-icon">📊</div>
      <p>Нет данных для отображения</p>
    </div>
    
    <!-- Диаграмма с данными -->
    <div v-else class="chart-content">
      <Bar 
        :data="chartData" 
        :options="chartOptions"
        ref="chartRef"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Bar } from 'vue-chartjs'

// Импорт композаблов
import { useChartConfiguration } from '@/composables/useChartConfiguration'
import { useChartValidation } from '@/composables/useChartValidation'

// Props
const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], datasets: [] })
  },
  loading: {
    type: Boolean,
    default: false
  },
  chartType: {
    type: String,
    default: 'topics',
    validator: (value) => ['topics', 'dates'].includes(value)
  }
})

// Emits
const emit = defineEmits(['topicClick', 'dateClick'])

// Refs
const chartRef = ref(null)

// Композаблы
const { chartOptions, isHorizontal } = useChartConfiguration(props, emit)
const { hasData, isValidData, totalItems } = useChartValidation(props)

// Методы
const updateChart = () => {
  if (chartRef.value?.chart) {
    chartRef.value.chart.update('none') // 'none' для отключения анимации
  }
}

const destroyChart = () => {
  if (chartRef.value?.chart) {
    chartRef.value.chart.destroy()
  }
}

// Наблюдатели
watch(() => props.chartData, () => {
  if (hasData.value) {
    nextTick(updateChart)
  }
}, { deep: true })

watch(() => props.chartType, () => {
  // Принудительное обновление при смене типа
  nextTick(updateChart)
})

// Хуки жизненного цикла
import { onUnmounted } from 'vue'
onUnmounted(destroyChart)

// Экспортируем методы
defineExpose({
  updateChart,
  destroyChart,
  getChart: () => chartRef.value?.chart
})
</script>

<style scoped>
.posts-chart {
  height: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
}

.chart-state.loading {
  background: linear-gradient(90deg, #f8f9fa 25%, #e9ecef 50%, #f8f9fa 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chart-state.empty {
  background: #f8f9fa;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.chart-state.empty p {
  margin: 0;
  font-size: 16px;
  color: #6c757d;
}

.chart-content {
  height: 100%;
  padding: 20px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .posts-chart {
    height: 400px;
  }
  
  .chart-content {
    padding: 10px;
  }
}
</style>