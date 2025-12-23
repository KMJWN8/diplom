// composables/useSelection.js
import { ref } from 'vue'

export function useSelection() {
  const selectedDate = ref('')
  const selectedTopic = ref('')

  const setSelection = (type, value) => {
    if (type === 'date') {
      selectedDate.value = value
      selectedTopic.value = '' // Сбрасываем противоположный выбор
    } else if (type === 'topic') {
      selectedTopic.value = value
      selectedDate.value = '' // Сбрасываем противоположный выбор
    }
  }

  const resetSelection = () => {
    selectedDate.value = ''
    selectedTopic.value = ''
  }

  const hasSelection = () => {
    return !!selectedDate.value || !!selectedTopic.value
  }

  return {
    selectedDate,
    selectedTopic,
    setSelection,
    resetSelection,
    hasSelection
  }
}