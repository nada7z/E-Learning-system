<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Course Performance</h1>
        <p class="page-sub">Analytics and insights across all your published courses</p>
      </div>
      <div class="header-actions">
        <select v-model="selectedCourseId" class="input filter-select">
          <option value="">All courses</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
        </select>
        <button class="btn btn-ghost btn-sm" @click="showToast('Report exported 📥')">↓ Export</button>
      </div>
    </div>

    <!-- KPI cards -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background:#EEF1FF">📚</div>
        <div class="stat-val">{{ kpi.totalCourses }}</div>
        <div class="stat-label">Published Courses</div>
        <div class="stat-trend trend-up">↑ 1 this month</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#E0F2F1">👥</div>
        <div class="stat-val">{{ kpi.totalEnrolled }}</div>
        <div class="stat-label">Total Enrolled</div>
        <div class="stat-trend trend-up">↑ 48 this month</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#EDE9FE">⭐</div>
        <div class="stat-val">{{ kpi.avgRating }}</div>
        <div class="stat-label">Avg Rating</div>
        <div class="stat-trend trend-up">↑ 0.2 this quarter</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFF3E0">🎓</div>
        <div class="stat-val">{{ kpi.avgCompletion }}%</div>
        <div class="stat-label">Avg Completion</div>
        <div class="stat-trend trend-dn">↓ 2.1% this week</div>
      </div>
    </div>

    <!-- Enrollment trend + Completion rate -->
    <div class="charts-row">
      <div class="card" style="flex:1.6">
        <div class="card-header">
          <span class="card-title">Enrollment Over Time</span>
          <div class="legend-inline">
            <span v-for="c in courses" :key="c.id" class="legend-item-inline">
              <span class="legend-dot-sm" :style="{ background: c.color }"></span>{{ c.shortTitle }}
            </span>
          </div>
        </div>
        <div class="chart-wrap">
          <canvas ref="enrollChart" aria-label="Line chart of weekly enrollment per course"></canvas>
        </div>
      </div>

      <div class="card" style="flex:1">
        <div class="card-header">
          <span class="card-title">Completion Rate</span>
          <span class="badge badge-blue">Per course</span>
        </div>
        <div class="chart-wrap">
          <canvas ref="completionChart" aria-label="Horizontal bar chart of course completion rates"></canvas>
        </div>
      </div>
    </div>

    <!-- Rating distribution + Quiz pass rates -->
    <div class="charts-row">
      <div class="card" style="flex:1">
        <div class="card-header">
          <span class="card-title">Rating Distribution</span>
          <span class="badge badge-purple">All courses</span>
        </div>
        <div class="chart-wrap">
          <canvas ref="ratingChart" aria-label="Bar chart of student ratings from 1 to 5 stars"></canvas>
        </div>
      </div>

      <div class="card" style="flex:1">
        <div class="card-header">
          <span class="card-title">Quiz Pass Rates</span>
          <span class="badge badge-green">By course</span>
        </div>
        <div class="chart-wrap">
          <canvas ref="passRateChart" aria-label="Bar chart of quiz pass rates per course"></canvas>
        </div>
      </div>
    </div>

    <!-- Course comparison table -->
    <div class="card mt-4">
      <div class="card-header">
        <span class="card-title">Course Breakdown</span>
        <div style="display:flex;gap:8px">
          <select v-model="tableSortBy" class="input filter-select" style="min-width:160px">
            <option value="enrolled">Sort: Enrolled</option>
            <option value="completion">Sort: Completion</option>
            <option value="rating">Sort: Rating</option>
            <option value="pass_rate">Sort: Pass Rate</option>
          </select>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Course</th>
              <th>Enrolled</th>
              <th>Completion</th>
              <th>Avg Quiz Score</th>
              <th>Pass Rate</th>
              <th>Rating</th>
              <th>Revenue</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in sortedCourses" :key="c.id" @click="drillDown(c)" style="cursor:pointer">
              <td>
                <div class="course-cell">
                  <div class="course-thumb" :style="{ background: c.thumbBg }">{{ c.thumb }}</div>
                  <div>
                    <div class="course-name">{{ c.title }}</div>
                    <div class="course-meta">{{ c.lessons }} lessons · {{ c.level }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="fw-600">{{ c.enrolled }}</span>
                <span class="text-muted text-sm"> students</span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: c.completion + '%', background: progressColor(c.completion) }"></div>
                  </div>
                  <span class="progress-pct">{{ c.completion }}%</span>
                </div>
              </td>
              <td>
                <span class="score-chip" :class="scoreClass(c.avg_quiz_score)">{{ c.avg_quiz_score }}%</span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: c.pass_rate + '%', background: passColor(c.pass_rate) }"></div>
                  </div>
                  <span class="progress-pct">{{ c.pass_rate }}%</span>
                </div>
              </td>
              <td>
                <div class="rating-cell">
                  <span class="rating-star">★</span>
                  <span class="fw-600">{{ c.rating }}</span>
                  <span class="text-muted text-sm">({{ c.reviews }})</span>
                </div>
              </td>
              <td>
                <span v-if="c.is_free" class="badge badge-gray">Free</span>
                <span v-else class="fw-600">${{ c.revenue.toLocaleString() }}</span>
              </td>
              <td>
                <span class="trend-chip" :class="c.trend > 0 ? 'trend-up-chip' : 'trend-dn-chip'">
                  {{ c.trend > 0 ? '↑' : '↓' }} {{ Math.abs(c.trend) }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Drill-down side panel -->
    <Transition name="slide-right">
      <div v-if="panel.open" class="panel-overlay" @click.self="panel.open = false">
        <div class="side-panel">
          <div class="panel-header">
            <div class="panel-course-info">
              <div class="course-thumb-lg" :style="{ background: panel.course?.thumbBg }">
                {{ panel.course?.thumb }}
              </div>
              <div>
                <div class="panel-title">{{ panel.course?.title }}</div>
                <div class="text-muted text-sm">{{ panel.course?.level }} · {{ panel.course?.lessons }} lessons</div>
              </div>
            </div>
            <button class="icon-btn" @click="panel.open = false">✕</button>
          </div>

          <div class="panel-body">
            <!-- KPI strip -->
            <div class="panel-kpi-row">
              <div class="panel-kpi">
                <div class="panel-kpi-val">{{ panel.course?.enrolled }}</div>
                <div class="panel-kpi-label">Enrolled</div>
              </div>
              <div class="panel-kpi">
                <div class="panel-kpi-val">{{ panel.course?.completion }}%</div>
                <div class="panel-kpi-label">Completed</div>
              </div>
              <div class="panel-kpi">
                <div class="panel-kpi-val">★ {{ panel.course?.rating }}</div>
                <div class="panel-kpi-label">Rating</div>
              </div>
              <div class="panel-kpi">
                <div class="panel-kpi-val">{{ panel.course?.pass_rate }}%</div>
                <div class="panel-kpi-label">Pass rate</div>
              </div>
            </div>

            <!-- Weekly enrollments -->
            <div class="panel-section">
              <div class="panel-section-title">Weekly enrollments</div>
              <div class="chart-wrap-sm">
                <canvas ref="panelChart" aria-label="Line chart of weekly enrollments for selected course"></canvas>
              </div>
            </div>

            <!-- Lesson engagement -->
            <div class="panel-section">
              <div class="panel-section-title">Lesson completion</div>
              <div class="lesson-bars">
                <div v-for="(l, i) in panel.lessons" :key="i" class="lesson-bar-row">
                  <span class="lesson-bar-label">{{ l.title }}</span>
                  <div class="lesson-bar-track">
                    <div class="lesson-bar-fill" :style="{ width: l.pct + '%', background: progressColor(l.pct) }"></div>
                  </div>
                  <span class="lesson-bar-pct">{{ l.pct }}%</span>
                </div>
              </div>
            </div>

            <!-- Drop-off point -->
            <div class="panel-section">
              <div class="panel-section-title">Student funnel</div>
              <div class="funnel">
                <div v-for="(f, i) in panel.funnel" :key="i" class="funnel-row">
                  <div class="funnel-bar-wrap">
                    <div class="funnel-label">{{ f.label }}</div>
                    <div class="funnel-track">
                      <div class="funnel-fill" :style="{ width: f.pct + '%', background: f.color }"></div>
                    </div>
                  </div>
                  <span class="funnel-pct">{{ f.pct }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.visible" class="toast">{{ toast.message }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import axios from 'axios'

const enrollChart = ref(null)
const completionChart = ref(null)
const ratingChart = ref(null)
const passRateChart = ref(null)
const panelChart = ref(null)

let chartInstances = {}
let panelChartInst = null

const courses = ref([])
const quizzes = ref([])
const attempts = ref([])
const assignments = ref([])
const submissions = ref([])

const selectedCourseId = ref('')
const tableSortBy = ref('enrolled')
const toast = reactive({ visible: false, message: '' })
const panel = reactive({ open: false, course: null, lessons: [], funnel: [] })

function authHeaders() {
  const token = localStorage.getItem('access_token')

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

const filteredCourses = computed(() => {
  if (!selectedCourseId.value) return courses.value

  return courses.value.filter(
    (course) => Number(course.id) === Number(selectedCourseId.value)
  )
})

const kpi = computed(() => {
  const list = filteredCourses.value

  if (!list.length) {
    return {
      totalCourses: 0,
      totalEnrolled: 0,
      avgRating: 'N/A',
      avgCompletion: 0,
    }
  }

  return {
    totalCourses: list.length,
    totalEnrolled: list.reduce((sum, c) => sum + c.enrolled, 0),
    avgRating: 'N/A',
    avgCompletion: Math.round(
      list.reduce((sum, c) => sum + c.completion, 0) / list.length
    ),
  }
})

const sortedCourses = computed(() => {
  const key = tableSortBy.value

  return [...filteredCourses.value].sort((a, b) => {
    return Number(b[key] || 0) - Number(a[key] || 0)
  })
})

function colorFor(index) {
  return [
    '#3D5AFE',
    '#00897B',
    '#7C3AED',
    '#DB2777',
    '#F57C00',
    '#C62828',
  ][index % 6]
}

function thumbFor(index) {
  return ['📚', '💻', '📊', '🎨', '🤖', '☁️'][index % 6]
}

function bgFor(index) {
  return [
    '#EEF1FF',
    '#E0F2F1',
    '#EDE9FE',
    '#FCE7F3',
    '#FFF3E0',
    '#FFEBEE',
  ][index % 6]
}

function progressColor(p) {
  return p >= 70 ? '#00897B' : p >= 40 ? '#3D5AFE' : '#F57C00'
}

function passColor(p) {
  return p >= 70 ? '#00897B' : p >= 50 ? '#F57C00' : '#C62828'
}

function scoreClass(s) {
  return s >= 75 ? 'score-high' : s >= 50 ? 'score-mid' : 'score-low'
}

function showToast(msg) {
  toast.message = msg
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 2600)
}

function getCourseStats(course, index) {
  const courseQuizzes = quizzes.value.filter(
    (quiz) => Number(quiz.course) === Number(course.id)
  )

  const courseQuizIds = courseQuizzes.map((quiz) => Number(quiz.id))

  const courseAttempts = attempts.value.filter((attempt) =>
    courseQuizIds.includes(Number(attempt.quiz_id || attempt.quiz))
  )

  const courseAssignments = assignments.value.filter(
    (assignment) => Number(assignment.course) === Number(course.id)
  )

  const courseAssignmentIds = courseAssignments.map((assignment) =>
    Number(assignment.id)
  )

  const courseSubmissions = submissions.value.filter((submission) =>
    courseAssignmentIds.includes(
      Number(submission.assignment_id || submission.assignment)
    )
  )

  const students = new Set()

  courseAttempts.forEach((attempt) => {
    if (attempt.student_name) students.add(attempt.student_name)
    else if (attempt.student) students.add(attempt.student)
  })

  courseSubmissions.forEach((submission) => {
    if (submission.student_name) students.add(submission.student_name)
    else if (submission.student) students.add(submission.student)
  })

  const enrolled = students.size

  const avgQuizScore = courseAttempts.length
    ? Math.round(
        courseAttempts.reduce(
          (sum, attempt) => sum + Number(attempt.score || 0),
          0
        ) / courseAttempts.length
      )
    : 0

  const passRate = courseAttempts.length
    ? Math.round(
        (courseAttempts.filter((attempt) => attempt.passed).length /
          courseAttempts.length) *
          100
      )
    : 0

  const completion = enrolled
    ? Math.round(
        Math.min(
          100,
          ((courseSubmissions.length + courseAttempts.length) /
            Math.max(enrolled, 1)) *
            20
        )
      )
    : 0

  const price = Number(course.price || 0)

  return {
    id: course.id,
    title: course.title,
    shortTitle: course.title?.slice(0, 16) || 'Course',
    thumb: thumbFor(index),
    thumbBg: bgFor(index),
    level: course.level,
    lessons: course.lessons_count || course.lessons?.length || 0,
    color: colorFor(index),
    enrolled,
    completion,
    avg_quiz_score: avgQuizScore,
    pass_rate: passRate,
    rating: 'N/A',
    reviews: 0,
    revenue: course.is_free ? 0 : enrolled * price,
    is_free: course.is_free,
    trend: 0,
  }
}

async function fetchData() {
  try {
    const [
      coursesRes,
      quizzesRes,
      attemptsRes,
      assignmentsRes,
      submissionsRes,
    ] = await Promise.all([
      axios.get('http://127.0.0.1:8000/api/courses/', authHeaders()),
      axios.get('http://127.0.0.1:8000/api/quizzes/', authHeaders()),
      axios.get('http://127.0.0.1:8000/api/quiz-attempts/', authHeaders()),
      axios.get('http://127.0.0.1:8000/api/assignments/', authHeaders()),
      axios.get('http://127.0.0.1:8000/api/submissions/', authHeaders()),
    ])

    quizzes.value = quizzesRes.data
    attempts.value = attemptsRes.data
    assignments.value = assignmentsRes.data
    submissions.value = submissionsRes.data

    courses.value = coursesRes.data.map((course, index) =>
      getCourseStats(course, index)
    )

    await nextTick()
    buildCharts()
  } catch (error) {
    console.error(error)
    showToast('Failed to load course performance')
  }
}

function drillDown(course) {
  panel.course = course

  panel.lessons = [
    {
      title: 'Course activity',
      pct: course.completion,
    },
    {
      title: 'Quiz performance',
      pct: course.avg_quiz_score,
    },
    {
      title: 'Quiz pass rate',
      pct: course.pass_rate,
    },
  ]

  panel.funnel = [
    {
      label: 'Enrolled',
      pct: 100,
      color: '#3D5AFE',
    },
    {
      label: 'Active',
      pct: course.completion,
      color: '#00897B',
    },
    {
      label: 'Passed quizzes',
      pct: course.pass_rate,
      color: '#F57C00',
    },
    {
      label: 'Completed',
      pct: course.completion,
      color: '#C62828',
    },
  ]

  panel.open = true

  nextTick(() => {
    buildPanelChart(course)
  })
}

function buildCharts() {
  Object.values(chartInstances).forEach((chart) => chart.destroy())
  chartInstances = {}

  if (
    !enrollChart.value ||
    !completionChart.value ||
    !ratingChart.value ||
    !passRateChart.value
  ) {
    return
  }

  const grid = '#E5E2DA'
  const tick = '#9C9A94'
  const list = filteredCourses.value

  chartInstances.enroll = new Chart(enrollChart.value, {
    type: 'line',
    data: {
      labels: ['Current'],
      datasets: list.map((course) => ({
        label: course.shortTitle,
        data: [course.enrolled],
        borderColor: course.color,
        backgroundColor: course.color + '10',
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: course.color,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: grid }, ticks: { color: tick }, beginAtZero: true },
        x: { grid: { color: grid }, ticks: { color: tick } },
      },
    },
  })

  chartInstances.completion = new Chart(completionChart.value, {
    type: 'bar',
    data: {
      labels: list.map((course) => course.shortTitle),
      datasets: [
        {
          label: 'Completion %',
          data: list.map((course) => course.completion),
          backgroundColor: list.map((course) => course.color + 'CC'),
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { color: grid },
          ticks: { color: tick, callback: (v) => v + '%' },
          max: 100,
        },
        y: { grid: { display: false }, ticks: { color: tick } },
      },
    },
  })

  chartInstances.rating = new Chart(ratingChart.value, {
    type: 'bar',
    data: {
      labels: ['1★', '2★', '3★', '4★', '5★'],
      datasets: [
        {
          data: [0, 0, 0, 0, 0],
          backgroundColor: [
            '#FFCDD2',
            '#FFCC80',
            '#FFF9C4',
            '#C8E6C9',
            '#A5D6A7',
          ],
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: grid }, ticks: { color: tick }, beginAtZero: true },
        x: { grid: { display: false }, ticks: { color: tick } },
      },
    },
  })

  chartInstances.passRate = new Chart(passRateChart.value, {
    type: 'bar',
    data: {
      labels: list.map((course) => course.shortTitle),
      datasets: [
        {
          label: 'Pass rate %',
          data: list.map((course) => course.pass_rate),
          backgroundColor: list.map(
            (course) => passColor(course.pass_rate) + 'CC'
          ),
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          grid: { color: grid },
          ticks: { color: tick, callback: (v) => v + '%' },
          max: 100,
          beginAtZero: true,
        },
        x: { grid: { display: false }, ticks: { color: tick } },
      },
    },
  })
}

function buildPanelChart(course) {
  if (panelChartInst) {
    panelChartInst.destroy()
    panelChartInst = null
  }

  if (!panelChart.value) return

  panelChartInst = new Chart(panelChart.value, {
    type: 'line',
    data: {
      labels: ['Current'],
      datasets: [
        {
          label: 'Enrollments',
          data: [course.enrolled],
          borderColor: course.color,
          backgroundColor: course.color + '14',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: course.color,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          grid: { color: '#E5E2DA' },
          ticks: { color: '#9C9A94' },
          beginAtZero: true,
        },
        x: { grid: { display: false }, ticks: { color: '#9C9A94' } },
      },
    },
  })
}

watch(selectedCourseId, () => {
  nextTick(() => {
    buildCharts()
  })
})

onMounted(() => {
  fetchData()
})
</script>

<style src="./src/assets/CoursePerformance.css"></style>