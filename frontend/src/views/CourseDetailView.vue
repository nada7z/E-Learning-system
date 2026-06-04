<template>
  <div class="course-detail-page">

    <!-- Loading -->
    <div v-if="loading" class="state-box">
      <div class="spinner-lg"></div>
      <p>Loading course…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-box state-error">
      <span class="state-icon">⚠️</span>
      <p>{{ error }}</p>
    </div>

    <!-- Content -->
    <div v-else-if="course" class="course-layout">

      <!-- ═══════════════ MAIN ═══════════════ -->
      <main class="course-main">

        <!-- Back + breadcrumb -->
        <div class="topnav">
          <span class="breadcrumb">Courses / {{ course.category }}</span>
        </div>

        <!-- Course header -->
        <div class="course-header">
          <h1 class="course-title">{{ course.title }}</h1>
          <p class="course-description">{{ course.description }}</p>

          <div class="course-meta-pills">
            <span class="meta-pill">{{ course.level }}</span>
            <span class="meta-pill">{{ course.language }}</span>
            <span class="meta-pill">⏱ {{ course.duration_hours }}h</span>
            <span class="meta-pill">📖 {{ courseItems.length }} items</span>
          </div>

          <!-- Student progress -->
          <div v-if="isStudent" class="progress-box">
            <div class="progress-top">
              <span class="progress-label">Your progress</span>
              <strong class="progress-pct">{{ courseProgress }}%</strong>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: courseProgress + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Video player -->
        <div v-if="selectedLesson?.lesson_type === 'video'" class="video-wrap">
          <video v-if="selectedLesson.video_file_url || selectedLesson.video_file" class="lesson-video" controls
            :src="selectedLesson.video_file_url || selectedLesson.video_file"></video>

          <iframe v-else-if="selectedLesson.content || selectedLesson.video_url" class="lesson-video"
            :src="formatVideoUrl(selectedLesson.content || selectedLesson.video_url)" allowfullscreen></iframe>
        </div>

        <!-- Tabs + content card -->
        <div class="content-card">

          <!-- Tab bar -->
          <div class="tab-bar">
            <button v-for="(tab, index) in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === index }"
              @click="activeTab = index">{{ tab }}</button>
          </div>

          <!-- ── Overview tab ── -->
          <section v-if="activeTab === 0" class="tab-section">

            <div class="lesson-heading-row">
              <h2 class="lesson-heading">{{ selectedLesson?.title || course.title }}</h2>
              <button
                v-if="isStudent && selectedLesson && selectedLesson.lesson_type !== 'quiz' && selectedLesson.lesson_type !== 'assignment'"
                class="complete-icon-btn" :class="{ completed: isCompleted(selectedLesson) }"
                @click="markCompleted(selectedLesson)">
                <CheckIcon :size="18" />
              </button>
            </div>

            <p v-if="selectedLesson?.lesson_type !== 'video'" class="lesson-body">
              {{ selectedLesson?.content || selectedLesson?.description || selectedLesson?.quiz?.description ||
                selectedLesson?.assignment?.description || 'No content yet.' }}
            </p>

            <button
              v-if="isStudent && selectedLesson && selectedLesson.lesson_type !== 'quiz' && selectedLesson.lesson_type !== 'assignment'"
              class="btn btn-primary" :disabled="isCompleted(selectedLesson)" @click="markCompleted(selectedLesson)">
              {{ isCompleted(selectedLesson) ? '✓ Completed' : 'Mark as completed' }}
            </button>

            <!-- Assignment block -->
            <div v-if="selectedLesson?.lesson_type === 'assignment'" class="activity-card">
              <div class="activity-header">
                <span class="activity-type-badge assignment-badge">📋 Assignment</span>
                <div class="activity-meta">
                  <span v-if="selectedLesson.assignment?.deadline">
                    ⏰ Due {{ formatDate(selectedLesson.assignment.deadline) }}
                  </span>
                  <span>🏆 {{ selectedLesson.assignment?.max_score || 100 }} pts max</span>
                </div>
              </div>

              <p class="activity-desc">
                {{ selectedLesson.assignment?.description || selectedLesson.content }}
              </p>

              <div v-if="isStudent" class="field">
                <label class="field-label">Your answer</label>
                <textarea v-model="assignmentForm.text_answer" class="field-textarea" rows="5"
                  placeholder="Write your answer here…"></textarea>
              </div>

              <div v-if="isStudent" class="field">
                <label class="field-label">Upload file <span class="optional">(optional)</span></label>
                <label class="file-drop">
                  <input class="file-input-hidden" type="file" @change="handleAssignmentFile" />
                  <span class="file-drop-inner">
                    <template v-if="assignmentForm.file_name">
                      ✓ {{ assignmentForm.file_name }}
                    </template>

                    <template v-else>
                      📂 Click to browse or drag a file here
                    </template>
                  </span>
                </label>
              </div>

              <button v-if="isStudent" class="btn btn-primary" :disabled="submitting || isCompleted(selectedLesson)"
                @click="submitAssignment">
                <span v-if="submitting" class="spinner-sm"></span>
                {{ isCompleted(selectedLesson) ? '✓ Submitted' : submitting ? 'Submitting…' : 'Submit assignment' }}
              </button>
            </div>

            <!-- Quiz block -->
            <div v-if="selectedLesson?.lesson_type === 'quiz' || selectedLesson?.lesson_type === 'final_exam'"
              class="activity-card">
              <div class="activity-header">
                <span class="activity-type-badge quiz-badge">
                  {{ selectedLesson.quiz?.is_final_exam ? '📝 Final Exam' : '📝 Quiz' }}
                </span>
                <div class="activity-meta">
                  <span>🏆 Pass {{ selectedLesson.quiz?.passing_score || 50 }}%</span>
                </div>
              </div>

              <p class="activity-desc">
                {{ selectedLesson.quiz?.description || selectedLesson.content }}
              </p>

              <div v-for="(question, qIndex) in selectedLesson.quiz?.questions || []" :key="question.id"
                class="question-block">
                <div class="q-meta-row">
                  <span class="q-num">Q{{ qIndex + 1 }}</span>
                </div>
                <p class="q-text">{{ question.text }}</p>

                <textarea v-if="question.question_type === 'short_answer'"
                  v-model="quizAnswers[question.id].text_answer" class="field-textarea" rows="3"
                  placeholder="Write your answer…"></textarea>

                <div v-else class="options-list">
                  <label v-for="option in question.options || []" :key="option.id" class="option-label"
                    :class="{ selected: quizAnswers[question.id]?.selected_option === option.id }">
                    <input type="radio" :name="`question-${question.id}`" :value="option.id"
                      v-model="quizAnswers[question.id].selected_option"" />
                    <span>{{ option.text }}</span>
                  </label>
                </div>
              </div>

              <button v-if="isStudent" class="btn btn-primary" :disabled="submitting || isCompleted(selectedLesson)"
                      @click="submitQuiz">
                    <span v-if="submitting" class="spinner-sm"></span>
                    {{ isCompleted(selectedLesson) ? '✓ Quiz submitted' : submitting ? 'Submitting…' : 'Submit quiz' }}
                    </button>
                </div>
          </section>

          <!-- ── Resources tab ── -->
          <section v-if="activeTab === 1" class="tab-section">
            <h2 class="section-heading">Resources</h2>
            <p class="empty-text">No resources have been added yet.</p>
          </section>

          <!-- ── Discussion tab ── -->
          <section v-if="activeTab === 2" class="tab-section">
            <h2 class="section-heading">Discussion</h2>
            <p class="section-sub">Ask questions and get answers from your teacher and classmates.</p>

            <!-- Compose -->
            <div class="compose-box">
              <div class="compose-avatar">You</div>
              <div class="compose-right">
                <textarea v-model="discussionText" class="compose-textarea"
                  placeholder="Ask a question or share something with the class…" rows="3"></textarea>
                <div class="compose-footer">
                  <button class="btn btn-primary btn-sm" :disabled="discussionLoading || !discussionText.trim()"
                    @click="submitDiscussion">
                    <span v-if="discussionLoading" class="spinner-sm"></span>
                    {{ discussionLoading ? 'Posting…' : 'Post message' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Messages -->
            <div v-if="discussionMessages.length" class="discussion-feed">
              <div v-for="message in discussionMessages" :key="message.id" class="discussion-msg">
                <div class="msg-avatar" :class="{ 'avatar-teacher': message.is_teacher }">
                  {{ message.author_name?.charAt(0) ?? '?' }}
                </div>
                <div class="msg-body">
                  <div class="msg-meta">
                    <span class="msg-author">{{ message.author_name }}</span>
                    <span v-if="message.is_teacher" class="teacher-chip">Teacher</span>
                    <span class="msg-time">{{ new Date(message.created_at).toLocaleString() }}</span>
                  </div>
                  <p class="msg-text">{{ message.message }}</p>
                </div>
              </div>
            </div>

            <div v-else class="empty-feed">
              <span class="empty-feed-icon">💬</span>
              <p>No messages yet. Start the discussion!</p>
            </div>
          </section>

          <!-- ── Reviews tab ── -->
          <section v-if="activeTab === 3" class="tab-section">
            <h2 class="section-heading">Reviews</h2>
            <p class="section-sub">What students are saying about this course.</p>

            <!-- Review form -->
            <div v-if="canReviewCourse" class="review-form-card">
              <h3 class="review-form-title">{{ myReview ? 'Update your review' : 'Leave a review' }}</h3>
              <div class="star-picker">
                <button v-for="star in 5" :key="star" type="button" class="star-btn"
                  :class="{ lit: star <= reviewForm.rating }" @click="reviewForm.rating = star">★</button>
              </div>
              <textarea v-model="reviewForm.review" class="field-textarea" rows="4"
                placeholder="Share your experience with this course…"></textarea>
              <button class="btn btn-primary btn-sm" @click="submitReview">
                {{ myReview ? 'Update review' : 'Submit review' }}
              </button>
            </div>

            <p v-else-if="isStudent" class="empty-text">
              Complete this course to leave a review.
            </p>

            <!-- Reviews list -->
            <div v-if="reviews.length" class="reviews-list">
              <div v-for="review in reviews" :key="review.id" class="review-card">
                <div class="review-top">
                  <div class="review-avatar">
                    {{ review.student_name?.charAt(0) ?? '?' }}
                  </div>
                  <div class="review-author-info">
                    <span class="review-author">{{ review.student_name }}</span>
                    <span class="review-stars">
                      <span v-for="s in 5" :key="s" class="review-star" :class="{ lit: s <= review.rating }">★</span>
                    </span>
                  </div>
                </div>
                <p class="review-text">{{ review.review }}</p>
              </div>
            </div>

            <div v-else class="empty-feed">
              <span class="empty-feed-icon">⭐</span>
              <p>No reviews yet. Be the first!</p>
            </div>
          </section>

        </div><!-- /content-card -->
      </main>

      <!-- ═══════════════ SIDEBAR ═══════════════ -->
      <aside class="course-sidebar">

        <!-- Lesson list -->
        <div class="sidebar-card">
          <div class="sidebar-card-header">
            <h3 class="sidebar-card-title">Course content</h3>
            <span class="sidebar-card-meta">{{ courseItems.length }} items</span>
          </div>

          <div class="lesson-list">
            <div v-for="(lesson, index) in courseItems" :key="lesson.uid" class="lesson-row"
              :class="{ active: selectedLesson?.uid === lesson.uid, completed: isCompleted(lesson) }"
              @click="selectLesson(lesson)">
              <div class="lesson-num"
                :class="{ 'num-done': isCompleted(lesson), 'num-active': selectedLesson?.uid === lesson.uid }">
                <span v-if="isStudent">
                  <CheckIcon v-if="isCompleted(lesson)" :size="13" />
                  <span v-else>{{ index + 1 }}</span>
                </span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="lesson-info">
                <span class="lesson-info-title">{{ lesson.title }}</span>
                <span class="lesson-info-type">
                  {{ lessonTypeIcon(lesson.lesson_type) }} {{ lessonTypeLabel(lesson.lesson_type) }}
                </span>
              </div>
              <span v-if="selectedLesson?.uid === lesson.uid" class="active-pip"></span>
            </div>
          </div>
        </div>

        <!-- Course info -->
        <div class="sidebar-card">
          <div class="sidebar-card-header">
            <h3 class="sidebar-card-title">Course info</h3>
          </div>
          <div class="info-list">
            <div class="info-row">
              <span class="info-key">Teacher</span>
              <span class="info-val">{{ course.teacher_name || 'Teacher' }}</span>
            </div>
            <div class="info-row">
              <span class="info-key">Category</span>
              <span class="info-val">{{ course.category }}</span>
            </div>
            <div class="info-row">
              <span class="info-key">Certificate</span>
              <span class="info-val">{{ course.has_certificate ? '✓ Yes' : 'No' }}</span>
            </div>
            <div class="info-row">
              <span class="info-key">Price</span>
              <span class="info-val">{{ course.is_free ? 'Free' : course.price }}</span>
            </div>
          </div>
        </div>

      </aside>

      <!-- Toast -->
      <div v-if="toast" class="toast">{{ toast }}</div>

    </div><!-- /course-layout -->
  </div><!-- /course-detail-page -->

  <!-- Completion modal -->
  <Transition name="modal">
    <div v-if="showCompletionModal" class="completion-backdrop">
      <div class="completion-modal">
        <div class="completion-emoji">🎉</div>
        <h2 class="completion-title">Course Completed!</h2>
        <p class="completion-sub">
          Congratulations! You've successfully completed this course and earned your certificate.
        </p>
        <div class="completion-actions">
          <button class="btn btn-ghost" @click="showCompletionModal = false">Stay here</button>
          <button class="btn btn-primary" @click="$router.push({ name: 'Certificates' })">View Certificate →</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import {
  CheckIcon,
} from 'lucide-vue-next'

const route = useRoute()

defineEmits(['navigate', 'toast'])

const course = ref(null)
const quizzes = ref([])
const assignments = ref([])
const selectedLesson = ref(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref(0)
const submitting = ref(false)
const toast = ref('')
const showCompletionModal = ref(false)

const completedItems = ref([])
const quizAnswers = ref({})
const reviews = ref([])
const myReview = ref(null)

const discussionMessages = ref([])
const discussionText = ref('')
const discussionLoading = ref(false)

const reviewForm = reactive({
  rating: 5,
  review: '',
})

const canReviewCourse = computed(() => {
  return isStudent.value && courseProgress.value >= 100
})

const assignmentForm = reactive({
  text_answer: '',
  file: null,
  file_name: '',
})

const tabs = ['Overview', 'Resources', 'Discussions', 'Reviews']

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

  const normalQuizzes = quizzes.value
    .filter((quiz) => !quiz.is_final_exam)
    .map((quiz) => ({
      uid: `quiz-${quiz.id}`,
      id: quiz.id,
      title: quiz.title,
      content: quiz.description || '',
      lesson_type: 'quiz',
      quiz,
    }))

  const finalExams = quizzes.value
    .filter((quiz) => quiz.is_final_exam)
    .map((quiz) => ({
      uid: `quiz-${quiz.id}`,
      id: quiz.id,
      title: quiz.title || 'Final Exam',
      content: quiz.description || '',
      lesson_type: 'final_exam',
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

  return [...lessons, ...normalQuizzes, ...assignmentItems, ...finalExams]
})

const courseProgress = computed(() => {
  if (!courseItems.value.length) return 0

  return Math.round(
    (completedItems.value.length / courseItems.value.length) * 100
  )
})

function authHeaders(extraHeaders = {}) {
  const token = localStorage.getItem('access_token')

  return {
    headers: {
      Authorization: `Bearer ${token}`,
      ...extraHeaders,
    },
  }
}

function progressKey() {
  return `course-progress-${route.params.id}`
}

function lessonTypeLabel(type) {
  const labels = {
    video: 'Video lesson',
    text: 'Text lesson',
    document: 'Document',
    quiz: 'Quiz',
    assignment: 'Assignment',
    exam: 'Final exam',
    final_exam: 'Final exam',
  }

  return labels[type] || 'Lesson'
}

function loadProgress() {
  const saved = localStorage.getItem(progressKey())
  completedItems.value = saved ? JSON.parse(saved) : []
}

function saveProgress() {
  localStorage.setItem(
    progressKey(),
    JSON.stringify(completedItems.value)
  )
}

function isCompleted(item) {
  return completedItems.value.includes(item?.uid)
}

async function markCompleted(item) {
  if (!item?.uid) return

  if (!completedItems.value.includes(item.uid)) {
    completedItems.value.push(item.uid)
    saveProgress()
  }

  const progress = courseProgress.value || 0

  console.log('COURSE PROGRESS:', progress)

  if (progress >= 100) {
    if (isStudent.value) {
      await generateCertificate()
      showCompletionModal.value = true
      showToast('🎉 Congratulations! Certificate unlocked.')
    }
    return
  }

  showToast('Marked as completed ✅')
}

function selectLesson(lesson) {
  console.log('SELECTED LESSON:', lesson)

  selectedLesson.value = lesson
  activeTab.value = 0

  if (lesson.lesson_type === 'quiz' || lesson.lesson_type === 'final_exam') {
    initQuizAnswers(lesson.quiz)
  }

  if (lesson.lesson_type === 'assignment') {
    assignmentForm.text_answer = ''
    assignmentForm.file = null
    assignmentForm.file_name = ''
  }
}

async function fetchCourse() {
  loading.value = true
  error.value = ''

  try {
    const [courseRes, quizzesRes, assignmentsRes] = await Promise.all([
      axios.get(
        `http://127.0.0.1:8000/api/courses/${route.params.id}/`,
        authHeaders()
      ),
      axios.get(
        'http://127.0.0.1:8000/api/quizzes/',
        authHeaders()
      ),
      axios.get(
        'http://127.0.0.1:8000/api/assignments/',
        authHeaders()
      ),
    ])

    course.value = courseRes.data

    quizzes.value = (quizzesRes.data || []).filter(
      (quiz) => Number(quiz.course) === Number(route.params.id)
    )

    assignments.value = (assignmentsRes.data || []).filter(
      (assignment) => Number(assignment.course) === Number(route.params.id)
    )

    loadProgress()

    selectedLesson.value = courseItems.value.length
      ? courseItems.value[0]
      : null

    if (selectedLesson.value?.lesson_type === 'quiz') {
      initQuizAnswers(selectedLesson.value.quiz)
    }
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load course.'
  } finally {
    loading.value = false
  }
}

async function fetchReviews() {
  try {
    const res = await axios.get(
      `http://127.0.0.1:8000/api/courses/${route.params.id}/reviews/`,
      authHeaders()
    )

    reviews.value = res.data.reviews || []
    myReview.value = res.data.my_review

    if (myReview.value) {
      reviewForm.rating = myReview.value.rating
      reviewForm.review = myReview.value.review || ''
    }
  } catch (err) {
    console.error(err)
  }
}

async function submitReview() {
  if (!canReviewCourse.value) {
    showToast('Complete and pass the course first.')
    return
  }

  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/courses/${route.params.id}/reviews/`,
      {
        rating: reviewForm.rating,
        review: reviewForm.review,
      },
      authHeaders()
    )

    myReview.value = res.data
    await fetchReviews()
    showToast('Review saved ⭐')
  } catch (err) {
    console.error(err)
    showToast(err.response?.data?.detail || 'Failed to submit review')
  }
}

async function fetchDiscussions() {
  try {
    const res = await axios.get(
      `http://127.0.0.1:8000/api/courses/${route.params.id}/discussions/`,
      authHeaders()
    )

    discussionMessages.value = res.data || []
  } catch (err) {
    console.error(err)
  }
}

async function submitDiscussion() {
  if (!discussionText.value.trim()) return

  discussionLoading.value = true

  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/courses/${route.params.id}/discussions/`,
      {
        message: discussionText.value,
      },
      authHeaders()
    )

    discussionMessages.value.push(res.data)
    discussionText.value = ''
  } catch (err) {
    console.error(err)
    toast.value = 'Could not post message.'
  } finally {
    discussionLoading.value = false
  }
}

function initQuizAnswers(quiz) {
  quizAnswers.value = {}

    ; (quiz?.questions || []).forEach((question) => {
      if (!question?.id) return

      quizAnswers.value[question.id] = {
        question: question.id,
        selected_option: null,
        text_answer: '',
      }
    })
}

async function submitQuiz() {
  if (!selectedLesson.value?.quiz) return

  const quiz = selectedLesson.value.quiz

  if (!Object.keys(quizAnswers.value).length) {
    initQuizAnswers(quiz)
  }

  const payload = {
    quiz: quiz.id,
    answers: Object.values(quizAnswers.value).map((answer) => ({
      question: answer.question,
      selected_option: answer.selected_option || null,
      text_answer: answer.text_answer || '',
    })),
  }

  submitting.value = true

  try {
    const res = await axios.post(
      'http://127.0.0.1:8000/api/quiz-attempts/',
      payload,
      authHeaders()
    )

    const score = Number(res.data.score || 0)
    const passingScore = Number(quiz.passing_score || 50)

    if (score >= passingScore) {
      await markCompleted(selectedLesson.value)
      showToast(`Quiz passed ✅ Score: ${score.toFixed(1)}%`)
    } else {
      showToast(`Quiz failed ❌ Score: ${score.toFixed(1)}%`)
    }
  } catch (err) {
    console.error(err)
    showToast('Failed to submit quiz')
  } finally {
    submitting.value = false
  }
}

function handleAssignmentFile(event) {
  const file = event.target.files?.[0]

  if (!file) return

  assignmentForm.file = file
  assignmentForm.file_name = file.name
}

async function submitAssignment() {
  if (!selectedLesson.value?.assignment) return

  if (!assignmentForm.text_answer.trim() && !assignmentForm.file) {
    showToast('Write an answer or upload a file')
    return
  }

  const data = new FormData()
  data.append('assignment', selectedLesson.value.assignment.id)
  data.append('text_answer', assignmentForm.text_answer)

  if (assignmentForm.file) {
    data.append('file', assignmentForm.file)
  }

  submitting.value = true

  try {
    await axios.post(
      'http://127.0.0.1:8000/api/submissions/',
      data,
      authHeaders({
        'Content-Type': 'multipart/form-data',
      })
    )

    await markCompleted(selectedLesson.value)

    assignmentForm.text_answer = ''
    assignmentForm.file = null

    showToast('Assignment submitted')
  } catch (err) {
    console.error(err)
    showToast('Failed to submit assignment')
  } finally {
    submitting.value = false
  }
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

function showToast(message) {
  toast.value = message

  setTimeout(() => {
    toast.value = ''
  }, 2600)
}

function canEarnCertificate() {
  return courseItems.value.every((item) => {
    if (item.lesson_type === 'quiz') {
      return completedItems.value.includes(item.uid)
    }

    if (item.lesson_type === 'assignment') {
      return completedItems.value.includes(item.uid)
    }

    return completedItems.value.includes(item.uid)
  })
}

async function generateCertificate() {
  if (!isStudent.value) return

  try {
    await axios.post(
      'http://127.0.0.1:8000/api/certificates/generate/',
      {
        course_id: course.value.id,
      },
      authHeaders()
    )
  } catch (err) {
    console.error(err)
    showToast('Course completed, but certificate was not generated.')
  }
}

async function checkCertificateOnLoad() {
  if (!isStudent.value) return

  if (courseProgress.value >= 100) {
    console.log('COURSE ALREADY 100%, GENERATING CERTIFICATE...')
    await generateCertificate()
  }
}

function getYouTubeEmbedUrl(url) {
  if (!url) return ''

  const match = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&?]+)/
  )

  return match ? `https://www.youtube.com/embed/${match[1]}` : ''
}

onMounted(async () => {
  await fetchCourse()
  await fetchReviews()
  await fetchDiscussions()
  await checkCertificateOnLoad()
})
</script>

<style src="/src/assets/CourseDetailView.css" scoped></style>