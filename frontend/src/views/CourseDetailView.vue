<template>
  <div class="course-detail-page">
    <div v-if="loading" class="state-box">
      Loading course...
    </div>

    <div v-else-if="error" class="state-box error">
      {{ error }}
    </div>

    <div v-else-if="course" class="course-layout">
      <main class="course-main">
        <button class="back-btn" @click="$emit('navigate', 'courses')">
          ← Back to courses
        </button>

        <div class="course-header">
          <p class="breadcrumb">Courses / {{ course.category }}</p>

          <h1>{{ course.title }}</h1>

          <p class="description">
            {{ course.description }}
          </p>

          <div class="course-meta">
            <span>{{ course.level }}</span>
            <span>{{ course.language }}</span>
            <span>{{ course.duration_hours }} hours</span>
            <span>{{ courseItems.length }} items</span>
          </div>

          <div v-if="isStudent" class="course-progress-box">
            <div class="course-progress-top">
              <span>Course progress</span>
              <strong>{{ courseProgress }}%</strong>
            </div>

            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: courseProgress + '%' }"></div>
            </div>
          </div>
        </div>

        <div v-if="
          selectedLesson?.lesson_type === 'video' &&
          (
            selectedLesson?.video_file_url ||
            selectedLesson?.video_file ||
            selectedLesson?.video_url
          )
        " class="video-card">
          <video v-if="selectedLesson.video_file_url || selectedLesson.video_file" class="lesson-video" controls
            :src="selectedLesson.video_file_url || selectedLesson.video_file"></video>

          <iframe v-else-if="selectedLesson.video_url" class="lesson-video"
            :src="formatVideoUrl(selectedLesson.video_url)" allowfullscreen></iframe>
        </div>

        <div class="lesson-content-card">
          <div class="tabs">
            <button v-for="(tab, index) in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === index }"
              @click="activeTab = index">
              {{ tab }}
            </button>
          </div>

          <section v-if="activeTab === 0">
            <div class="lesson-title-line">
              <h2>{{ selectedLesson?.title || course.title }}</h2>

              <button
                v-if="isStudent && selectedLesson?.lesson_type !== 'quiz' && selectedLesson?.lesson_type !== 'assignment'"
                class="lesson-complete-btn big" :class="{ completed: selectedLesson?.completed }"
                @click.stop="toggleLessonComplete(selectedLesson)">
                ✓
              </button>
            </div>

            <p class="lesson-text">
              {{ selectedLesson?.content || selectedLesson?.description || 'No content yet.' }}
            </p>

            <div v-if="selectedLesson?.lesson_type === 'assignment'" class="activity-box">
              <h3>Assignment</h3>

              <p>
                {{ selectedLesson.assignment?.description || selectedLesson.content }}
              </p>

              <p v-if="selectedLesson.assignment?.deadline">
                <strong>Deadline:</strong>
                {{ formatDate(selectedLesson.assignment.deadline) }}
              </p>

              <p>
                <strong>Max score:</strong>
                {{ selectedLesson.assignment?.max_score || 100 }}
              </p>
            </div>

            <div v-if="selectedLesson?.lesson_type === 'quiz'" class="activity-box">
              <h3>Quiz</h3>

              <p>
                {{ selectedLesson.quiz?.description || selectedLesson.content }}
              </p>

              <p>
                <strong>Passing score:</strong>
                {{ selectedLesson.quiz?.passing_score || 50 }}%
              </p>

              <p v-if="selectedLesson.quiz?.time_limit_minutes">
                <strong>Time limit:</strong>
                {{ selectedLesson.quiz.time_limit_minutes }} minutes
              </p>

              <p>
                <strong>Questions:</strong>
                {{ selectedLesson.quiz?.questions?.length || 0 }}
              </p>
            </div>
          </section>

          <section v-if="activeTab === 1">
            <h2>Resources</h2>
            <p class="lesson-text">Resources are not added yet.</p>
          </section>

          <section v-if="activeTab === 2">
            <h2>Discussions</h2>
            <p class="lesson-text">Discussion forum is not implemented yet.</p>
          </section>

          <section v-if="activeTab === 3">
            <template v-if="selectedLesson?.lesson_type === 'quiz'">
              <h2>{{ selectedLesson.quiz?.title || selectedLesson.title }}</h2>

              <div v-for="(question, qIndex) in selectedLesson.quiz?.questions || []" :key="question.id || qIndex"
                class="question-card">
                <h3>Question {{ qIndex + 1 }}</h3>
                <p>{{ question.text }}</p>

                <div v-for="option in question.options || []" :key="option.id || option.text" class="option">
                  {{ option.text }}
                </div>
              </div>
            </template>

            <p v-else class="lesson-text">
              Select a quiz from course content.
            </p>
          </section>
        </div>
      </main>

      <aside class="course-sidebar">
        <div class="sidebar-card">
          <h3>Course content</h3>

          <p class="small-muted">
            {{ courseItems.length }} items
          </p>

          <div class="lesson-list">
            <button v-for="(lesson, index) in courseItems" :key="lesson.uid" class="lesson-row" :class="{
              active: selectedLesson?.uid === lesson.uid,
              completed: lesson.completed
            }" @click="selectedLesson = lesson">
              <button v-if="isStudent && lesson.lesson_type !== 'quiz' && lesson.lesson_type !== 'assignment'"
                class="lesson-complete-btn" :class="{ completed: lesson.completed }"
                @click.stop="toggleLessonComplete(lesson)">
                ✓
              </button>

              <div v-else class="lesson-number">
                {{ index + 1 }}
              </div>

              <div class="lesson-info">
                <strong>{{ lesson.title }}</strong>
                <span>
                  {{ lessonTypeIcon(lesson.lesson_type) }}
                  {{ lessonTypeLabel(lesson.lesson_type) }}
                </span>
              </div>
            </button>
          </div>
        </div>

        <div class="sidebar-card">
          <h3>Course info</h3>

          <p>
            <strong>Teacher:</strong>
            {{ course.teacher_name || 'Teacher' }}
          </p>

          <p>
            <strong>Category:</strong>
            {{ course.category }}
          </p>

          <p>
            <strong>Certificate:</strong>
            {{ course.has_certificate ? 'Yes' : 'No' }}
          </p>

          <p>
            <strong>Price:</strong>
            {{ course.is_free ? 'Free' : course.price }}
          </p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

const route = useRoute()

defineEmits(['navigate', 'toast'])

const course = ref(null)
const quizzes = ref([])
const assignments = ref([])
const selectedLesson = ref(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref(0)
const courseProgress = ref(0)

const tabs = ['Overview', 'Resources', 'Discussions', 'Quiz']

const user = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    return {}
  }
})

const isStudent = computed(() => {
  return user.value?.role === 'student'
})

const courseItems = computed(() => {
  const lessons = (course.value?.lessons || []).map((lesson) => ({
    ...lesson,
    uid: `lesson-${lesson.id}`,
  }))

  const quizItems = quizzes.value.map((quiz) => ({
    uid: `quiz-${quiz.id}`,
    id: quiz.id,
    title: quiz.title,
    content: quiz.description || '',
    lesson_type: 'quiz',
    quiz,
  }))

  const assignmentItems = assignments.value.map((assignment) => ({
    uid: `assignment-${assignment.id}`,
    id: assignment.id,
    title: assignment.title,
    content: assignment.description || '',
    lesson_type: 'assignment',
    assignment,
  }))

  return [...lessons, ...quizItems, ...assignmentItems]
})

function calculateLocalCourseProgress() {
  const lessonsOnly = (course.value?.lessons || [])

  if (!lessonsOnly.length) {
    courseProgress.value = 0
    return
  }

  const completedLessons = lessonsOnly.filter((lesson) => lesson.completed).length

  courseProgress.value = Math.round(
    (completedLessons / lessonsOnly.length) * 100
  )

  course.value.progress = courseProgress.value
}

async function fetchCourse() {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('access_token')

    const headers = {
      Authorization: `Bearer ${token}`,
    }

    const [courseRes, quizzesRes, assignmentsRes] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/courses/${route.params.id}/`, {
        headers,
      }),
      axios.get('http://127.0.0.1:8000/api/quizzes/', {
        headers,
      }),
      axios.get('http://127.0.0.1:8000/api/assignments/', {
        headers,
      }),
    ])

    course.value = courseRes.data

    quizzes.value = (quizzesRes.data || []).filter(
      (quiz) => Number(quiz.course) === Number(route.params.id)
    )

    assignments.value = (assignmentsRes.data || []).filter(
      (assignment) => Number(assignment.course) === Number(route.params.id)
    )

    calculateLocalCourseProgress()

    selectedLesson.value = courseItems.value.length
      ? courseItems.value[0]
      : null
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load course.'
  } finally {
    loading.value = false
  }
}

async function toggleLessonComplete(lesson) {
  if (!lesson || lesson.lesson_type === 'quiz' || lesson.lesson_type === 'assignment') {
    return
  }

  try {
    const token = localStorage.getItem('access_token')

    const response = await axios.post(
      `http://127.0.0.1:8000/api/lessons/${lesson.id}/toggle_complete/`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    lesson.completed = response.data.lesson_completed

    const realLesson = course.value.lessons.find(
      (item) => Number(item.id) === Number(lesson.id)
    )

    if (realLesson) {
      realLesson.completed = response.data.lesson_completed
    }

    courseProgress.value = response.data.course_progress
    course.value.progress = response.data.course_progress
  } catch (err) {
    console.error(err)
    alert('Could not update lesson progress.')
  }
}

function lessonTypeLabel(type) {
  const labels = {
    video: 'Video lesson',
    reading: 'Reading lesson',
    quiz: 'Quiz',
    assignment: 'Assignment',
  }

  return labels[type] || 'Lesson'
}

function lessonTypeIcon(type) {
  const icons = {
    video: '▶',
    reading: '📖',
    quiz: '📝',
    assignment: '📋',
  }

  return icons[type] || '📘'
}

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleString()
}

function formatVideoUrl(url) {
  if (!url) return ''

  if (url.includes('youtube.com/watch?v=')) {
    const videoId = url.split('v=')[1]?.split('&')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }

  if (url.includes('youtu.be/')) {
    const videoId = url.split('youtu.be/')[1]?.split('?')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }

  return url
}

onMounted(fetchCourse)
</script>

<style scoped>
.course-detail-page {
  padding: 28px;
  background: #f7f6f2;
  min-height: 100vh;
}

.state-box {
  background: white;
  border-radius: 16px;
  padding: 24px;
  font-weight: 600;
}

.state-box.error {
  color: #dc2626;
}

.course-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.course-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.back-btn {
  width: fit-content;
  border: none;
  background: transparent;
  font-weight: 600;
  cursor: pointer;
}

.course-header {
  background: white;
  padding: 28px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
}

.breadcrumb {
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 10px;
}

.course-header h1 {
  font-size: 34px;
  margin: 0 0 12px;
}

.description {
  color: #4b5563;
  line-height: 1.6;
  max-width: 850px;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.course-meta span {
  background: #eef2ff;
  color: #4338ca;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.course-progress-box {
  margin-top: 22px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
}

.course-progress-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: #4b5563;
}

.course-progress-top strong {
  color: #111827;
}

.progress-bar {
  height: 9px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4f46e5;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.video-card {
  background: #111827;
  border-radius: 20px;
  min-height: 360px;
  overflow: hidden;
  display: flex;
}

.lesson-video {
  width: 100%;
  height: 360px;
  border: none;
  object-fit: cover;
}

.lesson-content-card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
}

.tabs {
  display: flex;
  gap: 10px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 22px;
  padding-bottom: 12px;
}

.tab-btn {
  border: none;
  background: transparent;
  padding: 9px 12px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.tab-btn.active {
  background: #eef2ff;
  color: #4f46e5;
}

.lesson-title-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.lesson-content-card h2 {
  margin: 0 0 14px;
}

.lesson-text {
  color: #4b5563;
  line-height: 1.8;
  white-space: pre-line;
}

.activity-box,
.question-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  margin-top: 18px;
}

.option {
  padding: 10px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  margin-top: 8px;
}

.course-sidebar {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.sidebar-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 20px;
}

.sidebar-card h3 {
  margin-top: 0;
}

.small-muted {
  color: #6b7280;
  font-size: 13px;
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lesson-row {
  width: 100%;
  border: 1px solid #e5e7eb;
  background: white;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 14px;
  text-align: left;
  cursor: pointer;
}

.lesson-row.active {
  border-color: #4f46e5;
  background: #eef2ff;
}

.lesson-row.completed {
  border-color: #10b981;
}

.lesson-number,
.lesson-complete-btn {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 800;
}

.lesson-number {
  background: #e5e7eb;
  color: #111827;
}

.lesson-complete-btn {
  border: 2px solid #4f46e5;
  background: white;
  color: #4f46e5;
  cursor: pointer;
  transition: all 0.2s ease;
}

.lesson-complete-btn:hover {
  transform: scale(1.06);
}

.lesson-complete-btn.completed {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.lesson-complete-btn.big {
  width: 38px;
  height: 38px;
  min-width: 38px;
}

.lesson-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lesson-info span {
  color: #6b7280;
  font-size: 12px;
}

@media (max-width: 1000px) {
  .course-layout {
    grid-template-columns: 1fr;
  }
}
</style>