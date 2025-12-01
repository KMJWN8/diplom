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
  }
})

const emit = defineEmits(['dateClick'])

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

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: true,
      text: 'Количество постов по датам'
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          return `Постов: ${context.parsed.y}`
        }
      }
    }
  },
  onClick: (event, elements) => {
    if (elements.length > 0) {
      const index = elements[0].index
      const date = props.chartData.labels[index]
      emit('dateClick', date)
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Количество постов'
      }
    },
    x: {
      title: {
        display: true,
        text: 'Даты'
      }
    }
  }
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