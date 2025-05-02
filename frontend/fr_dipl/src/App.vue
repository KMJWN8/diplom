<template>
    <header>
      <TopMenu />
    </header>

    <div class="flex flex-grow">
      <SidebarMenu />

      <main class="flex-grow p-5">
        <RouterView />
      </main>
      
    </div>

</template>

<script setup>
import TopMenu from './components/TopMenu.vue'
import SidebarMenu from './components/SidebarMenu.vue'
</script>

<style>

</style>
