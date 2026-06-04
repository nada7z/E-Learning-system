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

                        <button class="continue-btn" @click="continueCourse(course)">
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

const continueCourse = (course) => {
    router.push(`/courses/${course.id}`)
}

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
    padding: 32px;
    width: 100%;
}

.page-header {
    margin-bottom: 24px;
}

.page-header h1 {
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 4px;
    color: var(--text, #1A1916);
}

.page-header p {
    margin: 0;
    color: var(--text2, #6B6860);
    font-size: 14px;
}

.courses-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.course-box {
    display: flex;
    gap: 16px;
    background: var(--surface, #fff);
    border: 1px solid var(--border, #E5E2DA);
    border-radius: 16px;
    padding: 16px;
}

.course-thumb {
    width: 150px;
    height: 96px;
    border-radius: 14px;
    object-fit: cover;
    flex-shrink: 0;
}

.placeholder {
    background: var(--accent-light, #EEF1FF);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
}

.course-content {
    flex: 1;
    min-width: 0;
}

.course-top {
    display: flex;
    justify-content: space-between;
    gap: 16px;
}

.course-top h3 {
    margin: 0 0 4px;
    font-size: 17px;
    font-weight: 700;
    color: var(--text, #1A1916);
}

.course-top p {
    margin: 0;
    color: var(--text2, #6B6860);
    font-size: 13px;
}

.percent {
    font-size: 15px;
    font-weight: 700;
    color: var(--accent, #3D5AFE);
}

.progress-track {
    height: 6px;
    background: var(--surface2, #F0EEE9);
    border-radius: 999px;
    overflow: hidden;
    margin: 14px 0;
}

.progress-fill {
    height: 100%;
    background: var(--accent, #3D5AFE);
    border-radius: 999px;
}

.course-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.course-footer span {
    color: var(--text2, #6B6860);
    font-size: 13px;
}

.course-footer button {
    background: var(--accent, #3D5AFE);
    color: #fff;
    font-weight: 600;
    padding: 9px 18px;
    border-radius: 10px;
}

.course-footer button:hover {
    background: var(--accent-dark, #1939B7);
}

.empty-box {
    background: var(--surface, #fff);
    border: 1px solid var(--border, #E5E2DA);
    border-radius: 16px;
    padding: 40px;
    text-align: center;
}

.empty-icon {
    font-size: 36px;
    margin-bottom: 12px;
}

@media (max-width: 768px) {
    .continue-page {
        padding: 20px;
    }

    .course-box {
        flex-direction: column;
    }

    .course-thumb {
        width: 100%;
        height: 160px;
    }
}
</style>