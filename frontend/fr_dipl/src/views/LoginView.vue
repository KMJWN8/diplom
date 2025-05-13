<template>
  <div>
    <AuthForm/>
    <Button>
      <RouterLink :to="{name: 'home'}">Router</RouterLink>
    </Button>
  </div>
</template>

<script setup>
  import AuthForm from '@/components/AuthForm.vue'
  import { RouterLink } from 'vue-router'
  import { Button } from 'primevue'
  import { useRouter } from 'vue-router'

const router = useRouter()

</script>

<style>

</style>