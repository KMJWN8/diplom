<template>
  <div class="card">
      <Editor v-model="value" editorStyle="height: 1000px; width: 794px" />
  </div>
</template>

<script setup>
import Editor from "primevue/editor";
import { ref } from "vue";

const value = ref('')
</script>

<style scoped>
.card {
  max-width: 800px;
  margin: auto;
}
</style>
