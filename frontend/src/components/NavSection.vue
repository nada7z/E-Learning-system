<template>
  <div class="nav-section">
    <div class="nav-label">{{ label }}</div>
    <div v-for="item in items" :key="item.label" class="nav-item" :class="{ active: item.page && page === item.page }" @click="item.page && $emit('navigate', item.page)">
      <component :is="item.icon" class="nav-icon" />{{ item.label }}
    </div>
  </div>
</template>

<script setup>
defineProps({ label: String, items: Array, page: String })
defineEmits(['navigate'])
</script>
