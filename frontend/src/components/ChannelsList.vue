<template>
  <div class="channels-container">
    <!-- Заголовок -->
    <div class="section-header">
      <h2>Каналы</h2>
      <div class="header-actions">
        <button 
          class="btn btn-outline btn-sm" 
          @click="refreshChannels"
          :disabled="loading"
        >
          <span v-if="loading">Обновление...</span>
          <span v-else>Обновить</span>
        </button>
        <button 
          class="btn btn-primary btn-sm" 
          @click="showAddModal = true"
        >
          <span>+ Добавить канал</span>
        </button>
      </div>
    </div>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка каналов...</p>
    </div>

    <!-- Состояние ошибки -->
    <div v-if="error && !loading" class="error-state card">
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <p class="error-message">{{ error }}</p>
        <button class="btn btn-primary" @click="fetchChannels">
          Попробовать снова
        </button>
      </div>
    </div>

    <!-- Список каналов -->
    <div v-if="!loading && !error && channels.length > 0" class="channels-grid">
      <div 
        v-for="channel in channels" 
        :key="channel.id" 
        class="channel-card card"
      >
        <div class="channel-header">
          <div class="channel-avatar">
            {{ getChannelInitials(channel.title) }}
          </div>
          <div class="channel-info">
            <h3 class="channel-title">{{ channel.title }}</h3>
            <div class="channel-meta">
              <span class="channel-username">
                @{{ channel.username }}
              </span>
              <span class="channel-id">
                ID: {{ channel.channel_id }}
              </span>
            </div>
          </div>
        </div>

        <div class="channel-body">
          <div class="channel-stats">
            <div class="stat-item">
              <span class="stat-label">Обновлен:</span>
              <span class="stat-value">
                {{ formatDate(channel.updated_at) }}
              </span>
            </div>
          </div>
        </div>

        <div class="channel-footer">
          <div class="channel-actions">
            <button 
              class="btn btn-text btn-sm delete-btn" 
              @click="confirmDeleteChannel(channel)"
              :disabled="actionLoading[channel.id]"
            >
              <span v-if="actionLoading[channel.id]">...</span>
              <span v-else>Удалить</span>
            </button>
          </div>
          <div class="channel-date">
            Добавлен: {{ formatDate(channel.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Пустое состояние -->
    <div v-if="!loading && !error && channels.length === 0" class="empty-state card">
      <div class="empty-content">
        <span class="empty-icon">📭</span>
        <h3>Каналы не найдены</h3>
        <p>В системе пока нет добавленных каналов</p>
        <button 
          class="btn btn-primary" 
          @click="showAddModal = true"
        >
          Добавить первый канал
        </button>
      </div>
    </div>

    <!-- Модальное окно добавления канала -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content card">
        <div class="modal-header">
          <h3>Добавить канал</h3>
          <button class="modal-close" @click="closeAddModal">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="addChannel">
            <div class="form-group">
              <label for="channelId" class="form-label">ID канала или ссылка *</label>
              <input 
                id="channelId"
                v-model="newChannel.id"
                type="text" 
                class="form-input"
                placeholder="@username или https://t.me/username"
                required
                :disabled="addLoading"
              />
              <small class="form-hint">
                Введите ID канала (например: @channel_username) или полную ссылку
              </small>
            </div>

            <div class="form-actions">
              <button 
                type="button" 
                class="btn btn-outline"
                @click="closeAddModal"
                :disabled="addLoading"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="!newChannel.id || addLoading"
              >
                <span v-if="addLoading">Добавление...</span>
                <span v-else>Добавить канал</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content card">
        <div class="modal-header">
          <h3>Подтверждение удаления</h3>
          <button class="modal-close" @click="cancelDelete">×</button>
        </div>
        
        <div class="modal-body">
          <p>Вы действительно хотите удалить канал <strong>{{ channelToDelete?.title }}</strong>?</p>
          <p class="text-muted">Это действие нельзя отменить.</p>
          
          <div class="form-actions">
            <button 
              type="button" 
              class="btn btn-outline"
              @click="cancelDelete"
              :disabled="deleteLoading"
            >
              Отмена
            </button>
            <button 
              type="button" 
              class="btn btn-error"
              @click="deleteChannel"
              :disabled="deleteLoading"
            >
              <span v-if="deleteLoading">Удаление...</span>
              <span v-else>Удалить</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { postsApi } from '@/api/endpoints'

const channels = ref([])
const loading = ref(false)
const error = ref(null)
const addLoading = ref(false)
const deleteLoading = ref(false)
const actionLoading = ref({})

// Модальные окна
const showAddModal = ref(false)
const showDeleteModal = ref(false)
const channelToDelete = ref(null)

// Новый канал
const newChannel = ref({
  id: ''
})

// Получение списка каналов
const fetchChannels = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await postsApi.getChannels()
    channels.value = response.data || []
  } catch (err) {
    console.error('Ошибка при загрузке каналов:', err)
    error.value = err.response?.data?.message || 'Не удалось загрузить каналы'
  } finally {
    loading.value = false
  }
}

// Обновление каналов
const refreshChannels = () => {
  fetchChannels()
}

// Добавление канала
const addChannel = async () => {
  if (!newChannel.value.id.trim()) return
  
  addLoading.value = true
  try {
    // Очищаем входные данные
    let channelIdentifier = newChannel.value.id.trim()
    
    const response = await postsApi.addChannel(channelIdentifier)
    channels.value.unshift(response.data)
    
    // Очищаем форму и закрываем модалку
    newChannel.value.id = ''
    showAddModal.value = false

    // Показываем сообщение об успехе
    alert(`Канал @${channelIdentifier} успешно добавлен!`)
    
  } catch (err) {
    console.error('Ошибка при добавлении канала:', err)
    error.value = err.response?.data?.message || 'Не удалось добавить канал'
  } finally {
    addLoading.value = false
  }
}

// Подтверждение удаления
const confirmDeleteChannel = (channel) => {
  channelToDelete.value = channel
  showDeleteModal.value = true
}

// Удаление канала
const deleteChannel = async () => {
  if (!channelToDelete.value) return
  
  deleteLoading.value = true
  try {

    await postsApi.deleteChannel(channelToDelete.value.channel_id)
    
    // Удаляем канал из списка
    channels.value = channels.value.filter(
      channel => channel.channel_id !== channelToDelete.value.channel_id
    )
    
    // Закрываем модалку
    cancelDelete()
  } finally {
    deleteLoading.value = false
  }
}

// Отмена удаления
const cancelDelete = () => {
  channelToDelete.value = null
  showDeleteModal.value = false
}

// Закрытие модалки добавления
const closeAddModal = () => {
  if (!addLoading.value) {
    showAddModal.value = false
    newChannel.value.id = ''
  }
}

// Получение инициалов для аватара
const getChannelInitials = (title) => {
  if (!title) return '??'
  const words = title.split(' ')
  if (words.length === 1) return words[0].charAt(0).toUpperCase()
  return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase()
}

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return 'Нет данных'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch (e) {
    return dateString
  }
}

// Форматирование числа (подписчиков)
const formatNumber = (num) => {
  if (!num) return 'Не указано'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

// Загрузка каналов при монтировании компонента
onMounted(() => {
  fetchChannels()
})
</script>

<style scoped>
.channels-container {
  width: 100%;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.section-header h2 {
  margin-bottom: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

/* Загрузка */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  gap: var(--space-4);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--gray-200);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Ошибка */
.error-state {
  border-color: var(--error-color);
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-8);
  gap: var(--space-4);
}

.error-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
}

.error-message {
  color: var(--error-color);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--space-6);
}

/* Сетка каналов */
.channels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

@media (max-width: 768px) {
  .channels-grid {
    grid-template-columns: 1fr;
  }
}

/* Карточка канала */
.channel-card {
  display: flex;
  flex-direction: column;
  transition: all var(--transition-normal);
}

.channel-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.channel-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  border-bottom: 1px solid var(--gray-200);
}

.channel-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  color: var(--white);
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.channel-info {
  flex: 1;
  min-width: 0;
}

.channel-title {
  font-size: var(--font-size-lg);
  margin-bottom: var(--space-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.channel-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  font-size: var(--font-size-sm);
  color: var(--gray-500);
}

.channel-body {
  padding: var(--space-6);
  flex: 1;
}

.channel-stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: var(--gray-600);
  font-size: var(--font-size-sm);
}

.stat-value {
  font-weight: var(--font-weight-medium);
  color: var(--gray-800);
}

.channel-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--gray-200);
}

.channel-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--space-3);
}

.channel-date {
  font-size: var(--font-size-xs);
  color: var(--gray-500);
  text-align: right;
}

/* Кнопка удаления */
.delete-btn {
  background: none;
  border: none;
  color: var(--error-color);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.delete-btn:hover:not(:disabled) {
  text-decoration: underline;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--border-radius-sm);
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Пустое состояние */
.empty-state {
  border: 2px dashed var(--gray-300);
  background-color: var(--gray-50);
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-12) var(--space-8);
  gap: var(--space-4);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

.empty-content h3 {
  color: var(--gray-600);
}

.empty-content p {
  color: var(--gray-500);
}

/* Модальные окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
  animation: fadeIn var(--transition-fast);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn var(--transition-normal);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-bottom: 1px solid var(--gray-200);
}

.modal-header h3 {
  margin-bottom: 0;
  font-size: var(--font-size-xl);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--gray-500);
  padding: var(--space-2);
  line-height: 1;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
}

.modal-close:hover {
  color: var(--gray-700);
  background-color: var(--gray-100);
}

.modal-body {
  padding: var(--space-6);
}

/* Форма в модалке */
.form-group {
  margin-bottom: var(--space-6);
}

.form-label {
  display: block;
  margin-bottom: var(--space-2);
  font-weight: var(--font-weight-medium);
  color: var(--gray-700);
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--gray-300);
  border-radius: var(--border-radius);
  background-color: var(--white);
  transition: all var(--transition-fast);
  font-size: var(--font-size-base);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input:disabled {
  background-color: var(--gray-100);
  color: var(--gray-500);
  cursor: not-allowed;
}

.form-hint {
  display: block;
  margin-top: var(--space-2);
  color: var(--gray-500);
  font-size: var(--font-size-sm);
}

.form-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: flex-end;
  margin-top: var(--space-6);
}

/* Кнопка ошибки */
.btn-error {
  background-color: var(--error-color);
  color: var(--white);
  border: none;
}

.btn-error:hover:not(:disabled) {
  background-color: #dc2626;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-error:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Текст ошибки */
.text-muted {
  color: var(--gray-500);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-4);
}

/* Адаптивность */
@media (max-width: 768px) {
  .channels-container {
    padding: 0 var(--space-3);
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .modal-content {
    max-width: 100%;
    margin: var(--space-4);
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .channels-grid {
    gap: var(--space-4);
  }
  
  .channel-header,
  .channel-body,
  .channel-footer {
    padding: var(--space-4);
  }
  
  .modal-header,
  .modal-body {
    padding: var(--space-4);
  }
  
  .header-actions {
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .header-actions .btn {
    width: 100%;
  }
}
</style>