import apiClient from './client'

export const postsApi = {
  getPostsByDate(dateFrom, dateTo) {
    return apiClient.get('/analytics/posts-count-by-date', {
      params: { date_from: dateFrom, date_to: dateTo }
    })
  },
  
  getPostsBySpecificDate(date) {
    return apiClient.get('/analytics/posts-by-specific-date', {
      params: { date }
    })
  },
  

}