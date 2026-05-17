<template>
  <div class="course-detail-page">
    <button class="back-btn" @click="router.back()">
      ← Back to courses
    </button>

    <div v-if="loading" class="empty-state">
      Loading course...
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <template v-else-if="course">
      <section class="course-hero">
        <div>
          <span class="course-category">
            {{ course.category }}
          </span>

          <h1>{{ course.title }}</h1>

          <p>{{ course.description }}</p>

          <div class="course-meta">
            <span>{{ course.teacher_name }}</span>
            <span>{{ course.lessons_count || course.lessons?.length || 0 }} lessons</span>
            <span>{{ course.duration_hours }}h</span>
            <span class="level">{{ course.level }}</span>
          </div>
        </div>

        <div class="hero-card">
          <img
            v-if="course.thumbnail"
            :src="course.thumbnail"
            :alt="course.title"
          />

          <div v-else class="course-placeholder">
            {{ course.title?.charAt(0).toUpperCase() }}
          </div>

          <button
            class="primary-btn"
            :disabled="course.is_enrolled || enrolling"
            @click="enroll"
          >
            <span v-if="enrolling">Enrolling...</span>
            <span v-else-if="course.is_enrolled">Enrolled</span>
            <span v-else>Enroll Now</span>
          </button>
        </div>
      </section>

      <section class="content-layout">
        <div class="lesson-panel">
          <h2>Course Content</h2>

          <div
            v-if="course.lessons && course.lessons.length"
            class="lesson-list"
          >
            <button
              v-for="lesson in course.lessons"
              :key="lesson.id"
              class="lesson-item"
              :class="{ active: selectedLesson?.id === lesson.id }"
              @click="selectedLesson = lesson"
            >
              <span class="lesson-number">
                {{ lesson.order_number }}
              </span>

              <div>
                <strong>{{ lesson.title }}</strong>
                <small>{{ lesson.lesson_type }}</small>
              </div>
            </button>
          </div>

          <div v-else class="empty-state small">
            No lessons available yet.
          </div>
        </div>

        <div class="lesson-content">
          <template v-if="selectedLesson">
            <div class="lesson-header">
              <span class="lesson-type">
                {{ selectedLesson.lesson_type }}
              </span>

              <h2>{{ selectedLesson.title }}</h2>
            </div>

            <video
              v-if="selectedLesson.video_file"
              class="lesson-video"
              controls
              :src="selectedLesson.video_file"
            ></video>

            <iframe
              v-else-if="selectedLesson.video_url"
              class="lesson-video"
              :src="selectedLesson.video_url"
              allowfullscreen
            ></iframe>

            <div
              v-if="selectedLesson.content"
              class="lesson-text"
            >
              {{ selectedLesson.content }}
            </div>

            <div
              v-if="selectedLesson.lesson_type === 'quiz'"
              class="activity-box"
            >
              <h3>Quiz</h3>
              <p>This lesson has a quiz.</p>
              <button class="secondary-btn">
                Start Quiz
              </button>
            </div>

            <div
              v-if="selectedLesson.lesson_type === 'assignment'"
              class="activity-box"
            >
              <h3>Assignment</h3>
              <p>This lesson has an assignment.</p>
              <button class="secondary-btn">
                View Assignment
              </button>
            </div>
          </template>

          <div v-else class="empty-state">
            Select a lesson to start learning.
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const course = ref(null)
const selectedLesson = ref(null)
const loading = ref(false)
const error = ref('')
const enrolling = ref(false)

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api'

const getAuthHeaders = () => {
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('access') ||
    localStorage.getItem('token')

  return token
    ? { Authorization: `Bearer ${token}` }
    : {}
}

const fetchCourse = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_BASE}/courses/${route.params.id}/`, {
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Could not load course.')
    }

    course.value = data
    selectedLesson.value = data.lessons?.[0] || null
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const enroll = async () => {
  enrolling.value = true
  error.value = ''

  try {
    const response = await fetch(
      `${API_BASE}/student/courses/${route.params.id}/enroll/`,
      {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          ...getAuthHeaders(),
        },
      }
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Could not enroll.')
    }

    course.value.is_enrolled = true
  } catch (err) {
    error.value = err.message
  } finally {
    enrolling.value = false
  }
}

onMounted(fetchCourse)
</script>

<style src="./src/assets/StudentCourseDetail.css"></style>