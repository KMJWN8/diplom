<template>

    <Panel header="Меню" style="width: 220px; min-height: 100vh;">
        <Menubar :model="items" orientation="vertical" class="border-0"/>
    </Panel>
    
</template>

<script setup>

import Panel from 'primevue/panel'
import Menubar from 'primevue/menubar'

const items = [
  { label: 'Главная', icon: 'pi pi-home', command: () => {} },
  { label: 'Профиль', icon: 'pi pi-user', command: () => {/* ... */} },
  { label: 'Настройки', icon: 'pi pi-cog', items: [
    { label: 'Пароль' },
    { label: 'Уведомления' }
  ]}
]
</script>