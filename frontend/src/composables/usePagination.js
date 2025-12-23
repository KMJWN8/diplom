import { ref, computed } from 'vue'

export function usePagination(items, itemsPerPage = 10) {
  const currentPage = ref(1)
  const perPage = ref(itemsPerPage)

  const totalPages = computed(() => {
    return Math.ceil(items.value.length / perPage.value)
  })

  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * perPage.value
    const end = start + perPage.value
    return items.value.slice(start, end)
  })

  const nextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  const resetPage = () => {
    currentPage.value = 1
  }

  return {
    currentPage,
    perPage,
    totalPages,
    paginatedItems,
    nextPage,
    prevPage,
    goToPage,
    resetPage
  }
}