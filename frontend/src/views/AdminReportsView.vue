<template>
    <div class="page">
        <div class="page-header">
            <h1 class="page-title">Reports</h1>
            <p class="page-sub">Platform analytics and insights</p>
        </div>

        <p v-if="loading">Loading reports...</p>
        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="stat-grid">
            <StatCard :icon="Users" :value="formatNumber(stats.total_users)" label="Total Users" />
            <StatCard :icon="BookOpen" :value="formatNumber(stats.total_courses)" label="Total Courses"
                background="#E0F2F1" />
            <StatCard :icon="GraduationCap" :value="formatNumber(stats.total_enrollments)" label="Enrollments"
                background="#EDE9FE" />
            <StatCard :icon="DollarSign" :value="formatMoney(stats.total_revenue)" label="Revenue"
                background="#FFF3E0" />
        </div>

        <div class="reports-grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">User Growth</span>
                </div>
                <div class="chart-box">
                    <canvas ref="userGrowthCanvas"></canvas>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Enrollment Growth</span>
                </div>
                <div class="chart-box">
                    <canvas ref="enrollmentCanvas"></canvas>
                </div>
            </div>
        </div>

        <div class="card top-courses-card">
            <div class="card-header">
                <span class="card-title">Top Courses</span>
            </div>

            <table class="reports-table">
                <thead>
                    <tr>
                        <th>COURSE</th>
                        <th>TEACHER</th>
                        <th>STUDENTS</th>
                        <th>RATING</th>
                        <th>STATUS</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="course in topCourses" :key="course.id">
                        <td>{{ course.title }}</td>
                        <td>{{ course.teacher }}</td>
                        <td>{{ course.students }}</td>
                        <td>⭐ {{ course.rating }}</td>
                        <td>
                            <span class="status-pill" :class="course.published ? 'published' : 'draft'">
                                {{ course.published ? 'published' : 'draft' }}
                            </span>
                        </td>
                    </tr>

                    <tr v-if="!topCourses.length && !loading">
                        <td colspan="5" class="empty-row">No courses found</td>
                    </tr>
                </tbody>
            </table>
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

const API_URL = 'http://localhost:8000/api/dashboard/reports/'

const loading = ref(false)
const error = ref('')

const stats = ref({
    total_users: 0,
    total_courses: 0,
    total_enrollments: 0,
    total_revenue: 0,
})

const userGrowth = ref([])
const enrollmentGrowth = ref([])
const topCourses = ref([])

const userGrowthCanvas = ref(null)
const enrollmentCanvas = ref(null)

let charts = []

const getAuthHeaders = () => {
    const token =
        localStorage.getItem('access_token') ||
        localStorage.getItem('access') ||
        localStorage.getItem('token')

    return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchReports = async () => {
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
            throw new Error(`Reports request failed (${response.status})`)
        }

        const data = await response.json()

        stats.value = data.stats || stats.value
        userGrowth.value = data.user_growth || []
        enrollmentGrowth.value = data.enrollment_growth || []
        topCourses.value = data.top_courses || []

        await nextTick()
        renderCharts()
    } catch (err) {
        error.value = err.message || 'Could not load reports.'
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
                type: 'line',
                data: {
                    labels: userGrowth.value.map((item) => item.label),
                    datasets: [
                        {
                            label: 'Users',
                            data: userGrowth.value.map((item) => item.value),
                            tension: 0.35,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                },
            })
        )
    }

    if (enrollmentCanvas.value) {
        charts.push(
            new Chart(enrollmentCanvas.value, {
                type: 'bar',
                data: {
                    labels: enrollmentGrowth.value.map((item) => item.label),
                    datasets: [
                        {
                            label: 'Enrollments',
                            data: enrollmentGrowth.value.map((item) => item.value),
                            borderRadius: 8,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
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

onMounted(fetchReports)

onBeforeUnmount(() => {
    charts.forEach((chart) => chart.destroy())
})
</script>

<style scoped>
.reports-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-bottom: 24px;
}

.chart-box {
    height: 260px;
}

.top-courses-card {
    padding: 0;
    overflow: hidden;
}

.top-courses-card .card-header {
    padding: 22px 24px 0;
}

.reports-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
}

.reports-table th {
    text-align: left;
    padding: 14px 22px;
    font-size: 12px;
    font-weight: 800;
    color: #8f8b83;
    border-bottom: 1px solid #e5dfd6;
}

.reports-table td {
    padding: 16px 22px;
    border-bottom: 1px solid #e5dfd6;
}

.status-pill {
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
}

.status-pill.published {
    background: #dff5f2;
    color: #00897b;
}

.status-pill.draft {
    background: #fff3dc;
    color: #f57c00;
}

.empty-row {
    text-align: center;
    color: #777;
}

.error-text {
    color: red;
}

@media (max-width: 1000px) {
    .reports-grid {
        grid-template-columns: 1fr;
    }
}
</style>