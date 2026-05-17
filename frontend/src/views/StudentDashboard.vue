<template>
  <div class="page">
    <div class="page-header"><h1 class="page-title">Good morning, Alex! 👋</h1><p class="page-sub">You have 3 assignments due this week. Keep going!</p></div>
    <div class="stat-grid">
      <StatCard icon="📚" :value="stats.enrolled_courses" label="Enrolled Courses" trend="↑ 2 this month" trend-class="trend-up" />
      <StatCard icon="✅" :value="stats.completed_courses" label="Completed" trend="↑ 1 this week" trend-class="trend-up" background="#E0F2F1" />
      <StatCard icon="📝" :value="stats.pending_assignments" label="Pending Assignments" trend="Due soon" trend-class="trend-dn" background="#FFF3E0" />
      <StatCard icon="⚡" :value="stats.avg_quiz_score" label="Avg Quiz Score" trend="↑ 5% this week" trend-class="trend-up" background="#EDE9FE" />
    </div>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:24px">
      <div class="card"><div class="card-header"><span class="card-title">Learning Progress</span><span class="badge badge-blue">Last 6 months</span></div><div style="height:220px"><canvas ref="progressCanvas"></canvas></div></div>
      <div class="card"><div class="card-header"><span class="card-title">Quiz Scores</span></div><div style="height:220px"><canvas ref="quizCanvas"></canvas></div></div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">In-Progress Courses</span><span class="card-action" @click="$emit('navigate', 'courses')">View all →</span></div>
      <div style="display:flex;flex-direction:column;gap:16px">
        <div v-for="c in inProgress" :key="c.id" style="display:flex;align-items:center;gap:16px;padding:14px;border-radius:12px;border:1px solid var(--border);cursor:pointer" class="hover-surface" @click="$emit('navigate', 'course-detail')">
          <div style="width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0" :style="{ background: c.color }">{{ c.thumb }}</div>
          <div style="flex:1;min-width:0"><div style="font-weight:600;font-size:14px;color:var(--text);margin-bottom:4px">{{ c.title }}</div><div style="font-size:12px;color:var(--text2);margin-bottom:8px">{{ c.teacher }} · {{ c.lessons }} lessons</div><div class="progress-bar"><div class="progress-fill" :style="{ width: c.progress + '%', background: '#3D5AFE' }"></div></div></div>
          <div style="text-align:right;flex-shrink:0"><div style="font-weight:700;font-size:18px;color:var(--accent)">{{ c.progress }}%</div><div style="font-size:12px;color:var(--text2)">complete</div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'
import StatCard from '../components/StatCard.vue'

const emit = defineEmits(['navigate', 'toast'])

const API_URL = import.meta.env.VITE_DASHBOARD_API_URL || '/api/dashboard/'

const progressCanvas = ref(null)
const quizCanvas = ref(null)

const loading = ref(true)
const error = ref('')

const stats = ref({
  enrolled_courses: 0,
  completed_courses: 0,
  pending_assignments: 0,
  avg_quiz_score: 0,
  progress: 0,
})

const inProgress = ref([])
const progressChart = ref([])
const quizScores = ref([])

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

    inProgress.value = data.in_progress_courses || []
    progressChart.value = data.progress_chart || []
    quizScores.value = data.quiz_scores || []

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

  const progressLabels = progressChart.value.map((item) => item.label)
  const progressValues = progressChart.value.map((item) => item.value)

  const quizLabels = quizScores.value.map((item) => item.label)
  const quizValues = quizScores.value.map((item) => item.value)

  charts = [
    new Chart(progressCanvas.value, {
      type: 'line',
      data: {
        labels: progressLabels.length ? progressLabels : ['Progress'],
        datasets: [
          {
            label: 'Progress %',
            data: progressValues.length ? progressValues : [stats.value.progress || 0],
            borderColor: '#3D5AFE',
            backgroundColor: 'rgba(61,90,254,.1)',
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            max: 100,
            beginAtZero: true,
          },
        },
      },
    }),

    new Chart(quizCanvas.value, {
      type: 'bar',
      data: {
        labels: quizLabels.length ? quizLabels : ['No quizzes'],
        datasets: [
          {
            label: 'Score',
            data: quizValues.length ? quizValues : [0],
            backgroundColor: 'rgba(61,90,254,.8)',
            borderRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            max: 100,
            beginAtZero: true,
          },
        },
      },
    }),
  ]
}

const formatNumber = (value) => new Intl.NumberFormat().format(Number(value || 0))

onMounted(fetchDashboard)

onBeforeUnmount(() => {
  charts.forEach((chart) => chart.destroy())
})
</script>