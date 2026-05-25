<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Explore Courses</h1>
        <p class="page-sub">
          {{ filteredCourses.length }} courses available to enroll in
        </p>
      </div>
    </div>

    <div class="filters-bar">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input v-model="search" class="input search-input" placeholder="Search courses, topics, instructors…" />
      </div>

      <select v-model="filterCategory" class="input filter-select">
        <option value="">All categories</option>
        <option v-for="c in categories" :key="c" :value="c">
          {{ c }}
        </option>
      </select>

      <select v-model="filterLevel" class="input filter-select">
        <option value="">All levels</option>
        <option value="Beginner">Beginner</option>
        <option value="Intermediate">Intermediate</option>
        <option value="Advanced">Advanced</option>
      </select>

      <select v-model="filterPrice" class="input filter-select">
        <option value="">All pricing</option>
        <option value="free">Free</option>
        <option value="paid">Paid</option>
      </select>

      <div class="tab-bar">
        <button class="tab" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
          ⊞ Grid
        </button>

        <button class="tab" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
          ≡ List
        </button>
      </div>
    </div>

    <div v-if="activeFilters.length" class="active-filters">
      <span v-for="f in activeFilters" :key="f.key" class="filter-chip" @click="clearFilter(f.key)">
        {{ f.label }} ✕
      </span>

      <span class="clear-all" @click="clearAllFilters">
        Clear all
      </span>
    </div>

    <div v-if="loading">
      Loading courses...
    </div>

    <div v-else-if="error">
      {{ error }}
    </div>

    <div v-else-if="!filteredCourses.length" class="empty-state">
      <div class="empty-icon">🔍</div>
      <p class="empty-title">No courses found</p>
      <p class="empty-sub">Try adjusting your filters or search term.</p>
      <button class="btn btn-ghost" @click="clearAllFilters">
        Clear filters
      </button>
    </div>

    <div v-else-if="viewMode === 'grid'" class="course-grid">
      <div v-for="course in filteredCourses" :key="course.id" class="course-card" @click="openOverview(course)">
        <div class="course-thumb" :style="{ background: course.thumbBg }">
          <span class="thumb-emoji">{{ course.thumb }}</span>

          <span v-if="isEnrolled(course.id)" class="enrolled-badge">
            ✓ Enrolled
          </span>

          <span v-if="course.is_free" class="free-badge">
            Free
          </span>
        </div>

        <div class="course-body">
          <div class="course-tags">
            <span class="cat-badge">{{ course.category }}</span>

            <span class="level-badge" :class="'level-' + course.level.toLowerCase()">
              {{ course.level }}
            </span>
          </div>

          <h3 class="course-title">{{ course.title }}</h3>

          <p class="course-teacher">
            👤 {{ course.teacher }}
          </p>

          <div class="course-stats">
            <span>📖 {{ course.lessons_count }} lessons</span>
            <span>⏱ {{ course.duration_hours }}h</span>
            <span>👥 {{ course.enrolled_count.toLocaleString() }}</span>
          </div>

          <div class="course-footer">
            <div class="rating">
              <span class="star">★</span>
              <span class="rating-val">{{ course.rating }}</span>
              <span class="rating-count">({{ course.reviews }})</span>
            </div>

            <span v-if="course.is_free" class="price-free">Free</span>
            <span v-else class="price-paid">${{ course.price }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="course-list">
      <div v-for="course in filteredCourses" :key="course.id" class="list-row" @click="openOverview(course)">
        <div class="list-thumb" :style="{ background: course.thumbBg }">
          {{ course.thumb }}
        </div>

        <div class="list-info">
          <div class="list-tags">
            <span class="cat-badge">{{ course.category }}</span>

            <span class="level-badge" :class="'level-' + course.level.toLowerCase()">
              {{ course.level }}
            </span>

            <span v-if="isEnrolled(course.id)" class="enrolled-badge-sm">
              ✓ Enrolled
            </span>
          </div>

          <div class="list-title">
            {{ course.title }}
          </div>

          <div class="list-meta">
            👤 {{ course.teacher }} · 📖 {{ course.lessons_count }} lessons · ⏱ {{ course.duration_hours }}h
          </div>
        </div>

        <div class="list-right">
          <div class="rating">
            <span class="star">★</span>
            <span class="rating-val">{{ course.rating }}</span>
          </div>

          <div>
            <span v-if="course.is_free" class="price-free">Free</span>
            <span v-else class="price-paid">${{ course.price }}</span>
          </div>

          <button class="btn btn-primary btn-sm" @click.stop="openOverview(course)">
            {{ isEnrolled(course.id) ? 'Continue →' : 'View course' }}
          </button>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <div v-if="overlay.open" class="overlay-backdrop" @click.self="closeOverview">
        <div class="overlay-panel">
          <div class="overlay-hero" :style="{ background: overlay.course?.thumbBg }">
            <button class="close-btn" @click="closeOverview">
              ✕
            </button>

            <div class="hero-content">
              <div class="hero-emoji">
                {{ overlay.course?.thumb }}
              </div>

              <div>
                <div class="hero-tags">
                  <span class="cat-badge">
                    {{ overlay.course?.category }}
                  </span>

                  <span class="level-badge" :class="'level-' + (overlay.course?.level || '').toLowerCase()">
                    {{ overlay.course?.level }}
                  </span>

                  <span v-if="overlay.course?.is_free" class="free-badge-lg">
                    Free
                  </span>
                </div>

                <h2 class="hero-title">
                  {{ overlay.course?.title }}
                </h2>

                <p class="hero-teacher">
                  by {{ overlay.course?.teacher }}
                </p>

                <div class="hero-stats">
                  <span>
                    ⭐ {{ overlay.course?.rating }} ({{ overlay.course?.reviews }} reviews)
                  </span>
                  <span>
                    👥 {{ overlay.course?.enrolled_count?.toLocaleString() }} students
                  </span>
                  <span>
                    📖 {{ overlay.course?.lessons_count }} lessons
                  </span>
                  <span>
                    ⏱ {{ overlay.course?.duration_hours }} hours
                  </span>
                  <span>
                    🌐 {{ overlay.course?.language }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="overlay-body">
            <div class="overlay-cols">
              <div class="overlay-left">
                <div v-if="isEnrolled(overlay.course?.id)" class="enrolled-banner">
                  <span>✅ You are enrolled in this course</span>

                  <button class="btn btn-primary btn-sm" @click="goToCourse(overlay.course.id)">
                    Continue learning →
                  </button>
                </div>

                <div class="section">
                  <h3 class="section-title">About this course</h3>
                  <p class="course-desc">
                    {{ overlay.course?.description }}
                  </p>
                </div>

                <div v-if="overlay.course?.objectives?.length" class="section">
                  <h3 class="section-title">What you'll learn</h3>

                  <div class="objectives-grid">
                    <div v-for="(obj, i) in overlay.course.objectives" :key="i" class="objective-item">
                      <span class="obj-check">✓</span>
                      <span>{{ obj }}</span>
                    </div>
                  </div>
                </div>

                <div class="section">
                  <h3 class="section-title">Course content</h3>

                  <p class="curriculum-sub">
                    {{ overlay.course?.lessons_count }} lessons ·
                    {{ overlay.course?.duration_hours }} total hours
                  </p>

                  <div v-if="overlay.course?.curriculum_preview?.length" class="curriculum-list">
                    <div v-for="(lesson, i) in overlay.course.curriculum_preview" :key="i" class="curriculum-row"
                      :class="{ locked: !lesson.is_preview }">
                      <span class="curr-icon">
                        {{ lessonIcon(lesson.type) }}
                      </span>

                      <span class="curr-title">
                        {{ lesson.title }}
                      </span>

                      <span class="curr-right">
                        <span v-if="lesson.is_preview" class="preview-tag">
                          Preview
                        </span>

                        <span v-else class="lock-icon">
                          🔒
                        </span>

                        <span class="curr-meta">
                          {{ lesson.meta }}
                        </span>
                      </span>
                    </div>
                  </div>

                  <p v-if="!isEnrolled(overlay.course?.id)" class="enroll-hint">
                    Enroll to unlock all {{ overlay.course?.lessons_count }} lessons
                  </p>

                  <p v-else class="enroll-hint">
                    You already have access to all lessons.
                  </p>
                </div>
              </div>

              <div class="overlay-right">
                <div class="enroll-card" :class="{ 'already-enrolled': isEnrolled(overlay.course?.id) }">
                  <div class="enroll-price">
                    <span v-if="overlay.course?.is_free" class="price-free-lg">
                      Free
                    </span>

                    <template v-else>
                      <span class="price-main">
                        ${{ overlay.course?.price }}
                      </span>

                      <span v-if="overlay.course?.original_price" class="price-strike">
                        ${{ overlay.course?.original_price }}
                      </span>
                    </template>
                  </div>

                  <button class="btn btn-primary enroll-btn" :disabled="enrolling"
                    @click="handleEnrollClick(overlay.course)">
                    <span v-if="enrolling" class="spinner"></span>

                    {{
                      isEnrolled(overlay.course?.id)
                        ? 'Enrolled ✓'
                        : enrolling
                          ? 'Enrolling…'
                          : overlay.course?.is_free
                            ? 'Enroll for free'
                            : 'Enroll now'
                    }}
                  </button>

                  <p class="enroll-note">
                    Full lifetime access · No expiry
                  </p>

                  <div v-if="isEnrolled(overlay.course?.id)" class="enrolled-progress-row">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: enrolledProgress(overlay.course?.id) + '%' }"></div>
                    </div>

                    <span class="progress-pct">
                      {{ enrolledProgress(overlay.course?.id) }}%
                    </span>
                  </div>

                  <div class="includes">
                    <p class="includes-title">
                      This course includes:
                    </p>

                    <div class="includes-list">
                      <div class="includes-item">
                        <span>🎬</span>
                        {{ overlay.course?.duration_hours }} hours of video
                      </div>

                      <div class="includes-item">
                        <span>📝</span>
                        Assignments &amp; quizzes
                      </div>

                      <div class="includes-item">
                        <span>📱</span>
                        Access on mobile &amp; desktop
                      </div>

                      <div v-if="overlay.course?.has_certificate" class="includes-item">
                        <span>🏆</span>
                        Certificate of completion
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="toast">
      <div v-if="toast.visible" class="toast">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000/api'

const courses = ref([])
const loading = ref(false)
const error = ref('')

const search = ref('')
const filterCategory = ref('')
const filterLevel = ref('')
const filterPrice = ref('')
const viewMode = ref('grid')

const enrolling = ref(false)
const enrolledMap = reactive({})

const overlay = reactive({
  open: false,
  course: null
})

const toast = reactive({
  visible: false,
  message: ''
})

const categories = computed(() => {
  return [...new Set(courses.value.map(course => course.category).filter(Boolean))]
})

const filteredCourses = computed(() => {
  return courses.value.filter(course => {
    const term = search.value.toLowerCase()

    const matchesSearch =
      !term ||
      course.title.toLowerCase().includes(term) ||
      course.description.toLowerCase().includes(term) ||
      course.teacher.toLowerCase().includes(term) ||
      course.category.toLowerCase().includes(term)

    const matchesCategory =
      !filterCategory.value ||
      course.category === filterCategory.value

    const matchesLevel =
      !filterLevel.value ||
      course.level === filterLevel.value

    const matchesPrice =
      !filterPrice.value ||
      (filterPrice.value === 'free' && course.is_free) ||
      (filterPrice.value === 'paid' && !course.is_free)

    return matchesSearch && matchesCategory && matchesLevel && matchesPrice
  })
})

const activeFilters = computed(() => {
  const filters = []

  if (filterCategory.value) {
    filters.push({
      key: 'category',
      label: filterCategory.value
    })
  }

  if (filterLevel.value) {
    filters.push({
      key: 'level',
      label: filterLevel.value
    })
  }

  if (filterPrice.value) {
    filters.push({
      key: 'price',
      label: filterPrice.value === 'free' ? 'Free only' : 'Paid only'
    })
  }

  return filters
})

function normalizeLevel(level) {
  if (!level) return 'Beginner'

  const value = String(level).toLowerCase()

  if (value === 'intermediate') return 'Intermediate'
  if (value === 'advanced') return 'Advanced'

  return 'Beginner'
}

function mapCourse(course) {
  return {
    id: course.id,
    title: course.title || '',
    description: course.description || '',
    category: course.category || 'General',
    level: normalizeLevel(course.level),
    language: course.language || 'English',
    duration_hours: course.duration_hours || 0,
    lessons_count: course.lessons_count || 0,
    enrolled_count: course.enrolled_count || 0,
    rating: course.rating || 0,
    reviews: course.reviews || 0,
    is_free: course.is_free,
    price: course.price || 0,
    original_price: course.original_price || null,
    has_certificate: course.has_certificate || false,
    teacher: course.teacher_name || course.teacher || 'Teacher',
    is_enrolled: course.is_enrolled || false,
    progress_percentage: course.progress_percentage || 0,
    objectives: course.objectives || [],
    curriculum_preview: course.curriculum_preview || [],
    thumb: '📚',
    thumbBg: '#EEF1FF'
  }
}

async function fetchCourses() {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('access_token')

    const response = await axios.get(`${API_BASE}/courses/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    courses.value = response.data.map(mapCourse)

    courses.value.forEach(course => {
      if (course.is_enrolled) {
        enrolledMap[course.id] = course.progress_percentage || 0
      }
    })
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load courses.'
  } finally {
    loading.value = false
  }
}

function openOverview(course) {
  overlay.course = course
  overlay.open = true
}

function closeOverview() {
  overlay.open = false
  overlay.course = null
}

function isEnrolled(id) {
  if (!id) return false
  return id in enrolledMap
}

function enrolledProgress(id) {
  if (!id) return 0
  return enrolledMap[id] || 0
}

function handleEnrollClick(course) {
  if (!course) return

  if (isEnrolled(course.id)) {
    showToast('Already enrolled.')
    return
  }

  enroll(course)
}

async function enroll(course) {
  if (!course) return

  enrolling.value = true

  try {
    const token = localStorage.getItem('access_token')

    const response = await axios.post(
      `${API_BASE}/student/courses/${course.id}/enroll/`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    course.is_enrolled = true
    enrolledMap[course.id] = course.progress_percentage || 0

    if (response.data?.detail === 'Already enrolled.') {
      showToast('Already enrolled.')
    } else {
      showToast(`Enrolled in "${course.title}" 🎉`)
    }
  } catch (err) {
    console.error(err)

    if (err.response?.data?.detail) {
      showToast(err.response.data.detail)
    } else {
      showToast('Failed to enroll.')
    }
  } finally {
    enrolling.value = false
  }
}

function goToLearn(course) {
  if (!course) return
  closeOverview()
  router.push(`/courses/${course.id}/learn`)
}

function clearFilter(key) {
  if (key === 'category') filterCategory.value = ''
  if (key === 'level') filterLevel.value = ''
  if (key === 'price') filterPrice.value = ''
}

function clearAllFilters() {
  search.value = ''
  filterCategory.value = ''
  filterLevel.value = ''
  filterPrice.value = ''
}

function lessonIcon(type) {
  if (type === 'video') return '▶'
  if (type === 'reading') return '📄'
  if (type === 'quiz') return '📝'
  if (type === 'assignment') return '📋'
  return '📚'
}

function showToast(message) {
  toast.message = message
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 3000)
}

function goToCourse(id) {
  closeOverview()
  router.push(`/courses/${id}`)
}

onMounted(() => {
  fetchCourses()
})
</script>

<style src="./src/assets/ExploreCourses.css"></style>