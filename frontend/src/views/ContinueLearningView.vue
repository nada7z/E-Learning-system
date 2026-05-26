<template>
    <div class="continue-page">
        <div class="page-header">
            <h1>Continue Learning</h1>
            <p>Pick up where you left off</p>
        </div>

        <div v-if="loading" class="empty-box">
            Loading your courses...
        </div>

        <div v-else-if="courses.length === 0" class="empty-box">
            <div class="empty-icon">▶</div>
            <h3>No courses yet</h3>
            <p>Enroll in a course to start learning.</p>
        </div>

        <div v-else class="courses-list">
            <div v-for="course in courses" :key="course.id" class="course-box">
                <img v-if="course.thumbnail" :src="course.thumbnail" class="course-thumb" alt="Course thumbnail" />

                <div v-else class="course-thumb placeholder">
                    📚
                </div>

                <div class="course-content">
                    <div class="course-top">
                        <div>
                            <h3>{{ course.title }}</h3>
                            <p>{{ course.category }}</p>
                        </div>

                        <span class="percent">
                            {{ course.progress_percentage || 0 }}%
                        </span>
                    </div>

                    <div class="progress-track">
                        <div class="progress-fill" :style="{ width: `${course.progress_percentage || 0}%` }"></div>
                    </div>

                    <div class="course-footer">
                        <span>{{ course.lessons_count }} items</span>

                        <button @click="goToCourse(course.id)">
                            Continue
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const courses = ref([])
const loading = ref(false)

function authHeaders() {
    const token = localStorage.getItem('access_token')

    return {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    }
}

async function fetchContinueCourses() {
    loading.value = true

    try {
        const res = await axios.get(
            'http://127.0.0.1:8000/api/continue-learning/',
            authHeaders()
        )

        courses.value = res.data || []
    } catch (err) {
        console.error(err)
    } finally {
        loading.value = false
    }
}

function goToCourse(id) {
    router.push(`/student/courses/${id}`)
}

onMounted(fetchContinueCourses)
</script>

<style scoped>
.continue-page {
    padding: 32px 40px;
}

.page-header {
    margin-bottom: 28px;
}

.page-header h1 {
    font-size: 32px;
    font-weight: 800;
    margin: 0 0 8px;
    color: var(--text, #0f172a);
}

.page-header p {
    margin: 0;
    color: var(--text2, #64748b);
    font-size: 16px;
}

.courses-list {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.course-box {
    display: flex;
    gap: 20px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
}

.course-thumb {
    width: 180px;
    height: 120px;
    border-radius: 18px;
    object-fit: cover;
    flex-shrink: 0;
}

.placeholder {
    background: #eef1ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 42px;
}

.course-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.course-top {
    display: flex;
    justify-content: space-between;
    gap: 16px;
}

.course-top h3 {
    margin: 4px 0 6px;
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
}

.course-top p {
    margin: 0;
    color: #64748b;
    font-size: 14px;
}

.percent {
    font-size: 18px;
    font-weight: 800;
    color: #4f46e5;
}

.progress-track {
    height: 10px;
    background: #eef1ff;
    border-radius: 999px;
    overflow: hidden;
    margin: 20px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4f46e5, #8b5cf6);
    border-radius: 999px;
}

.course-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.course-footer span {
    color: #64748b;
    font-size: 14px;
}

.course-footer button {
    border: none;
    background: #4f46e5;
    color: white;
    font-weight: 700;
    padding: 12px 24px;
    border-radius: 14px;
    cursor: pointer;
}

.course-footer button:hover {
    background: #4338ca;
}

.empty-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 60px;
    text-align: center;
}

.empty-icon {
    font-size: 44px;
    margin-bottom: 12px;
}

@media (max-width: 768px) {
    .continue-page {
        padding: 24px 18px;
    }

    .course-box {
        flex-direction: column;
    }

    .course-thumb {
        width: 100%;
        height: 180px;
    }
}
</style>