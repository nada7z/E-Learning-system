<template>
  <div class="app-layout">
    <div
      class="sidebar-overlay"
      :class="{ show: sidebarOpen }"
      @click="sidebarOpen = false"
    ></div>

    <Sidebar
      :page="page"
      :role="actualRole"
      :dark="dark"
      :unread-count="unreadCount"
      :open="sidebarOpen"
      @navigate="onNavigate"
      @logout="logout"
      @toggle-dark="toggleDark"
    />

    <div class="main-content">
      <Topbar
        :role="actualRole"
        :dark="dark"
        :unread-count="unreadCount"
        @toggle-sidebar="sidebarOpen = !sidebarOpen"
        @toggle-dark="$emit('toggle-dark')"
        @navigate="$emit('navigate', $event)"
        @toast="$emit('toast', $event)"
      />

      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import Sidebar from '../components/Sidebar.vue'
import Topbar from '../components/Topbar.vue'

const router = useRouter()

const props = defineProps({
  page: String,
  role: String,
  dark: Boolean,
  unreadCount: Number
})

const emit = defineEmits([
  'navigate',
  'logout',
  'toggle-dark',
  'toast'
])

const sidebarOpen = ref(false)

const dark = ref(localStorage.getItem('dark') === 'true')

const currentUser = computed(() => {
  const savedUser = localStorage.getItem('user')
  return savedUser
    ? JSON.parse(savedUser)
    : null
})

const actualRole = computed(() => {
  return String(
    props.role ||
    currentUser.value?.role ||
    ''
  ).toLowerCase()
})

function onNavigate(page) {
  sidebarOpen.value = false

  router.push(`/${page}`)
}

const toggleDark = () => {
  dark.value = !dark.value

  document.documentElement.classList.toggle(
    'dark',
    dark.value
  )

  localStorage.setItem(
    'dark',
    dark.value ? 'true' : 'false'
  )
}

onMounted(() => {
  document.documentElement.classList.toggle(
    'dark',
    dark.value
  )
})

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('access')
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('refresh')
  localStorage.removeItem('user')

  router.push('/login')
}
</script>