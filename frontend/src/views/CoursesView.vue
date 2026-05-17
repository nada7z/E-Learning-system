<template>
  <div class="page">
    <div class="page-header flex items-center justify-between">
      <div>
        <h1 class="page-title">
          {{ role === 'student' ? 'My Courses' : role === 'teacher' ? 'Manage Courses' : 'All Courses' }}
        </h1>

        <p class="page-sub">
          {{ courses.length }} courses total
        </p>
      </div>

      <button
        v-if="role !== 'student'"
        class="btn btn-primary"
        @click="goToCreateCourse"
      >
        + New Course
      </button>
    </div>

    <div style="display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap;align-items:center">
      <div style="position:relative;flex:1;min-width:200px">
        <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--text3)">🔍</span>

        <input
          v-model="search"
          style="width:100%;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 14px 10px 36px;font-size:14px;color:var(--text)"
          placeholder="Search courses…"
        />
      </div>

      <select
        v-model="selectedCategory"
        style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 14px;font-size:14px;color:var(--text)"
      >
        <option value="">All Categories</option>
        <option>Development</option>
        <option>Design</option>
        <option>Data Science</option>
        <option>AI / Machine Learning</option>
        <option>Marketing</option>
        <option>DevOps</option>
        <option>Business</option>
      </select>

      <div class="tab-bar" style="margin:0">
        <div
          class="tab"
          :class="{ active: viewMode === 'grid' }"
          @click="viewMode = 'grid'"
        >
          Grid
        </div>

        <div
          class="tab"
          :class="{ active: viewMode === 'list' }"
          @click="viewMode = 'list'"
        >
          List
        </div>
      </div>
    </div>

    <div v-if="loading">
      Loading courses...
    </div>

    <div v-else-if="error">
      {{ error }}
    </div>

    <div v-else-if="filteredCourses.length === 0">
      No courses found.
    </div>

    <div v-else-if="viewMode === 'grid'" class="course-grid">
      <div
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-card"
        @click="goToCourse(course.id)"
      >
        <div class="course-thumb" :style="{ background: '#EEF1FF' }">
          <span>📚</span>
        </div>

        <div class="course-body">
          <div style="display:flex;gap:6px;margin-bottom:8px">
            <span class="badge badge-blue">
              {{ course.category }}
            </span>

            <span class="badge badge-gray">
              {{ course.level }}
            </span>
          </div>

          <div class="course-title">
            {{ course.title }}
          </div>

          <div class="course-meta">
            <span>👤 {{ course.teacher_name || 'Teacher' }}</span>
            <span>📖 {{ course.lessons_count || 0 }} lessons</span>
            <span>⏱ {{ course.duration_hours || 0 }}h</span>
          </div>

          <div class="course-footer">
            <span style="font-weight:600;font-size:15px">
              {{ course.is_free ? 'Free' : `$${course.price}` }}
            </span>

            <span
              v-if="role !== 'student'"
              class="badge"
              :class="course.is_published ? 'badge-green' : 'badge-warn'"
            >
              {{ course.is_published ? 'published' : 'draft' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <CourseTable
      v-else
      :courses="filteredCourses"
      @navigate="$emit('navigate', $event)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import CourseTable from '../components/CourseTable.vue'

const props = defineProps({
  role: String
})

defineEmits(['navigate', 'toast'])

const router = useRouter()

const viewMode = ref('grid')
const courses = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const selectedCategory = ref('')

const filteredCourses = computed(() => {
  return courses.value.filter((course) => {
    const matchesSearch =
      course.title?.toLowerCase().includes(search.value.toLowerCase()) ||
      course.description?.toLowerCase().includes(search.value.toLowerCase())

    const matchesCategory =
      !selectedCategory.value ||
      course.category === selectedCategory.value

    return matchesSearch && matchesCategory
  })
})

async function fetchCourses() {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('access_token')

    const response = await axios.get(
      'http://127.0.0.1:8000/api/courses/',
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    courses.value = response.data
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load courses.'
  } finally {
    loading.value = false
  }
}

function goToCreateCourse() {
  router.push('/create-course')
}

function goToCourse(id) {
  router.push(`/courses/${id}`)
}

onMounted(() => {
  fetchCourses()
})
</script>