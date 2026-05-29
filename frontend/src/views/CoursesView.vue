<template>
  <div class="page">
    <div class="page-header flex items-center justify-between">
      <div>
        <h1 class="page-title">
          {{ role === 'admin' ? 'All Courses' : 'My Courses' }}
        </h1>

        <p class="page-sub">
          {{ courses.length }} courses total
        </p>
      </div>

      <button v-if="canManageCourses" class="btn btn-primary" @click="goToCreateCourse">
        + New Course
      </button>
    </div>

    <div style="
        display:flex;
        gap:12px;
        margin-bottom:24px;
        flex-wrap:wrap;
        align-items:center;
      ">
      <div style="position:relative;flex:1;min-width:200px">
        <span style="
            position:absolute;
            left:12px;
            top:50%;
            transform:translateY(-50%);
            color:var(--text3);
          ">
          <Search :size="16" />
        </span>

        <input v-model="search" style="
            width:100%;
            background:var(--surface);
            border:1px solid var(--border);
            border-radius:10px;
            padding:10px 14px 10px 36px;
            font-size:14px;
            color:var(--text);
          " placeholder="Search courses…" />
      </div>

      <select v-model="selectedCategory" style="
          background:var(--surface);
          border:1px solid var(--border);
          border-radius:10px;
          padding:10px 14px;
          font-size:14px;
          color:var(--text);
        ">
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
        <div class="tab" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
          Grid
        </div>

        <div class="tab" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
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
      <div v-for="course in filteredCourses" :key="course.id" class="course-card" @click="goToCourse(course.id)">
        <div class="course-thumb" :style="{ background: course.thumbnail ? 'transparent' : '#EEF1FF' }">
          <img v-if="course.thumbnail && !brokenImages[course.id]" :src="course.thumbnail" class="course-thumb-img"
            @error="brokenImages[course.id] = true" />

          <span v-else>📚</span>
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
            <span>
              <User :size="14" /> {{ course.teacher_name || 'Teacher' }}
            </span>
            <span>
              <BookOpen :size="14" /> {{ course.lessons_count || 0 }} lessons
            </span>
            <span>
              <Clock3 :size="14" /> {{ course.duration_hours || 0 }}h
            </span>
          </div>

          <div class="course-footer">
            <span style="font-weight:600;font-size:15px">
              {{ course.is_free ? 'Free' : `$${course.price}` }}
            </span>

            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
              <span v-if="canManageCourses" class="badge" :class="course.is_published ? 'badge-green' : 'badge-warn'">
                {{ course.is_published ? 'published' : 'draft' }}
              </span>

              <button v-if="canManageCourses" class="btn btn-sm" @click.stop="editCourse(course.id)">
                Edit
              </button>

              <button v-if="canManageCourses" class="btn btn-sm btn-danger" @click.stop="deleteCourse(course.id)">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <CourseTable v-else :courses="filteredCourses" :can-manage="canManageCourses" @navigate="goToCourse"
      @edit="editCourse" @delete="deleteCourse" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import CourseTable from '../components/CourseTable.vue'
import {
  BookOpen,
  Clock3,
  Search,
  User,
  Pencil,
  Trash2,
  Plus,
} from 'lucide-vue-next'

const brokenImages = ref({})
const router = useRouter()

const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
const role = ref(storedUser.role || '')

const canManageCourses = computed(() => role.value === 'teacher')

const viewMode = ref('grid')
const courses = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const selectedCategory = ref('')

const filteredCourses = computed(() => {
  return courses.value.filter((course) => {
    const term = search.value.toLowerCase()

    const matchesSearch =
      course.title?.toLowerCase().includes(term) ||
      course.description?.toLowerCase().includes(term) ||
      course.teacher_name?.toLowerCase().includes(term)

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

    const url =
      role.value === 'student'
        ? 'http://127.0.0.1:8000/api/continue-learning/'
        : 'http://127.0.0.1:8000/api/courses/'

    const response = await axios.get(url, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

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

function editCourse(id) {
  if (!canManageCourses.value) return
  router.push(`/courses/${id}/edit`)
}

async function deleteCourse(id) {
  if (!canManageCourses.value) return
  if (!confirm('Delete this course?')) return

  try {
    const token = localStorage.getItem('access_token')

    await axios.delete(
      `http://127.0.0.1:8000/api/courses/${id}/`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    courses.value = courses.value.filter(
      (course) => course.id !== id
    )
  } catch (err) {
    console.error(err)
    alert('Failed to delete course.')
  }
}

function getThumbnailUrl(thumbnail) {
  if (!thumbnail) return null
  if (thumbnail.startsWith('http')) return thumbnail
  return `http://127.0.0.1:8000${thumbnail}`
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.course-thumb {
  width: 100%;
  height: 185px;
  overflow: hidden;
  background: #eef1ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.course-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>