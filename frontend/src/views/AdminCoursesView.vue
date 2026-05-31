<template>
    <div class="page admin-courses-page">
        <div class="courses-header">
            <div>
                <h1>All Courses</h1>
                <p>{{ filteredCourses.length }} courses total</p>
            </div>
        </div>

        <div class="courses-toolbar">
            <div class="search-box">
                <span>🔍</span>
                <input v-model="search" placeholder="Search courses..." />
            </div>

            <select v-model="categoryFilter">
                <option value="">All Categories</option>
                <option v-for="category in categories" :key="category" :value="category">
                    {{ category }}
                </option>
            </select>

            <select v-model="levelFilter">
                <option value="">All Levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
            </select>

            <div class="view-toggle">
                <button class="active">Grid</button>
                <button>List</button>
            </div>
        </div>

        <p v-if="loading">Loading courses...</p>
        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="course-grid">
            <div v-for="course in filteredCourses" :key="course.id" class="course-card">
                <div class="course-cover" :class="coverClass(course.category)">
                    <img v-if="course.thumbnail" :src="course.thumbnail" alt="Course thumbnail" />
                    <span v-else>{{ coverEmoji(course.category) }}</span>
                </div>

                <div class="course-body">
                    <div class="course-badges">
                        <span class="badge blue">{{ course.category || 'General' }}</span>
                        <span class="badge gray">{{ formatLevel(course.level) }}</span>
                    </div>

                    <h3>{{ course.title }}</h3>

                    <div class="meta-row">
                        <span>👤 {{ course.teacher_name || 'Teacher' }}</span>
                        <span>📖 {{ course.lessons_count || 0 }} lessons</span>
                        <span>⏱ {{ course.duration_hours || 0 }}h</span>
                    </div>

                    <div class="course-bottom">
                        <div class="rating">
                            ⭐ <strong>{{ course.avg_rating || '0.0' }}</strong>
                        </div>

                        <span>{{ course.enrolled_count || 0 }} students</span>

                        <span class="status" :class="course.is_published ? 'published' : 'draft'">
                            {{ course.is_published ? 'published' : 'draft' }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <p v-if="!loading && !filteredCourses.length" class="empty">
            No courses found.
        </p>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const API_URL = 'http://localhost:8000/api/student/courses/'

const courses = ref([])
const loading = ref(false)
const error = ref('')

const search = ref('')
const categoryFilter = ref('')
const levelFilter = ref('')

const getAuthHeaders = () => {
    const token =
        localStorage.getItem('access_token') ||
        localStorage.getItem('access') ||
        localStorage.getItem('token')

    return token ? { Authorization: `Bearer ${token}` } : {}
}

const getAverageRating = async (courseId) => {
    try {
        const response = await fetch(
            `http://localhost:8000/api/courses/${courseId}/reviews/`,
            {
                headers: {
                    Accept: 'application/json',
                    ...getAuthHeaders(),
                },
            }
        )

        if (!response.ok) return '0.0'

        const data = await response.json()
        const reviews = data.reviews || []

        if (!reviews.length) return '0.0'

        const total = reviews.reduce((sum, review) => {
            return sum + Number(review.rating || 0)
        }, 0)

        return (total / reviews.length).toFixed(1)
    } catch {
        return '0.0'
    }
}

const fetchCourses = async () => {
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
            throw new Error(`Courses request failed (${response.status})`)
        }

        const courseData = await response.json()

        courses.value = await Promise.all(
            courseData.map(async (course) => {
                const avgRating = await getAverageRating(course.id)

                return {
                    ...course,
                    avg_rating: avgRating,
                }
            })
        )
    } catch (err) {
        error.value = err.message || 'Could not load courses.'
        courses.value = []
    } finally {
        loading.value = false
    }
}

const categories = computed(() => {
    return [...new Set(courses.value.map((course) => course.category).filter(Boolean))]
})

const filteredCourses = computed(() => {
    const q = search.value.toLowerCase().trim()

    return courses.value.filter((course) => {
        const matchesSearch =
            !q ||
            course.title?.toLowerCase().includes(q) ||
            course.teacher_name?.toLowerCase().includes(q) ||
            course.category?.toLowerCase().includes(q)

        const matchesCategory =
            !categoryFilter.value || course.category === categoryFilter.value

        const matchesLevel =
            !levelFilter.value || course.level === levelFilter.value

        return matchesSearch && matchesCategory && matchesLevel
    })
})

const formatLevel = (level) => {
    if (!level) return 'Beginner'
    return level.charAt(0).toUpperCase() + level.slice(1)
}

const coverEmoji = (category) => {
    const value = (category || '').toLowerCase()

    if (value.includes('development') || value.includes('web')) return '💻'
    if (value.includes('data')) return '📊'
    if (value.includes('design')) return '🎨'
    if (value.includes('ai') || value.includes('machine')) return '🤖'
    if (value.includes('mobile')) return '📱'
    if (value.includes('cloud')) return '☁️'

    return '📚'
}

const coverClass = (category) => {
    const value = (category || '').toLowerCase()

    if (value.includes('development') || value.includes('web')) return 'cover-blue'
    if (value.includes('data')) return 'cover-mint'
    if (value.includes('design')) return 'cover-pink'
    if (value.includes('ai') || value.includes('machine')) return 'cover-purple'
    if (value.includes('mobile')) return 'cover-yellow'

    return 'cover-blue'
}

onMounted(fetchCourses)
</script>

<style scoped>
@import '../assets/AdminCoursesView.css';
</style>