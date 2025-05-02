<template>
    <Menubar 
      :model="items" 
      class="bg-sky-400"
      header="Header"
    >
    </Menubar>
</template>

<script setup>

import Menubar from 'primevue/menubar'

import { useRouter } from 'vue-router'

const router = useRouter()

const items = [
  {
    label: 'Home',
    icon: 'pi pi-home',
    command: () => { router.push('/')}
  },
  {
    label: 'Account',
    icon: 'pi pi-check',
    items: [
        {
            label: 'Login',
            icon: 'pi pi-user',
            command: () => { router.push('/login')}
        },
        {
            label: 'Register',
            icon: 'pi pi-check',
            command: () => { router.push('/register')}
        }
    ]
  }
]

</script>
