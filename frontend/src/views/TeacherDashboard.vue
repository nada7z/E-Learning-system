<template>
  <div class="page">
    <div class="page-header flex items-center justify-between">
      <div>
        <h1 class="page-title">Teacher Dashboard</h1>
        <p class="page-sub">Manage your courses and track student performance</p>
      </div>

      <button class="btn btn-primary" type="button" @click="goToCreateCourse">
        + New Course
      </button>
    </div>

    <div class="stat-grid">
      <StatCard :icon="BookOpen" :value="stats.active_courses" label="Active Courses" />

      <StatCard :icon="Users" :value="stats.total_students" label="Total Students" trend-class="trend-up"
        background="#E0F2F1" />

      <StatCard :icon="FileText" :value="stats.pending_grading" label="Pending Grading" background="#FFF3E0" />

      <StatCard :icon="Star" :value="stats.avg_rating || 0" label="Avg Rating" background="#EDE9FE" />

      <StatCard :icon="DollarSign" :value="formatMoney(stats.teacher_revenue)" label="My Revenue"
        trend="80% of paid course sales" trend-class="trend-up" background="#DCFCE7" />
    </div>

    <div class="card mb-6">
      <div class="card-header">
        <span class="card-title">Student Enrollment Trends</span>
        <span class="badge badge-green">Live</span>
      </div>

      <div class="chart-box">
        <canvas ref="enrollCanvas"></canvas>
      </div>
    </div>

    <div class="card mb-6">
      <div class="card-header">
        <span class="card-title">Revenue Trends</span>
        <span class="badge badge-green">80% Share</span>
      </div>

      <div class="chart-box">
        <canvas ref="revenueCanvas"></canvas>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">Your Courses</span>
        <button class="btn btn-ghost btn-sm" @click="$router.push('/courses')">
          Manage All
        </button>
      </div>

      <CourseTable :courses="courses.slice(0, 4)" @navigate="$router.push" />
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'
import StatCard from '../components/StatCard.vue'
import CourseTable from '../components/CourseTable.vue'
import { useRouter } from 'vue-router'
import {
  BookOpen,
  Users,
  FileText,
  Star,
  DollarSign,
} from 'lucide-vue-next'

const emit = defineEmits(['navigate', 'toast'])

const router = useRouter()

const goToCreateCourse = () => {
  console.log('NEW COURSE CLICKED')
  router.push('/create-course')
}

const API_URL = 'http://127.0.0.1:8000/api/dashboard/'

const enrollCanvas = ref(null)
const revenueCanvas = ref(null)
const loading = ref(true)
const error = ref('')

const stats = ref({
  active_courses: 0,
  total_students: 0,
  pending_grading: 0,
  avg_rating: null,
  gross_revenue: 0,
  teacher_revenue: 0,
  platform_fee: 0,
})

const courses = ref([])

const enrollmentTrends = ref({
  labels: [],
  datasets: [],
})

const revenueTrends = ref({
  labels: [],
  data: [],
})

let chart = null
let revenueChart = null

const getAuthHeaders = () => {
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('access') ||
    localStorage.getItem('token')

  return token
    ? {
      Authorization: `Bearer ${token}`,
    }
    : {}
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
    console.log('DASHBOARD COURSES:', data.courses)
    console.log(
      data.courses.map(c => ({
        title: c.title,
        is_published: c.is_published,
        status: c.status,
      }))
    )
    stats.value = {
      ...stats.value,
      ...(data.stats || data),
    }

    courses.value = (data.courses || []).map((course) => {
      const published =
        course.is_published === true ||
        course.is_published === 'true' ||
        course.is_published === 1 ||
        course.is_published === '1'

      return {
        ...course,

        lessons_count: course.lessons_count ?? course.lessons?.length ?? 0,
        duration_hours: course.duration_hours ?? course.duration ?? 0,
        level: course.level || 'Beginner',
        category: course.category || 'Uncategorized',
        teacher_name: course.teacher_name || 'Teacher',
        price: course.is_free ? 0 : Number(course.price ?? 0),

        is_published: published,
        status: published ? 'Published' : 'Draft',
      }
    })

    enrollmentTrends.value = data.enrollment_trends || {
      labels: [],
      datasets: [],
    }

    revenueTrends.value = data.revenue_trends || {
      labels: [],
      data: [],
    }
  } catch (err) {
    console.error(err)

    error.value = err.message || 'Could not load dashboard data.'

    emit('toast', error.value, '⚠️')
  } finally {
    loading.value = false
    await nextTick()
    renderChart()
    renderRevenueChart()
  }
}

const chartColors = [
  '#3D5AFE',
  '#00897B',
  '#F57C00',
  '#7C3AED',
  '#DB2777',
  '#00ACC1',
  '#C62828',
]

const renderChart = () => {
  if (!enrollCanvas.value) return

  chart?.destroy()

  const labels = enrollmentTrends.value.labels?.length
    ? enrollmentTrends.value.labels
    : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

  const sourceDatasets = enrollmentTrends.value.datasets?.length
    ? enrollmentTrends.value.datasets
    : [
      {
        label: 'Enrollments',
        data: [0, 0, 0, 0, 0, 0],
      },
    ]

  chart = new Chart(enrollCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: sourceDatasets.map((dataset, index) => {
        const color = chartColors[index % chartColors.length]

        return {
          label: dataset.label || 'Enrollments',
          data: dataset.data?.length
            ? dataset.data
            : [0, 0, 0, 0, 0, 0],
          borderColor: color,
          backgroundColor: color + '22',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointStyle: 'circle',
        }
      }),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: {
            usePointStyle: true,
            pointStyle: 'circle',
            boxWidth: 10,
            boxHeight: 10,
          },
        },
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: true,
          },
        },
        y: {
          display: true,
          beginAtZero: true,
          suggestedMax: 10,
          ticks: {
            stepSize: 2,
          },
          grid: {
            display: true,
          },
        },
      },
    },
  })
}

const renderRevenueChart = () => {
  if (!revenueCanvas.value) return

  revenueChart?.destroy()

  revenueChart = new Chart(revenueCanvas.value, {
    type: 'line',
    data: {
      labels: revenueTrends.value.labels,
      datasets: [
        {
          label: 'Revenue',
          data: revenueTrends.value.data,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16,185,129,0.1)',
          fill: true,
          tension: 0.4,

          pointStyle: 'circle',
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: {
          display: true,
          labels: {
            usePointStyle: true,
            pointStyle: 'circle',
            boxWidth: 10,
            boxHeight: 10,
          },
        },
      },
    },
  })
}

const formatNumber = (value) =>
  new Intl.NumberFormat().format(Number(value || 0))

const formatMoney = (value) =>
  `$${new Intl.NumberFormat().format(Number(value || 0))}`

onMounted(fetchDashboard)

onBeforeUnmount(() => {
  chart?.destroy()
  revenueChart?.destroy()
})
</script>

<style scoped>
.chart-box {
  position: relative;
  height: 240px;
  width: 100%;
}

.chart-box canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .stat-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>