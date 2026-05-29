<template>
  <div class="page">
    <div class="page-header flex items-center justify-between">
      <div>
        <h1 class="page-title">Notifications</h1>
        <p class="page-sub">{{ unreadCount }} unread notifications</p>
      </div>

      <button class="btn btn-ghost btn-sm" @click="markAllRead">
        Mark all read
      </button>
    </div>

    <div class="card" style="padding:8px">
      <div style="display:flex;gap:8px;padding:8px;border-bottom:1px solid var(--border);margin-bottom:4px">
        <div class="tab" :class="{ active: activeTab === 0 }" @click="activeTab = 0">All</div>
        <div class="tab" :class="{ active: activeTab === 1 }" @click="activeTab = 1">Unread</div>
      </div>

      <div v-if="loading" style="padding:20px;text-align:center;color:var(--text2)">
        Loading notifications...
      </div>

      <div v-else-if="filtered.length === 0" style="padding:20px;text-align:center;color:var(--text2)">
        No notifications found.
      </div>

      <div v-else v-for="n in filtered" :key="n.id" class="notif-item" :class="{ unread: n.unread }"
        @click="openNotification(n)">
        <div
          style="width:44px;height:44px;border-radius:12px;background:var(--surface2);display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0">
          {{ n.icon || '🔔' }}
        </div>

        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
            <span style="font-weight:600;font-size:14px;color:var(--text)">
              {{ n.title }}
            </span>
            <div v-if="n.unread" class="notif-dot2"></div>
          </div>

          <div style="font-size:13px;color:var(--text2);margin-bottom:4px">
            {{ n.msg || n.message }}
          </div>

          <div style="font-size:12px;color:var(--text3)">
            {{ n.time || n.created_at }}
          </div>
        </div>

        <button class="btn btn-ghost btn-sm">View</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['toast'])

const activeTab = ref(0)
const loading = ref(false)
const notifications = ref([])

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json'
  }
})

const unreadCount = computed(() => {
  return notifications.value.filter((n) => n.unread).length
})

const filtered = computed(() => {
  if (activeTab.value === 1) {
    return notifications.value.filter((n) => n.unread)
  }

  return notifications.value
})

async function fetchNotifications() {
  loading.value = true

  try {
    const token = localStorage.getItem('access_token')

    const response = await api.get('notifications/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    notifications.value = response.data
  } catch (error) {
    console.error(error)
    emit('toast', 'Could not load notifications from database', '⚠️')
    notifications.value = []
  } finally {
    loading.value = false
  }
}

async function markAllRead() {
  try {
    const token = localStorage.getItem('access_token')

    await api.patch('notifications/mark_all_read/', {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    notifications.value = notifications.value.map((notification) => ({
      ...notification,
      unread: false,
      is_read: true,
    }))

    window.dispatchEvent(new Event('notifications-updated'))

    emit('toast', 'All notifications marked as read', '✅')
  } catch (error) {
    console.error(error)
    emit('toast', 'Could not mark notifications as read', '⚠️')
  }
}

async function openNotification(notification) {
  try {
    const token = localStorage.getItem('access_token')

    await api.patch(`notifications/${notification.id}/mark_read/`, {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    notification.unread = false
    notification.is_read = true

    emit('toast', 'Notification opened', '🔔')
  } catch (error) {
    console.error(error)
    emit('toast', 'Could not update notification', '⚠️')
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>