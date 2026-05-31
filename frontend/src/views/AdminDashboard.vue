<template>
  <div class="page">
    <div class="page-header flex items-center justify-between">
      <div>
        <h1 class="page-title">Platform Overview</h1>
        <p class="page-sub">Complete visibility into your LMS platform</p>
      </div>
    </div>

    <p v-if="loading">Loading dashboard...</p>
    <p v-if="error" style="color:red">{{ error }}</p>

    <div class="stat-grid">
      <StatCard :icon="Users" :value="formatNumber(stats.total_users)" label="Total Users"
        :trend="`${formatNumber(stats.active_users_today)} active today`" trend-class="trend-up" />

      <StatCard :icon="BookOpen" :value="formatNumber(stats.total_courses)" label="Total Courses"
        :trend="`${formatNumber(stats.total_enrollments)} enrollments`" trend-class="trend-up" background="#E0F2F1" />

      <StatCard :icon="GraduationCap" :value="formatNumber(stats.total_completions)" label="Completions"
        trend="Completed enrollments" trend-class="trend-up" background="#EDE9FE" />

      <StatCard :icon="DollarSign" :value="formatMoney(stats.total_revenue)" label="Revenue"
        trend="Paid courses revenue" trend-class="trend-up" background="#FFF3E0" />
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px">
      <div class="card">
        <div class="card-header">
          <span class="card-title">User Growth</span>
        </div>
        <div style="height:220px">
          <canvas ref="userGrowthCanvas"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-title">Course Distribution</span>
        </div>
        <div style="height:220px">
          <canvas ref="platformCanvas"></canvas>
        </div>
      </div>
    </div>

    <div class="card users-card">
      <div class="card-header">
        <span class="card-title">Recent Users</span>
        <button class="btn btn-ghost btn-sm" @click="$emit('navigate', 'users')">
          View All Users
        </button>
      </div>

      <div class="users-table-wrap">
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
            <tr v-for="user in recentUsers" :key="user.id">
              <td>
                <div class="user-cell">
                  <div class="avatar">
                    {{ initials(user.name || user.email) }}
                  </div>

                  <div>
                    <strong>{{ user.name || 'No name' }}</strong>
                    <p>{{ user.email }}</p>
                  </div>
                </div>
              </td>

              <td>
                <span class="role-badge" :class="user.role">
                  {{ user.role }}
                </span>
              </td>

              <td>{{ user.courses_count || 0 }}</td>

              <td>{{ formatDate(user.joined) }}</td>

              <td>
                <span class="status-badge">active</span>
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

            <tr v-if="!recentUsers.length && !loading">
              <td colspan="6" class="empty-row">No users found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'
import StatCard from '../components/StatCard.vue'
import {
  Users,
  BookOpen,
  GraduationCap,
  DollarSign,
} from 'lucide-vue-next'

const emit = defineEmits(['navigate', 'toast'])

const API_URL = 'http://localhost:8000/api/dashboard/'

const userGrowthCanvas = ref(null)
const platformCanvas = ref(null)

const loading = ref(true)
const error = ref('')

const stats = ref({
  total_users: 0,
  total_courses: 0,
  total_enrollments: 0,
  total_completions: 0,
  active_users_today: 0,
  total_revenue: 0,
})

const userGrowth = ref([])
const courseDistribution = ref([])
const recentUsers = ref([])

const initials = (value) => {
  if (!value) return '?'

  return value
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

let charts = []

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchDashboard = async () => {
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
      throw new Error(`Dashboard request failed (${response.status})`)
    }

    const data = await response.json()

    stats.value = {
      ...stats.value,
      ...(data.stats || {}),
    }

    userGrowth.value = data.user_growth || []
    courseDistribution.value = data.course_distribution || []
    recentUsers.value = data.recent_users || []

    await nextTick()
    renderCharts()
  } catch (err) {
    error.value = err.message || 'Could not load dashboard data.'
    emit('toast', error.value, '⚠️')
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  charts.forEach((chart) => chart.destroy())
  charts = []

  if (userGrowthCanvas.value) {
    charts.push(
      new Chart(userGrowthCanvas.value, {
        type: 'bar',
        data: {
          labels: userGrowth.value.length
            ? userGrowth.value.map((item) => item.label)
            : ['No users'],
          datasets: [
            {
              label: 'Users',
              data: userGrowth.value.length
                ? userGrowth.value.map((item) => item.value)
                : [0],
              backgroundColor: 'rgba(61,90,254,.85)',
              borderRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
        },
      })
    )
  }

  if (platformCanvas.value) {
    charts.push(
      new Chart(platformCanvas.value, {
        type: 'doughnut',
        data: {
          labels: courseDistribution.value.length
            ? courseDistribution.value.map((item) => item.label)
            : ['No courses'],
          datasets: [
            {
              data: courseDistribution.value.length
                ? courseDistribution.value.map((item) => item.value)
                : [1],
              backgroundColor: [
                '#3D5AFE',
                '#DB2777',
                '#00897B',
                '#7C3AED',
                '#F57C00',
                '#00BCD4',
              ],
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '68%',
        },
      })
    )
  }
}

const formatNumber = (value) => {
  return new Intl.NumberFormat().format(Number(value || 0))
}

const formatMoney = (value) => {
  return `$${new Intl.NumberFormat().format(Number(value || 0))}`
}

const formatDate = (value) => {
  return value ? new Date(value).toLocaleDateString() : '—'
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

onMounted(fetchDashboard)

onBeforeUnmount(() => {
  charts.forEach((chart) => chart.destroy())
})
</script>

<style scoped>
@import '../assets/AdminDashboardView.css';
</style>

<style scoped>
@import '../assets/UsersView.css';
</style>