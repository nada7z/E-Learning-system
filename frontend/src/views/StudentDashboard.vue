<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">
        Good morning, {{ displayName }}!
        <span class="welcome-icon" v-html="icons.sparkles"></span>
      </h1>
      <p class="page-sub">
        You have {{ stats.pending_assignments }} assignments due this week. Keep going!
      </p>
    </div>

    <div class="stat-grid">
      <div v-for="card in statCards" :key="card.label" class="stat-card">
        <div class="stat-icon" :style="{ background: card.background }" v-html="card.icon"></div>
        <div class="stat-value">{{ card.value }}</div>
        <div class="stat-label">{{ card.label }}</div>
        <div :class="card.trendClass">{{ card.trend }}</div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="card">
        <div class="card-header">
          <span class="card-title">Learning Progress</span>
          <span class="badge badge-blue">Last 6 months</span>
        </div>

        <div class="chart-box">
          <canvas ref="progressCanvas"></canvas>
          <div v-if="!hasProgressData" class="empty-chart-message">
            No learning progress yet
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-title">Quiz Scores</span>
        </div>

        <div class="chart-box">
          <canvas ref="quizCanvas"></canvas>
          <div v-if="!hasQuizData" class="empty-chart-message">
            No quizzes yet
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">In-Progress Courses</span>
        <span class="card-action" @click="$emit('navigate', 'courses')">View all →</span>
      </div>

      <div v-if="inProgress.length" class="course-list">
        <div
          v-for="c in inProgress"
          :key="c.id"
          class="course-row hover-surface"
          @click="$emit('navigate', 'course-detail')"
        >
          <div class="course-thumb" :style="{ background: c.color }">
            {{ c.thumb }}
          </div>

          <div class="course-main">
            <div class="course-title">{{ c.title }}</div>
            <div class="course-meta">{{ c.teacher }} · {{ c.lessons }} lessons</div>

            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: c.progress + '%', background: '#3D5AFE' }"
              ></div>
            </div>
          </div>

          <div class="course-progress">
            <div class="course-percent">{{ c.progress }}%</div>
            <div class="course-complete">complete</div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        No courses in progress yet
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'

const emit = defineEmits(['navigate', 'toast'])

const API_URL = import.meta.env.VITE_DASHBOARD_API_URL || 'http://127.0.0.1:8000/api/dashboard/'

const progressCanvas = ref(null)
const quizCanvas = ref(null)

const loading = ref(true)
const error = ref('')
const currentUser = ref(null)

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

const icons = {
  book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/></svg>',

  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',

  file: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>',

  target: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',

  sparkles: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3z"/><path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15z"/></svg>',
}

const getStoredUser = () => {
  const rawUser = localStorage.getItem('user') || localStorage.getItem('auth_user')

  if (!rawUser) return null

  try {
    return JSON.parse(rawUser)
  } catch {
    return null
  }
}

const displayName = computed(() => {
  const user = currentUser.value || getStoredUser() || {}

  const fullName = [user.first_name, user.last_name]
    .filter(Boolean)
    .join(' ')
    .trim()

  return fullName || user.username || user.email?.split('@')[0] || 'Student'
})

const hasProgressData = computed(() => progressChart.value.length > 0)
const hasQuizData = computed(() => quizScores.value.length > 0)

const statCards = computed(() => [
  {
    icon: icons.book,
    value: stats.value.enrolled_courses,
    label: 'Enrolled Courses',
    trend: '↑ 2 this month',
    trendClass: 'trend-up',
    background: '#EEF2FF',
  },
  {
    icon: icons.check,
    value: stats.value.completed_courses,
    label: 'Completed',
    trend: '↑ 1 this week',
    trendClass: 'trend-up',
    background: '#E0F2F1',
  },
  {
    icon: icons.file,
    value: stats.value.pending_assignments,
    label: 'Pending Assignments',
    trend: stats.value.pending_assignments ? 'Due soon' : 'All clear',
    trendClass: stats.value.pending_assignments ? 'trend-dn' : 'trend-up',
    background: '#FFF3E0',
  },
  {
    icon: icons.target,
    value: `${stats.value.avg_quiz_score || 0}%`,
    label: 'Avg Quiz Score',
    trend: hasQuizData.value ? '↑ 5% this week' : 'No quizzes yet',
    trendClass: hasQuizData.value ? 'trend-up' : 'trend-muted',
    background: '#EDE9FE',
  },
])

const getAuthHeaders = () => {
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('access') ||
    localStorage.getItem('token')

  return token
    ? { Authorization: `Bearer ${token}` }
    : {}
}

const fetchDashboard = async () => {
  loading.value = true
  error.value = ''
  currentUser.value = getStoredUser()

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

    currentUser.value = data.user || currentUser.value

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

    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  charts.forEach((chart) => chart.destroy())
  charts = []

  if (!progressCanvas.value || !quizCanvas.value) return

  const progressLabels = hasProgressData.value
    ? progressChart.value.map((item) => item.label)
    : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

  const progressValues = hasProgressData.value
    ? progressChart.value.map((item) => item.value)
    : [null, null, null, null, null, null]

  const quizLabels = hasQuizData.value
    ? quizScores.value.map((item) => item.label)
    : ['Quiz 1', 'Quiz 2', 'Quiz 3']

  const quizValues = hasQuizData.value
    ? quizScores.value.map((item) => item.value)
    : [null, null, null]

  charts = [
    new Chart(progressCanvas.value, {
      type: 'line',
      data: {
        labels: progressLabels,
        datasets: [
          {
            label: 'Progress %',
            data: progressValues,
            borderColor: '#3D5AFE',
            backgroundColor: 'rgba(61,90,254,.1)',
            fill: hasProgressData.value,
            tension: 0.4,
            spanGaps: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: hasProgressData.value },
        },
        scales: {
          x: {
            grid: { display: false },
          },
          y: {
            min: 0,
            max: 100,
            ticks: { stepSize: 25 },
          },
        },
      },
    }),

    new Chart(quizCanvas.value, {
      type: 'bar',
      data: {
        labels: quizLabels,
        datasets: [
          {
            label: 'Score',
            data: quizValues,
            backgroundColor: 'rgba(61,90,254,.8)',
            borderRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: hasQuizData.value },
        },
        scales: {
          x: {
            grid: { display: false },
          },
          y: {
            min: 0,
            max: 100,
            ticks: { stepSize: 25 },
          },
        },
      },
    }),
  ]
}

onMounted(fetchDashboard)

onBeforeUnmount(() => {
  charts.forEach((chart) => chart.destroy())
})
</script>

<style scoped>
.chart-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #e5e1dc);
  border-radius: 14px;
  padding: 24px;
}

.stat-icon,
.welcome-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--accent, #3D5AFE);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  margin-bottom: 14px;
}

.stat-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.welcome-icon {
  width: 28px;
  height: 28px;
  vertical-align: -4px;
}

.welcome-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.stat-value {
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--text, #111827);
  margin-bottom: 8px;
}

.stat-label {
  color: var(--text2, #6b7280);
  font-size: 14px;
  margin-bottom: 10px;
}

.trend-up,
.trend-dn,
.trend-muted {
  font-size: 13px;
  font-weight: 700;
}

.trend-up {
  color: #00897b;
}

.trend-dn {
  color: #e00000;
}

.trend-muted {
  color: var(--text2, #6b7280);
}

.chart-box {
  position: relative;
  height: 220px;
}

.empty-chart-message {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text2, #6b7280);
  font-weight: 600;
  pointer-events: none;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  cursor: pointer;
}

.course-thumb {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.course-main {
  flex: 1;
  min-width: 0;
}

.course-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 4px;
}

.course-meta {
  font-size: 12px;
  color: var(--text2);
  margin-bottom: 8px;
}

.course-progress {
  text-align: right;
  flex-shrink: 0;
}

.course-percent {
  font-weight: 700;
  font-size: 18px;
  color: var(--accent);
}

.course-complete {
  font-size: 12px;
  color: var(--text2);
}

.empty-state {
  padding: 32px;
  text-align: center;
  color: var(--text2, #6b7280);
  font-weight: 600;
  border: 1px dashed var(--border, #e5e1dc);
  border-radius: 12px;
}

@media (max-width: 900px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>