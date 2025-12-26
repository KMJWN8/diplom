// composables/useChartConfiguration.js
import { 
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  CategoryScale, 
  LinearScale 
} from 'chart.js'
import { computed } from 'vue'

// Регистрируем компоненты Chart.js один раз
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export function useChartConfiguration(props, emit) {
  const chartOptions = computed(() => {
    const isHorizontal = props.chartType === 'topics'
    
    return {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: isHorizontal ? 'y' : 'x',
      plugins: getPluginsConfig(isHorizontal),
      scales: getScalesConfig(isHorizontal, props.chartType),
      layout: {
        padding: {
          left: 10,
          right: 10,
          top: 10,
          bottom: 20
        }
      },
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index
          const label = props.chartData.labels[index]
          const eventName = props.chartType === 'topics' ? 'topicClick' : 'dateClick'
          emit(eventName, label)
        }
      }
    }
  })
  
  return {
    chartOptions
  }
}

// Вспомогательные функции
function getPluginsConfig(isHorizontal) {
  return {
    legend: {
      display: false
    },
    title: {
      display: true,
      text: isHorizontal 
        ? 'Количество постов по темам' 
        : 'Количество постов по датам'
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          return isHorizontal 
            ? `${context.dataset.label}: ${context.parsed.x}`
            : `${context.dataset.label}: ${context.parsed.y}`
        },
        title: (context) => context[0].label
      },
      displayColors: true,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1
    }
  }
}

function getScalesConfig(isHorizontal, chartType) {
  return {
    x: {
      beginAtZero: true,
      title: {
        display: true,
        text: isHorizontal 
          ? 'Количество постов' 
          : (chartType === 'dates' ? 'Даты' : 'Темы')
      },
      ticks: {
        precision: 0,
        callback: function(value) {
          if (!isHorizontal && chartType === 'dates') {
            const label = this.getLabelForValue(value)
            if (label && /^\d{4}-\d{2}-\d{2}$/.test(label)) {
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
        autoSkip: !isHorizontal,
        maxTicksLimit: isHorizontal ? undefined : 20,
        maxRotation: isHorizontal ? 0 : 45,
        minRotation: 0,
        font: {
          size: isHorizontal ? 11 : 12
        },
        callback: function(value) {
          if (isHorizontal) {
            const label = this.getLabelForValue(value)
            if (label && label.length > 25) {
              return label.substring(0, 22) + '...'
            }
          }
          return this.getLabelForValue(value)
        }
      },
      grid: {
        display: !isHorizontal
      }
    }
  }
}