<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Users</h1>
        <p class="page-sub">
          Manage students, teachers and administrators
        </p>
      </div>
    </div>

    <div class="filters-row">
      <div class="search-box">
        <span class="search-icon">🔍</span>

        <input v-model="search" type="text" placeholder="Search users..." />
      </div>

      <select v-model="roleFilter">
        <option value="">All Roles</option>
        <option value="student">Student</option>
        <option value="teacher">Teacher</option>
        <option value="admin">Admin</option>
      </select>

      <select v-model="statusFilter">
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>

    <div class="users-card">
      <table class="users-table">
        <thead>
          <tr>
            <th>USER</th>
            <th>ROLE</th>
            <th>COURSES</th>
            <th>JOINED</th>
            <th>STATUS</th>
            <th>ACTIONS</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id">
            <td>
              <div class="user-cell">
                <div class="avatar">
                  {{ initials(user.name) }}
                </div>

                <div>
                  <div class="user-name">
                    {{ user.name }}
                  </div>

                  <div class="user-email">
                    {{ user.email }}
                  </div>
                </div>
              </div>
            </td>

            <td>
              <span class="role-pill" :class="user.role">
                {{ capitalize(user.role) }}
              </span>
            </td>

            <td>
              {{ user.courses_count }}
            </td>

            <td>
              {{ formatDate(user.joined) }}
            </td>

            <td>
              <span class="status-pill" :class="user.status">
                {{ user.status }}
              </span>
            </td>

            <td>
              <div class="action-buttons">
                <button v-if="user.status === 'active' || user.status === 'inactive'" class="suspend-btn"
                  @click="suspendUser(user)">
                  Suspend
                </button>

                <button v-if="user.status === 'active' || user.status === 'inactive'" class="ban-btn"
                  @click="banUser(user)">
                  Ban
                </button>

                <button v-if="user.status === 'suspended' || user.status === 'banned'" class="restore-btn"
                  @click="restoreUser(user)">
                  Restore
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="!loading && !paginatedUsers.length">
            <td colspan="6" class="empty-row">
              No users found
            </td>
          </tr>
        </tbody>
      </table>

      <div class="table-footer">
        <span>
          Showing {{ paginatedUsers.length }}
          of {{ filteredUsers.length }} users
        </span>

        <div class="pagination">
          <button>
            ← Prev
          </button>

          <button class="active-page">
            1
          </button>

          <button>
            Next →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

defineEmits(['toast'])

const API_URL = 'http://localhost:8000/api/dashboard/users/'

const users = ref([])
const loading = ref(false)
const error = ref('')

const search = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

const currentPage = ref(1)
const perPage = 6

const getAuthHeaders = () => {
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('access') ||
    localStorage.getItem('token')

  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchUsers = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(API_URL, {
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error(`Users request failed (${response.status})`)
    }

    users.value = await response.json()
  } catch (err) {
    error.value = err.message || 'Could not load users.'
    users.value = []
  } finally {
    loading.value = false
  }
}

const filteredUsers = computed(() => {
  const q = search.value.toLowerCase().trim()

  return users.value.filter((user) => {
    const matchesSearch =
      !q ||
      user.name?.toLowerCase().includes(q) ||
      user.email?.toLowerCase().includes(q)

    const matchesRole =
      !roleFilter.value || user.role === roleFilter.value

    const matchesStatus =
      !statusFilter.value || user.status === statusFilter.value

    return matchesSearch && matchesRole && matchesStatus
  })
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredUsers.value.length / perPage))
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredUsers.value.slice(start, start + perPage)
})

const showingFrom = computed(() => {
  if (!filteredUsers.value.length) return 0
  return (currentPage.value - 1) * perPage + 1
})

const showingTo = computed(() => {
  return Math.min(currentPage.value * perPage, filteredUsers.value.length)
})

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const initials = (name) => {
  if (!name) return '?'

  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

const capitalize = (value) => {
  if (!value) return ''
  return value.charAt(0).toUpperCase() + value.slice(1)
}

const formatDate = (date) => {
  if (!date) return '—'

  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const userAction = async (user, action, days = null) => {
  const response = await fetch(
    `http://localhost:8000/api/dashboard/users/${user.id}/action/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ action, days }),
    }
  )

  const data = await response.json()

  if (!response.ok) {
    alert(data.detail || 'Action failed')
    return
  }

  await fetchUsers()
}

const suspendUser = (user) => {
  const days = prompt('Suspend for how many days? Example: 1, 2, 7, 30')
  if (!days) return

  userAction(user, 'suspend', Number(days))
}

const banUser = (user) => {
  if (!confirm(`Ban ${user.name}?`)) return
  userAction(user, 'ban')
}

const restoreUser = (user) => {
  userAction(user, 'restore')
}

onMounted(fetchUsers)
</script>

<style scoped>
@import '../assets/UsersView.css';
</style>