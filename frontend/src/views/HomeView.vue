<script setup>
import Button from 'primevue/button';
import ToggleButton from 'primevue/togglebutton';
import MessageListArea from '@/components/MessageListArea.vue';
import { ref } from 'vue';

const checked = ref(false);
</script>

<template>
  <div>
    <h1>This is a home page</h1>
    <Button label="Profile" icon="pi pi-user" severity="info" />
    <ToggleButton v-model="checked" class="w-24" onLabel="On" offLabel="Off" />
    <message-list-area />
  </div>
</template>

<style>

</style>
