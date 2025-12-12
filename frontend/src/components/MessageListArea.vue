<template>
  <div class="message-list-area">
    <div v-if="loading" class="loading">Загрузка постов...</div>
    <div v-else-if="posts.length === 0" class="empty">Постов не найдено</div>
    <div v-else class="posts-list">
      <div v-for="post in posts" :key="post.id" class="post-card">
        <div class="post-header">
          <span class="channel-name">{{ post.channel_name }}</span>
          <span class="post-id">#{{ post.post_id }}</span>
          <span class="post-date">{{ new Date(post.date).toLocaleString('ru-RU') }}</span>
        </div>
        <div class="post-message">{{ post.message }}</div>
        <div class="post-stats">
          <span>👁️ {{ post.views }}</span>
          <span>💬 {{ post.comments_count }}</span>
          <span class="topic">{{ post.topic }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.message-list-area {
  margin-top: 30px;
  max-width: 1200px;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.post-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.channel-name {
  font-weight: bold;
  color: #333;
}

.post-message {
  line-height: 1.5;
  margin-bottom: 10px;
  white-space: pre-line;
}

.post-stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.topic {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}
</style>