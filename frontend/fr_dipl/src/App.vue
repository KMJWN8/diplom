<template>
  <component :is="layout"><RouterView></RouterView></component>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router"
import { computed } from "vue"
import { useRoute } from "vue-router"

import AuthLayout from "@/Layout/AuthLayout.vue"
import MainLayout from "@/Layout/MainLayout.vue"


const route = useRoute()

const layout = computed(() => {
  const layoutName = route.meta.layout
  if (layoutName === "Main") {
    return MainLayout
  } else if (layoutName === "Auth") {
    return AuthLayout
  }
  return null
})

</script>


<style scoped></style>