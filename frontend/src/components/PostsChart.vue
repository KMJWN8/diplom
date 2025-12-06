<template>
  <div class="posts-chart">
    <div v-if="loading" class="loading">Загрузка диаграммы...</div>
    <div v-else-if="!hasData" class="no-data">Нет данных для отображения</div>
    <div v-else class="chart-container">
      <Bar 
        :data="chartData" 
        :options="chartOptions"
        ref="chartRef"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  CategoryScale, 
  LinearScale 
} from 'chart.js'

// Регистрируем компоненты Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  chartData: {
    type: Object,
    default: () => ({ labels: [], datasets: [] })
  },
  loading: {
    type: Boolean,
    default: false
  },
  chartType: {
    type: String,
    default: 'topics' // 'topics' или 'dates'
  }
})

const emit = defineEmits(['topicClick', 'dateClick'])

const chartRef = ref(null)

// Проверяем есть ли данные для отображения
const hasData = computed(() => {
  return props.chartData && 
         props.chartData.labels && 
         props.chartData.labels.length > 0 &&
         props.chartData.datasets &&
         props.chartData.datasets.length > 0 &&
         props.chartData.datasets[0].data &&
         props.chartData.datasets[0].data.length > 0
})

// Динамические заголовки
const chartTitle = computed(() => {
  return props.chartType === 'topics' 
    ? 'Количество постов по темам' 
    : 'Количество постов по датам'
})

const xAxisTitle = computed(() => {
  return props.chartType === 'topics' ? 'Темы' : 'Даты'
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: true,
      text: chartTitle
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          return `Постов: ${context.parsed.y}`
        },
        title: function(context) {
          return context[0].label
        }
      }
    }
  },
  onClick: (event, elements) => {
    if (elements.length > 0) {
      const index = elements[0].index
      const label = props.chartData.labels[index]
      
      if (props.chartType === 'topics') {
        emit('topicClick', label)
      } else {
        emit('dateClick', label)
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Количество постов'
      },
      ticks: {
        precision: 0 // Целые числа
      }
    },
    x: {
      title: {
        display: true,
        text: xAxisTitle
      },
      ticks: {
        maxRotation: props.chartType === 'dates' ? 45 : 0,
        callback: function(value) {
          // Для дат можно форматировать отображение
          if (props.chartType === 'dates') {
            const label = this.getLabelForValue(value)
            // Если дата в формате YYYY-MM-DD, преобразуем в DD.MM.YYYY
            if (label && label.match(/^\d{4}-\d{2}-\d{2}$/)) {
              const [year, month, day] = label.split('-')
              return `${day}.${month}.${year}`
            }
          }
          return this.getLabelForValue(value)
        }
      }
    }
  }
})

// Обновляем options при изменении chartType
watch(() => props.chartType, () => {
  chartOptions.value.plugins.title.text = chartTitle.value
  chartOptions.value.scales.x.title.text = xAxisTitle.value
})
</script>

<style scoped>
.posts-chart {
  height: 400px;
  margin-bottom: 20px;
}

.loading, .no-data {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.chart-container {
  height: 100%;
  position: relative;
}
</style>