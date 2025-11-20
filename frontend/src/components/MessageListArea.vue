<template>
  <div class="posts-container">
    <Fieldset 
      v-for="post in tgPosts" 
      :key="post.id"
      :legend="post.channel"
      :toggleable="true"
      class="mb-4"
    >
      <div class="post-content">
        <p class="m-0 whitespace-pre-wrap">{{ post.text }}</p>
        
        <!-- Медиа вложения -->
        <div v-if="post.media" class="media-container mt-3">
          <img 
            v-if="isImage(post.media)" 
            :src="post.media" 
            :alt="post.text"
            class="post-media"
          />
          <div v-else class="media-file">
            <i class="pi pi-file text-2xl"></i>
            <span>Вложение</span>
          </div>
        </div>
        
        <!-- Мета-информация -->
        <div class="post-meta mt-3 pt-3 border-top-1 surface-border">
          <div class="flex align-items-center gap-3 text-sm text-color-secondary">
            <span><i class="pi pi-calendar mr-1"></i> {{ formatDate(post.date) }}</span>
            <span><i class="pi pi-eye mr-1"></i> {{ post.views }} просмотров</span>
            <span v-if="post.reactions" class="flex align-items-center gap-1">
              <i class="pi pi-heart mr-1"></i>
              {{ post.reactions }}
            </span>
          </div>
        </div>
      </div>
    </Fieldset>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Fieldset from 'primevue/fieldset'

const tgPosts = ref([
  {
    id: 1,
    channel: "Технологии и AI",
    text: "OpenAI представила новую модель GPT-5 с улучшенными возможностями...\n\nОсновные нововведения:\n• Улучшенное понимание контекста\n• Поддержка мультимодальности\n• Ускоренная обработка запросов",
    date: new Date('2024-01-15T14:30:00'),
    views: 1542,
    reactions: 89,
    media: null
  },
  {
    id: 2,
    channel: "Дизайн и UX",
    text: "Новые тренды в веб-дизайне на 2024 год:\n\n1. Неоморфизм и стеклянный морфизм\n2. Анимированные интерфейсы\n3. Минимализм с акцентом на типографику",
    date: new Date('2024-01-14T12:15:00'),
    views: 892,
    reactions: 45,
    media: "https://example.com/design-trends.jpg"
  }
])

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isImage = (media) => {
  return media && media.match(/\.(jpg|jpeg|png|gif|webp)$/i)
}
</script>

<style scoped>
.posts-container {
  max-width: 800px;
  margin: 0 auto;
}

.post-content {
  line-height: 1.6;
}

.post-media {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  border: 1px solid var(--surface-border);
}

.media-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--surface-ground);
  border-radius: 6px;
  border: 1px dashed var(--surface-border);
}

.whitespace-pre-wrap {
  white-space: pre-wrap;
  word-break: break-word;
}

.border-top-1 {
  border-top: 1px solid var(--surface-border);
}
</style>