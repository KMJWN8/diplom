// composables/useDateRange.js
import { ref } from 'vue'

export function useDateRange(defaultFrom = '2024-01-01', defaultTo = '2025-01-01') {
  const dateRange = ref({
    from: defaultFrom,
    to: defaultTo
  })

  const updateDateRange = (from, to) => {
    dateRange.value = { from, to }
  }

  const resetDateRange = () => {
    dateRange.value = {
      from: defaultFrom,
      to: defaultTo
    }
  }

  const isValidDateRange = () => {
    const from = new Date(dateRange.value.from)
    const to = new Date(dateRange.value.to)
    return from <= to
  }

  return {
    dateRange,
    updateDateRange,
    resetDateRange,
    isValidDateRange
  }
}