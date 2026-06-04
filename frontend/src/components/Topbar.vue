<template>
  <header class="topbar">

    <button class="hamburger" @click="$emit('toggle-sidebar')">
      <Menu class="top-icon" />
    </button>

    <div class="topbar-actions">

      <div class="icon-btn" @click="goTo('notifications')" title="Notifications">
        <Bell class="top-icon" />

        <div class="notif-dot" v-if="unreadCount"></div>
      </div>

      <div class="icon-btn" @click="$emit('toggle-dark')" title="Toggle dark mode">
        <Sun v-if="dark" class="top-icon" />

        <Moon v-else class="top-icon" />
      </div>

      <div class="avatar" style="cursor:pointer;background:var(--accent-light);color:var(--accent)"
        @click="$emit('toast', 'Profile page coming soon!')">
        {{ avatarText }}
      </div>

    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

import {
  Menu,
  Search,
  Bell,
  Sun,
  Moon
} from 'lucide-vue-next'

const props = defineProps({
  role: String,
  dark: Boolean,
  unreadCount: Number
})

defineEmits([
  'toggle-sidebar',
  'toggle-dark',
  'navigate',
  'toast'
])

const avatarText = computed(() =>
  props.role === 'student'
    ? 'AS'
    : props.role === 'teacher'
      ? 'TC'
      : 'AD'
)
</script>
