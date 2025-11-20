<script setup>
import DatePicker from 'primevue/datepicker';
import { ref } from "vue";
import VerticalBar from '@/components/VerticalBar.vue';

const date_from = ref();
const date_to = ref();
</script>

<template>
  <h1>This is a dashboard page</h1>
  <div class="card flex flex-wrap justify-center gap-4">
    <DatePicker v-model="date_from" variant="filled" />
    <DatePicker v-model="date_to" variant="filled" />
  </div>
  <VerticalBar />
</template>

<style>

</style>
