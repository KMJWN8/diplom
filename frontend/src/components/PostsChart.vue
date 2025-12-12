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

// Основные настройки графика
const chartOptions = computed(() => {
  const isHorizontal = props.chartType === 'topics'
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: isHorizontal ? 'y' : 'x', // Горизонтальная для тем
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: isHorizontal ? 'Количество постов по темам' : 'Количество постов по датам'
      },
      tooltip: {
        callbacks: {
          // Правильно определяем label в зависимости от типа диаграммы
          label: function(context) {
            if (isHorizontal) {
              // Для горизонтальной диаграммы значение находится по оси X
              return `${context.dataset.label}: ${context.parsed.x}`
            } else {
              // Для вертикальной диаграммы значение находится по оси Y
              return `${context.dataset.label}: ${context.parsed.y}`
            }
          },
          title: function(context) {
            // Для заголовка всегда используем label
            return context[0].label
          }
        },
        // Для лучшего отображения
        displayColors: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
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
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: isHorizontal ? 'Количество постов' : (props.chartType === 'dates' ? 'Даты' : 'Темы')
        },
        ticks: {
          precision: 0, // Целые числа
          // Для горизонтальной диаграммы (темы) на оси X отображаются количества
          // Для вертикальной диаграммы (даты) на оси X отображаются даты
          callback: function(value) {
            if (!isHorizontal && props.chartType === 'dates') {
              const label = this.getLabelForValue(value)
              if (label && label.match(/^\d{4}-\d{2}-\d{2}$/)) {
                const [year, month, day] = label.split('-')
                return `${day}.${month}`
              }
            }
            return this.getLabelForValue(value)
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      y: {
        title: {
          display: true,
          text: isHorizontal ? 'Темы' : 'Количество постов'
        },
        ticks: {
          // Для вертикальной диаграммы (даты) на оси Y отображаются количества
          // Для горизонтальной диаграммы (темы) на оси Y отображаются названия тем
          autoSkip: !isHorizontal, // Для тем не пропускаем подписи
          maxTicksLimit: isHorizontal ? undefined : 20,
          maxRotation: isHorizontal ? 0 : 45,
          minRotation: isHorizontal ? 0 : 0,
          font: {
            size: isHorizontal ? 11 : 12
          },
          callback: function(value) {
            if (isHorizontal) {
              const label = this.getLabelForValue(value)
              // Для тем: обрезаем слишком длинные названия
              if (label && label.length > 25) {
                return label.substring(0, 22) + '...'
              }
            }
            return this.getLabelForValue(value)
          }
        },
        grid: {
          display: !isHorizontal // Убираем сетку только для вертикальной оси в горизонтальной диаграмме
        }
      }
    },
    // Дополнительные настройки для лучшего отображения
    layout: {
      padding: {
        left: 10,
        right: 10,
        top: 10,
        bottom: 20
      }
    }
  }
  
  return options
})
</script>

<style scoped>
.posts-chart {
  /* Увеличиваем высоту для лучшего отображения тем */
  height: 500px;
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
  /* Добавляем возможность горизонтальной прокрутки */
  min-width: 600px;
}

/* Для родительского контейнера добавьте */
:deep(.chartjs-render-monitor) {
  width: 100% !important;
}
</style>