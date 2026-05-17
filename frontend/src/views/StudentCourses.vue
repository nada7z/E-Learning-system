<template>
  <div class="student-courses-page">
    <div class="courses-header">
      <div>
        <h1>Explore Courses</h1>
        <p>
          Choose a course and enroll to start learning.
        </p>
      </div>
    </div>

    <div
      v-if="loading"
      class="empty-state"
    >
      Loading courses...
    </div>

    <div
      v-else-if="courses.length === 0"
      class="empty-state"
    >
      <strong>No courses available yet</strong>

      <span>
        Published courses will appear here.
      </span>
    </div>

    <div
      v-else
      class="courses-grid"
    >
      <div
        v-for="course in courses"
        :key="course.id"
        class="course-card"
        @click="openCourse(course)"
      >
        <div class="course-image">
          <img
            v-if="course.thumbnail"
            :src="course.thumbnail"
            :alt="course.title"
          />

          <div
            v-else
            class="course-placeholder"
          >
            {{ course.title.charAt(0).toUpperCase() }}
          </div>
        </div>

        <div class="course-content">
          <div class="course-top">
            <span class="course-category">
              {{ course.category }}
            </span>

            <span class="course-level">
              {{ course.level }}
            </span>
          </div>

          <h2>
            {{ course.title }}
          </h2>

          <p class="course-description">
            {{ course.description }}
          </p>

          <div class="course-meta">
            <span>
              {{ course.teacher_name }}
            </span>

            <span>
              {{ course.lessons_count }} lessons
            </span>

            <span>
              {{ course.duration_hours }}h
            </span>
          </div>

          <div class="course-footer">
            <div class="course-price">
              <span v-if="course.is_free">
                Free
              </span>

              <span v-else>
                ${{ course.price }}
              </span>
            </div>

            <button
              class="enroll-btn"
              :disabled="
                course.is_enrolled ||
                enrollingId === course.id
              "
              @click.stop="enroll(course)"
            >
              <span
                v-if="
                  enrollingId === course.id
                "
              >
                Enrolling...
              </span>

              <span
                v-else-if="
                  course.is_enrolled
                "
              >
                Enrolled
              </span>

              <span v-else>
                Enroll Now
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <p
      v-if="error"
      class="error-message"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const openCourse = (course) => {
  router.push({
    name: 'StudentCourseDetail',
    params: { id: course.id },
  })
}

const emit = defineEmits(['toast'])

const courses = ref([])
const loading = ref(false)
const error = ref('')
const enrollingId = ref(null)

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

const getAuthHeaders = () => {
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('access') ||
    localStorage.getItem('token')

  return token
    ? { Authorization: `Bearer ${token}` }
    : {}
}

const fetchCourses = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_BASE}/student/courses/`, {
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error('Could not load courses.')
    }

    courses.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const enroll = async (course) => {
  enrollingId.value = course.id
  error.value = ''

  try {
    const response = await fetch(
      `${API_BASE}/student/courses/${course.id}/enroll/`,
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
      throw new Error(data.detail || 'Could not enroll in course.')
    }

    course.is_enrolled = true

    emit('toast', data.detail || 'Enrolled successfully.', '✅')
  } catch (err) {
    error.value = err.message
    emit('toast', err.message, '⚠️')
  } finally {
    enrollingId.value = null
  }
}

onMounted(fetchCourses)
</script>

<style src="./src/assets/StudentCourses.css"></style>