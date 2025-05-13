<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div class="max-w-md w-full bg-white shadow-lg rounded-lg p-6 space-y-6">
        <h2 class="text-2xl font-bold text-center text-gray-800">Регистрация</h2>
  
        <!-- Имя -->
        <div class="space-y-1">
          <label for="name" class="block text-sm font-medium text-gray-700">Имя</label>
          <InputText
            id="name"
            v-model="form.name"
            @blur="v$.name.$touch"
            class="w-full"
            :class="{ 'border-red-500': v$.name.$error }"
          />
          <small v-for="(error, index) in v$.name.$errors" :key="index" class="text-red-500 text-xs">{{ error.$message }}</small>
        </div>
  
        <!-- Email -->
        <div class="space-y-1">
          <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
          <InputText
            id="email"
            v-model="form.email"
            @blur="v$.email.$touch"
            class="w-full"
            :class="{ 'border-red-500': v$.email.$error }"
          />
          <small v-for="(error, index) in v$.email.$errors" :key="index" class="text-red-500 text-xs">{{ error.$message }}</small>
        </div>
  
        <!-- Пароль -->
        <div class="space-y-1">
          <label for="password" class="block text-sm font-medium text-gray-700">Пароль</label>
          <Password
            id="password"
            v-model="form.password"
            @blur="v$.password.$touch"
            toggleMask
            class="w-full"
            :class="{ 'border-red-500': v$.password.$error }"
          />
          <small v-for="(error, index) in v$.password.$errors" :key="index" class="text-red-500 text-xs">{{ error.$message }}</small>
        </div>
  
        <!-- Подтверждение пароля -->
        <div class="space-y-1">
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Подтвердите пароль</label>
          <Password
            id="confirmPassword"
            v-model="form.confirmPassword"
            @blur="v$.confirmPassword.$touch"
            toggleMask
            class="w-full"
            :class="{ 'border-red-500': v$.confirmPassword.$error }"
          />
          <small v-for="(error, index) in v$.confirmPassword.$errors" :key="index" class="text-red-500 text-xs">{{ error.$message }}</small>
        </div>
  
        <!-- Сообщения об ошибках сервера -->
        <div v-if="serverError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {{ serverError }}
        </div>
  
        <!-- Кнопка отправки -->
        <Button
          type="submit"
          label="Зарегистрироваться"
          @click="submitForm"
          class="w-full mt-4"
          :disabled="v$.$invalid || isSubmitting"
          :loading="isSubmitting"
        />
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import useVuelidate from '@vuelidate/core'
  import { required, minLength, email, sameAs } from '@vuelidate/validators'
  import axios from 'axios'
  import { useRouter } from 'vue-router'

  import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

  
  // --- Состояние формы ---
  const form = ref({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  
  const serverError = ref(null)
  const isSubmitting = ref(false)
  
  // --- Валидация ---
  const rules = {
    name: { required, minLength: minLength(2) },
    email: { required, email },
    password: { required, minLength: minLength(6) },
    confirmPassword: { required, 
        sameAsPassword: sameAs(computed(() => form.value.password)) }
  }
  
  const v$ = useVuelidate(rules, form)
  
  // --- Роутер для перенаправления ---
  const router = useRouter()
  
  // --- Отправка формы ---
  const submitForm = async () => {
    const isValid = await v$.value.$validate()
    if (!isValid) return
  
    isSubmitting.value = true
    serverError.value = null
  
    try {
      // Запрос на DRF
      await axios.post('/api/auth/register', {
        username: form.value.name,
        email: form.value.email,
        password: form.value.password
      })
  
      // Перенаправление после успешной регистрации
      await router.push('/login')
    } catch (error) {
      if (error.response?.status === 400) {
        const errors = error.response.data
        if (errors.email) {
          serverError.value = errors.email[0]
        } else if (errors.non_field_errors) {
          serverError.value = errors.non_field_errors[0]
        } else {
          serverError.value = 'Ошибка регистрации'
        }
      } else {
        serverError.value = 'Произошла сетевая ошибка'
      }
    } finally {
      isSubmitting.value = false
    }
  }
  </script>