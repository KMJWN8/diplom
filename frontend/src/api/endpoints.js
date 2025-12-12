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

  getPostsCountByTopic(dateFrom, dateTo) {
    return apiClient.get('/analytics/posts-count-by-topic', {
      params: { date_from: dateFrom, date_to: dateTo }
    })
  },

  getPostsByTopic(topic, dateFrom, dateTo) {
    return apiClient.get('/analytics/posts-by-topic', {
      params: {
        topic: topic,
        date_from: dateFrom,
        date_to: dateTo
      }
    })
  },

  getChannels() {
    return apiClient.get('/analytics/channels')
  },

  addChannel(channelLink) {
    return apiClient.post('/channel', null, {
      params: {
        channel_link: channelLink
      }
    })
  },
  
  deleteChannel(channelId) {
    return apiClient.delete(`/analytics/channels/${channelId}`)
  },
  
}