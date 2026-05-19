<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Student Stats</h1>
        <p class="page-sub">Performance overview across all your courses</p>
      </div>
      <div class="header-actions">
        <select v-model="filterCourse" class="input filter-select">
          <option value="">All courses</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
        </select>
        <button class="btn btn-ghost btn-sm" @click="showToast('Report exported 📥')">
          ↓ Export CSV
        </button>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background:#EEF1FF">👥</div>
        <div class="stat-val">{{ totalStudents }}</div>
        <div class="stat-label">Total Students</div>
        <div class="stat-trend trend-up">↑ 14 this month</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#E0F2F1">📊</div>
        <div class="stat-val">{{ avgProgress }}%</div>
        <div class="stat-label">Avg Progress</div>
        <div class="stat-trend trend-up">↑ 3.2% this week</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFF3E0">🏆</div>
        <div class="stat-val">{{ avgQuizScore }}%</div>
        <div class="stat-label">Avg Quiz Score</div>
        <div class="stat-trend trend-up">↑ 5pts vs last month</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#EDE9FE">✅</div>
        <div class="stat-val">{{ completionRate }}%</div>
        <div class="stat-label">Completion Rate</div>
        <div class="stat-trend trend-dn">↓ 1.1% this week</div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="charts-row">
      <div class="card chart-card">
        <div class="card-header">
          <span class="card-title">Quiz Score Distribution</span>
          <span class="badge badge-blue">All quizzes</span>
        </div>
        <div class="chart-wrap">
          <canvas ref="scoreDistChart" aria-label="Bar chart of quiz score distribution across score ranges"></canvas>
        </div>
      </div>

      <div class="card chart-card">
        <div class="card-header">
          <span class="card-title">Progress Over Time</span>
          <span class="badge badge-green">Last 8 weeks</span>
        </div>
        <div class="chart-wrap">
          <canvas ref="progressChart" aria-label="Line chart of average student progress over 8 weeks"></canvas>
        </div>
      </div>
    </div>

    <!-- Engagement donut + top students -->
    <div class="bottom-row">
      <div class="card">
        <div class="card-header">
          <span class="card-title">Engagement Breakdown</span>
        </div>
        <div class="chart-wrap-sm">
          <canvas ref="engagementChart" aria-label="Doughnut chart of student engagement levels"></canvas>
        </div>
        <div class="donut-legend">
          <div v-for="item in engagementLegend" :key="item.label" class="legend-item">
            <span class="legend-dot" :style="{ background: item.color }"></span>
            <span class="legend-label">{{ item.label }}</span>
            <span class="legend-val">{{ item.val }}%</span>
          </div>
        </div>
      </div>

      <div class="card" style="flex:1">
        <div class="card-header">
          <span class="card-title">Top Performers</span>
          <span class="card-action" @click="activeTab = 'all'">View all</span>
        </div>
        <div class="top-list">
          <div v-for="(s, i) in topStudents" :key="s.id" class="top-row">
            <span class="top-rank" :class="i < 3 ? 'rank-gold' : ''">{{ i + 1 }}</span>
            <div class="avatar-sm" :style="{ background: s.color + '22', color: s.color }">
              {{ initials(s.name) }}
            </div>
            <div class="top-info">
              <div class="top-name">{{ s.name }}</div>
              <div class="top-course">{{ s.course }}</div>
            </div>
            <div class="top-right">
              <div class="top-score">{{ s.avg_score }}%</div>
              <div class="mini-bar-wrap">
                <div class="mini-bar">
                  <div class="mini-fill" :style="{ width: s.avg_score + '%', background: scoreColor(s.avg_score) }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters & search above table -->
    <div class="table-toolbar">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input v-model="search" class="input search-input" placeholder="Search students…" />
      </div>
      <div class="tab-bar">
        <button
          v-for="t in tabs" :key="t.value"
          class="tab" :class="{ active: activeTab === t.value }"
          @click="activeTab = t.value"
        >{{ t.label }}</button>
      </div>
      <select v-model="sortBy" class="input filter-select" style="min-width:160px">
        <option value="name">Sort: Name</option>
        <option value="progress">Sort: Progress</option>
        <option value="avg_score">Sort: Quiz Score</option>
        <option value="submissions">Sort: Submissions</option>
      </select>
    </div>

    <!-- Student table -->
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Student</th>
            <th>Course</th>
            <th>Progress</th>
            <th>Avg Quiz Score</th>
            <th>Submissions</th>
            <th>Last Active</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!filteredStudents.length">
            <td colspan="8" style="text-align:center;padding:40px;color:#9C9A94">No students match your filters.</td>
          </tr>
          <tr v-for="s in filteredStudents" :key="s.id">
            <td>
              <div class="student-cell">
                <div class="avatar-sm" :style="{ background: s.color + '22', color: s.color }">
                  {{ initials(s.name) }}
                </div>
                <div>
                  <div class="student-name">{{ s.name }}</div>
                  <div class="student-email">{{ s.email }}</div>
                </div>
              </div>
            </td>
            <td>
              <span class="course-chip">{{ s.course }}</span>
            </td>
            <td>
              <div class="progress-cell">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: s.progress + '%', background: progressColor(s.progress) }"
                  ></div>
                </div>
                <span class="progress-pct">{{ s.progress }}%</span>
              </div>
            </td>
            <td>
              <span class="score-chip" :class="scoreClass(s.avg_score)">
                {{ s.avg_score }}%
              </span>
            </td>
            <td class="text-muted">{{ s.submissions }} / {{ s.total_assignments }}</td>
            <td class="text-muted text-sm">{{ s.last_active }}</td>
            <td>
              <span class="status-badge" :class="s.status === 'active' ? 'status-green' : s.status === 'at_risk' ? 'status-red' : 'status-gray'">
                {{ statusLabel(s.status) }}
              </span>
            </td>
            <td>
              <button class="btn btn-ghost btn-sm" @click="openDetail(s)">View →</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Student detail drawer -->
    <Transition name="slide-right">
      <div v-if="drawer.open" class="drawer-overlay" @click.self="drawer.open = false">
        <div class="drawer">
          <div class="drawer-header">
            <div class="drawer-student">
              <div class="avatar-lg" :style="{ background: drawer.student?.color + '22', color: drawer.student?.color }">
                {{ initials(drawer.student?.name ?? '') }}
              </div>
              <div>
                <div class="drawer-name">{{ drawer.student?.name }}</div>
                <div class="drawer-email">{{ drawer.student?.email }}</div>
              </div>
            </div>
            <button class="icon-btn" @click="drawer.open = false">✕</button>
          </div>

          <div class="drawer-body">
            <div class="detail-stat-row">
              <div class="detail-stat">
                <div class="detail-stat-val">{{ drawer.student?.progress }}%</div>
                <div class="detail-stat-label">Progress</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-val">{{ drawer.student?.avg_score }}%</div>
                <div class="detail-stat-label">Avg Score</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-val">{{ drawer.student?.submissions }}</div>
                <div class="detail-stat-label">Submitted</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-val">{{ drawer.student?.streak }}d</div>
                <div class="detail-stat-label">Streak</div>
              </div>
            </div>

            <div class="detail-section">
              <div class="detail-section-title">Course progress</div>
              <div class="detail-progress-bar">
                <div
                  class="detail-progress-fill"
                  :style="{ width: drawer.student?.progress + '%', background: progressColor(drawer.student?.progress ?? 0) }"
                ></div>
              </div>
              <div class="detail-progress-label">{{ drawer.student?.progress }}% complete · {{ drawer.student?.course }}</div>
            </div>

            <div class="detail-section">
              <div class="detail-section-title">Quiz history</div>
              <div class="quiz-history">
                <div v-for="(q, i) in drawer.quizHistory" :key="i" class="quiz-history-row">
                  <span class="quiz-history-name">{{ q.name }}</span>
                  <div class="quiz-history-bar">
                    <div class="quiz-history-fill" :style="{ width: q.score + '%', background: scoreColor(q.score) }"></div>
                  </div>
                  <span class="quiz-history-score" :class="scoreClass(q.score)">{{ q.score }}%</span>
                  <span class="status-badge" :class="q.passed ? 'status-green' : 'status-red'" style="font-size:10px">
                    {{ q.passed ? 'Pass' : 'Fail' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <div class="detail-section-title">Assignments</div>
              <div class="assign-history">
                <div v-for="(a, i) in drawer.assignHistory" :key="i" class="assign-row">
                  <div>
                    <div class="assign-name">{{ a.name }}</div>
                    <div class="assign-date text-muted text-sm">{{ a.submitted }}</div>
                  </div>
                  <span v-if="a.grade != null" class="score-chip" :class="scoreClass(a.grade / a.max * 100)">
                    {{ a.grade }} / {{ a.max }}
                  </span>
                  <span v-else class="status-badge status-warn">Pending</span>
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
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import axios from 'axios'

const scoreDistChart = ref(null)
const progressChart = ref(null)
const engagementChart = ref(null)

let chartInstances = {}

const courses = ref([])
const quizzes = ref([])
const attempts = ref([])
const assignments = ref([])
const submissions = ref([])
const students = ref([])

const search = ref('')
const filterCourse = ref('')
const activeTab = ref('all')
const sortBy = ref('progress')

const toast = reactive({ visible: false, message: '' })

const drawer = reactive({
  open: false,
  student: null,
  quizHistory: [],
  assignHistory: [],
})

const tabs = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'at_risk', label: 'At risk' },
  { value: 'inactive', label: 'Inactive' },
]

function authHeaders() {
  const token = localStorage.getItem('access_token')

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

const totalStudents = computed(() => students.value.length)

const avgProgress = computed(() => {
  if (!students.value.length) return 0

  return Math.round(
    students.value.reduce((sum, student) => sum + student.progress, 0) /
      students.value.length
  )
})

const avgQuizScore = computed(() => {
  if (!students.value.length) return 0

  return Math.round(
    students.value.reduce((sum, student) => sum + student.avg_score, 0) /
      students.value.length
  )
})

const completionRate = computed(() => {
  if (!students.value.length) return 0

  return Math.round(
    (students.value.filter((student) => student.progress >= 100).length /
      students.value.length) *
      100
  )
})

const topStudents = computed(() => {
  return [...students.value]
    .sort((a, b) => b.avg_score - a.avg_score)
    .slice(0, 5)
})

const filteredStudents = computed(() => {
  let list = students.value

  if (filterCourse.value) {
    list = list.filter(
      (student) => Number(student.course_id) === Number(filterCourse.value)
    )
  }

  if (activeTab.value !== 'all') {
    list = list.filter((student) => student.status === activeTab.value)
  }

  if (search.value) {
    const term = search.value.toLowerCase()

    list = list.filter((student) => {
      return (
        student.name.toLowerCase().includes(term) ||
        student.email.toLowerCase().includes(term)
      )
    })
  }

  return [...list].sort((a, b) => {
    if (sortBy.value === 'name') {
      return a.name.localeCompare(b.name)
    }

    return Number(b[sortBy.value] || 0) - Number(a[sortBy.value] || 0)
  })
})

const engagementLegend = computed(() => {
  const total = students.value.length || 1

  const highlyActive = students.value.filter(
    (student) => student.progress >= 80
  ).length

  const active = students.value.filter(
    (student) => student.progress >= 40 && student.progress < 80
  ).length

  const atRisk = students.value.filter(
    (student) => student.status === 'at_risk'
  ).length

  const inactive = students.value.filter(
    (student) => student.status === 'inactive'
  ).length

  return [
    {
      label: 'Highly active',
      color: '#3D5AFE',
      val: Math.round((highlyActive / total) * 100),
    },
    {
      label: 'Active',
      color: '#00897B',
      val: Math.round((active / total) * 100),
    },
    {
      label: 'At risk',
      color: '#F57C00',
      val: Math.round((atRisk / total) * 100),
    },
    {
      label: 'Inactive',
      color: '#E5E2DA',
      val: Math.round((inactive / total) * 100),
    },
  ]
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

function initials(name) {
  if (!name) return '?'

  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function progressColor(p) {
  return p >= 70 ? '#00897B' : p >= 40 ? '#3D5AFE' : '#F57C00'
}

function scoreColor(s) {
  return s >= 75 ? '#00897B' : s >= 50 ? '#F57C00' : '#C62828'
}

function scoreClass(s) {
  return s >= 75 ? 'score-high' : s >= 50 ? 'score-mid' : 'score-low'
}

function statusLabel(s) {
  return {
    active: 'Active',
    at_risk: 'At risk',
    inactive: 'Inactive',
  }[s] || s
}

function formatDate(date) {
  if (!date) return '—'

  return new Date(date).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
  })
}

function showToast(msg) {
  toast.message = msg
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 2600)
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

    courses.value = coursesRes.data
    quizzes.value = quizzesRes.data
    attempts.value = attemptsRes.data
    assignments.value = assignmentsRes.data
    submissions.value = submissionsRes.data

    buildStudents()

    await nextTick()
    buildCharts()
  } catch (error) {
    console.error(error)
    showToast('Failed to load student statistics')
  }
}

function buildStudents() {
  const map = new Map()

  attempts.value.forEach((attempt) => {
    const quiz = quizzes.value.find(
      (q) => Number(q.id) === Number(attempt.quiz_id || attempt.quiz)
    )

    if (!quiz) return

    const course = courses.value.find(
      (c) => Number(c.id) === Number(quiz.course)
    )

    const name =
      attempt.student_name ||
      `Student ${attempt.student || attempt.id}`

    const key = `${name}-${quiz.course}`

    if (!map.has(key)) {
      map.set(key, {
        id: key,
        name,
        email: '—',
        course_id: quiz.course,
        course: course?.title || 'Course',
        progress: 0,
        avg_score: 0,
        quizScores: [],
        submissions: 0,
        total_assignments: 0,
        last_active: formatDate(attempt.submitted_at),
        status: 'inactive',
        color: colorFor(map.size),
        streak: 0,
      })
    }

    const student = map.get(key)

    student.quizScores.push(Number(attempt.score || 0))
    student.avg_score = Math.round(
      student.quizScores.reduce((sum, score) => sum + score, 0) /
        student.quizScores.length
    )

    student.last_active = formatDate(attempt.submitted_at)
  })

  submissions.value.forEach((submission) => {
    const assignment = assignments.value.find(
      (a) =>
        Number(a.id) === Number(submission.assignment_id || submission.assignment)
    )

    if (!assignment) return

    const course = courses.value.find(
      (c) => Number(c.id) === Number(assignment.course)
    )

    const name =
      submission.student_name ||
      `Student ${submission.student || submission.id}`

    const key = `${name}-${assignment.course}`

    if (!map.has(key)) {
      map.set(key, {
        id: key,
        name,
        email: '—',
        course_id: assignment.course,
        course: course?.title || 'Course',
        progress: 0,
        avg_score: 0,
        quizScores: [],
        submissions: 0,
        total_assignments: 0,
        last_active: formatDate(submission.submitted_at),
        status: 'inactive',
        color: colorFor(map.size),
        streak: 0,
      })
    }

    const student = map.get(key)

    student.submissions += 1
    student.last_active = formatDate(submission.submitted_at)
  })

  const allStudents = Array.from(map.values())

  allStudents.forEach((student) => {
    const courseAssignments = assignments.value.filter(
      (assignment) => Number(assignment.course) === Number(student.course_id)
    )

    const courseQuizzes = quizzes.value.filter(
      (quiz) => Number(quiz.course) === Number(student.course_id)
    )

    student.total_assignments = courseAssignments.length

    const assignmentProgress = courseAssignments.length
      ? (student.submissions / courseAssignments.length) * 50
      : 0

    const quizProgress = courseQuizzes.length
      ? (student.quizScores.length / courseQuizzes.length) * 50
      : 0

    student.progress = Math.min(
      100,
      Math.round(assignmentProgress + quizProgress)
    )

    if (student.progress < 20) {
      student.status = 'inactive'
    } else if (student.progress < 45 || student.avg_score < 50) {
      student.status = 'at_risk'
    } else {
      student.status = 'active'
    }

    student.streak = student.status === 'active' ? 1 : 0
  })

  students.value = allStudents
}

function openDetail(student) {
  drawer.student = student

  const studentAttempts = attempts.value.filter((attempt) => {
    const quiz = quizzes.value.find(
      (q) => Number(q.id) === Number(attempt.quiz_id || attempt.quiz)
    )

    return (
      quiz &&
      Number(quiz.course) === Number(student.course_id) &&
      (attempt.student_name === student.name ||
        `Student ${attempt.student || attempt.id}` === student.name)
    )
  })

  drawer.quizHistory = studentAttempts.map((attempt) => ({
    name: attempt.quiz_title || 'Quiz',
    score: Math.round(Number(attempt.score || 0)),
    passed: attempt.passed,
  }))

  const studentSubmissions = submissions.value.filter((submission) => {
    const assignment = assignments.value.find(
      (a) =>
        Number(a.id) === Number(submission.assignment_id || submission.assignment)
    )

    return (
      assignment &&
      Number(assignment.course) === Number(student.course_id) &&
      (submission.student_name === student.name ||
        `Student ${submission.student || submission.id}` === student.name)
    )
  })

  drawer.assignHistory = studentSubmissions.map((submission) => ({
    name: submission.assignment_title || 'Assignment',
    submitted: formatDate(submission.submitted_at),
    grade: submission.grade,
    max: 100,
  }))

  drawer.open = true
}

function buildCharts() {
  Object.values(chartInstances).forEach((chart) => chart.destroy())
  chartInstances = {}

  if (!scoreDistChart.value || !progressChart.value || !engagementChart.value) {
    return
  }

  const grid = '#E5E2DA'
  const tick = '#9C9A94'

  const ranges = [0, 0, 0, 0, 0, 0]

  students.value.forEach((student) => {
    const score = student.avg_score

    if (score <= 20) ranges[0]++
    else if (score <= 40) ranges[1]++
    else if (score <= 60) ranges[2]++
    else if (score <= 75) ranges[3]++
    else if (score <= 90) ranges[4]++
    else ranges[5]++
  })

  chartInstances.scoreDist = new Chart(scoreDistChart.value, {
    type: 'bar',
    data: {
      labels: ['0–20', '21–40', '41–60', '61–75', '76–90', '91–100'],
      datasets: [
        {
          label: 'Students',
          data: ranges,
          backgroundColor: [
            '#FFCDD2',
            '#FFCC80',
            '#FFF9C4',
            '#B3E5FC',
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
        y: {
          grid: { color: grid },
          ticks: { color: tick, stepSize: 1 },
          beginAtZero: true,
        },
        x: { grid: { display: false }, ticks: { color: tick } },
      },
    },
  })

  chartInstances.progress = new Chart(progressChart.value, {
    type: 'line',
    data: {
      labels: ['Current'],
      datasets: courses.value.map((course, index) => {
        const courseStudents = students.value.filter(
          (student) => Number(student.course_id) === Number(course.id)
        )

        const avg = courseStudents.length
          ? Math.round(
              courseStudents.reduce((sum, s) => sum + s.progress, 0) /
                courseStudents.length
            )
          : 0

        return {
          label: course.title,
          data: [avg],
          borderColor: colorFor(index),
          backgroundColor: colorFor(index) + '14',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: colorFor(index),
        }
      }),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: tick,
            usePointStyle: true,
            pointStyle: 'circle',
            font: { size: 12 },
            padding: 16,
          },
        },
      },
      scales: {
        y: {
          grid: { color: grid },
          ticks: { color: tick, callback: (v) => v + '%' },
          max: 100,
          beginAtZero: true,
        },
        x: { grid: { color: grid }, ticks: { color: tick } },
      },
    },
  })

  chartInstances.engagement = new Chart(engagementChart.value, {
    type: 'doughnut',
    data: {
      labels: engagementLegend.value.map((e) => e.label),
      datasets: [
        {
          data: engagementLegend.value.map((e) => e.val),
          backgroundColor: engagementLegend.value.map((e) => e.color),
          borderWidth: 0,
          hoverOffset: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: { legend: { display: false } },
    },
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style src="./src/assets/StudentsStatsView.css"></style>