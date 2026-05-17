<template>
  <div class="stat-card">
    <div class="stat-icon" :style="{ background }"><component :is="icon" class="icon" /></div>
    <div class="stat-val">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="trend" class="stat-trend" :class="trendClass">{{ trend }}</div>
  </div>
</template>

<script setup>
defineProps({ icon: String, value: [String, Number], label: String, trend: String, trendClass: String, background: { type: String, default: '#EEF1FF' } })
</script>
