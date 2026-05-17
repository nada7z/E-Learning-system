<template>
  <div class="toast-container">
    <div v-for="toast in toasts" :key="toast.id" class="toast">
      <span>{{ toast.icon }}</span>
      <span>{{ toast.msg }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ toasts: { type: Array, required: true } })
</script>
