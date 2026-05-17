<template>
  <div class="page">
    <div class="page-header flex items-center justify-between"><div><h1 class="page-title">Platform Overview</h1><p class="page-sub">Complete visibility into your LMS platform</p></div><button class="btn btn-primary btn-sm" @click="$emit('toast', 'Settings opened', '⚙️')">⚙️ Settings</button></div>
    <div class="stat-grid">
      <StatCard icon="👥" value="2,841" label="Total Users" trend="↑ 12.4% this month" trend-class="trend-up" />
      <StatCard icon="📚" value="48" label="Active Courses" trend="↑ 3 new this week" trend-class="trend-up" background="#E0F2F1" />
      <StatCard icon="🎓" value="1,204" label="Completions" trend="↑ 8.2% this month" trend-class="trend-up" background="#EDE9FE" />
      <StatCard icon="💰" value="$147k" label="Revenue (Jul)" trend="↑ 23% vs last month" trend-class="trend-up" background="#FFF3E0" />
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px">
      <div class="card"><div class="card-header"><span class="card-title">Revenue Trend</span></div><div style="height:220px"><canvas ref="revenueCanvas"></canvas></div></div>
      <div class="card"><div class="card-header"><span class="card-title">Course Distribution</span></div><div style="height:220px"><canvas ref="platformCanvas"></canvas></div></div>
    </div>
    <div class="card"><div class="card-header"><span class="card-title">Recent Users</span><button class="btn btn-ghost btn-sm" @click="$emit('navigate', 'users')">View All Users</button></div><UsersTable :users="mockUsers.slice(0,4)" @toast="$emit('toast', $event)" /></div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'
import StatCard from '../components/StatCard.vue'

const emit = defineEmits(['navigate', 'toast'])

const API_URL = import.meta.env.VITE_DASHBOARD_API_URL || '/api/dashboard/'

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

let charts = []

const getAuthHeaders = () => {
  const token = localStorage.getItem('access') || localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchDashboard = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(API_URL, {
      credentials: 'include',
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
      ...(data.stats || data),
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

  const growthLabels = userGrowth.value.map((item) => item.label)
  const growthValues = userGrowth.value.map((item) => item.value)

  const distributionLabels = courseDistribution.value.map((item) => item.label)
  const distributionValues = courseDistribution.value.map((item) => item.value)

  charts = [
    new Chart(userGrowthCanvas.value, {
      type: 'bar',
      data: {
        labels: growthLabels.length ? growthLabels : ['No users'],
        datasets: [
          {
            label: 'Users',
            data: growthValues.length ? growthValues : [0],
            backgroundColor: 'rgba(61,90,254,.85)',
            borderRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    }),

    new Chart(platformCanvas.value, {
      type: 'doughnut',
      data: {
        labels: distributionLabels.length ? distributionLabels : ['No courses'],
        datasets: [
          {
            data: distributionValues.length ? distributionValues : [1],
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
    }),
  ]
}

const formatNumber = (value) => new Intl.NumberFormat().format(Number(value || 0))

const formatDate = (value) => {
  return value ? new Date(value).toLocaleDateString() : '—'
}

onMounted(fetchDashboard)

onBeforeUnmount(() => {
  charts.forEach((chart) => chart.destroy())
})
</script>