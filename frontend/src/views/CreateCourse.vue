<template>
  <div class="create-course">
    <CourseStepper
      :step="step"
      :total-steps="totalSteps"
      :step-labels="stepLabels"
    />

    <CourseBasics
      v-if="step === 1"
      :form="form"
      :errors="errors"
      :categories="categories"
      :levels="levels"
      :languages="languages"
      :thumbnail-options="thumbnailOptions"
      :available-tags="availableTags"
      @toggle-tag="toggleTag"
    />

    <CourseContent
      v-if="step === 2"
      :form="form"
      :lesson-types="lessonTypes"
      @add-lesson="addLesson"
      @edit-lesson="editLesson"
      @remove-lesson="removeLesson"
      @add-objective="addObjective"
      @remove-objective="removeObjective"
    />

    <CourseSettings
      v-if="step === 3"
      :form="form"
      :toggle-settings="toggleSettings"
    />

    <CourseReview
      v-if="step === 4"
      :form="form"
      :checklist="checklist"
      :selected-thumbnail-bg="selectedThumbnailBg"
    />

    <div v-if="step === 5" class="success-banner">
      <div class="success-icon">✓</div>
      <p class="success-title">Course created!</p>
      <p class="success-sub">Your course is live and ready for enrollment.</p>

      <div class="success-actions">
        <button class="btn btn-primary" @click="$emit('view-course', form)">
          View course
        </button>

        <button class="btn btn-ghost" @click="resetForm">
          Create another
        </button>
      </div>
    </div>

    <div v-if="step <= totalSteps" class="footer">
      <button v-if="step > 1" class="btn btn-ghost" @click="step--">
        Back
      </button>

      <span v-else />

      <button class="btn btn-ghost btn-sm save-draft" @click="saveDraft">
        Save draft
      </button>

      <button
        class="btn"
        :class="step === totalSteps ? 'btn-success' : 'btn-primary'"
        @click="handleNext"
      >
        {{ step === totalSteps ? 'Publish course' : 'Continue' }}
      </button>
    </div>

    <Transition name="toast">
      <div v-if="toast.visible" class="toast">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import axios from 'axios'

import CourseStepper from '@/components/course/CourseStepper.vue'
import CourseBasics from '@/components/course/CourseBasics.vue'
import CourseContent from '@/components/course/CourseContent.vue'
import CourseSettings from '@/components/course/CourseSettings.vue'
import CourseReview from '@/components/course/CourseReview.vue'

import '@/assets/create-course.css'

const emit = defineEmits([
  'view-course',
  'save-draft'
])

const step = ref(1)
const totalSteps = 4

const stepLabels = [
  'Basics',
  'Content',
  'Settings',
  'Review'
]

const form = reactive({
  title: '',
  description: '',
  category: '',
  level: 'Beginner',
  language: 'English',
  duration: null,
  certificate: 'yes',
  thumbnail: '',
  tags: [],
  lessons: [],
  objectives: [],
  pricing: 'free',
  price: null,
  discountPrice: null,

  settings: {
    publishImmediately: true,
    allowPreviews: true,
    discussionForum: false,
    completionCertificate: true,
    enrollmentCap: false,
  },

  startDate: new Date().toISOString().split('T')[0],
  enrollDeadline: '',
})

const errors = reactive({
  title: '',
  description: '',
  category: '',
})

const toast = reactive({
  visible: false,
  message: '',
})

const categories = [
  'Development',
  'Design',
  'Data Science',
  'AI / Machine Learning',
  'Marketing',
  'DevOps',
  'Business',
]

const levels = [
  'Beginner',
  'Intermediate',
  'Advanced',
  'All levels'
]

const languages = [
  'English',
  'French',
  'Arabic',
  'Spanish',
  'German',
  'Portuguese'
]

const thumbnailOptions = [
  { icon: '💻', bg: '#EEF1FF' },
  { icon: '📊', bg: '#E0F2F1' },
  { icon: '🎨', bg: '#FCE7F3' },
  { icon: '🤖', bg: '#EDE9FE' },
  { icon: '📱', bg: '#FFF3E0' },
  { icon: '☁️', bg: '#E0F2F1' },
  { icon: '🔬', bg: '#FFEBEE' },
  { icon: '📐', bg: '#F1EFE8' },
]

const availableTags = [
  'JavaScript',
  'React',
  'Node.js',
  'Python',
  'CSS',
  'APIs',
  'SQL',
  'Git',
  'TypeScript',
  'Docker',
]

const lessonTypes = [
  { value: 'video', label: 'Video' },
  { value: 'quiz', label: 'Quiz' },
  { value: 'assignment', label: 'Assignment' },
  { value: 'reading', label: 'Reading' },
]

const toggleSettings = [
  {
    key: 'publishImmediately',
    label: 'Publish immediately',
    hint: 'Course goes live right after saving',
  },
  {
    key: 'allowPreviews',
    label: 'Allow previews',
    hint: 'Guests can preview the first 2 lessons',
  },
  {
    key: 'discussionForum',
    label: 'Discussion forum',
    hint: 'Enable Q&A and comments per lesson',
  },
  {
    key: 'completionCertificate',
    label: 'Completion certificate',
    hint: 'Auto-generate PDF certificate on 100% completion',
  },
  {
    key: 'enrollmentCap',
    label: 'Enrollment cap',
    hint: 'Limit the maximum number of students',
  },
]

const selectedThumbnailBg = computed(() => {
  return thumbnailOptions.find(
    (o) => o.icon === form.thumbnail
  )?.bg || '#EEF1FF'
})

const checklist = computed(() => [
  {
    label: 'Course title set',
    ok: !!form.title.trim(),
    val: form.title.substring(0, 32),
  },
  {
    label: 'Category selected',
    ok: !!form.category,
    val: form.category || '—',
  },
  {
    label: 'Description written',
    ok: !!form.description.trim(),
    val: '',
  },
  {
    label: 'Lessons added',
    ok: form.lessons.length >= 1,
    val: `${form.lessons.length} lessons`,
  },
  {
    label: 'Learning objectives',
    ok: form.objectives.filter((o) => o.trim()).length >= 1,
    val: '',
  },
  {
    label: 'Thumbnail chosen',
    ok: !!form.thumbnail,
    val: 'Icon selected',
  },
])

let lessonIdSeq = 0

function addLesson(type) {
  const defaults = {
    video: {
      title: 'New video lesson',
      meta: 'Video',
      content: '',
      video_url: '',
      video_file: null,
    },

    reading: {
      title: 'New reading material',
      meta: 'Reading',
      content: '',
      video_url: '',
      video_file: null,
    },

    quiz: {
      title: 'New quiz',
      meta: 'Quiz',
      content: '',
      video_url: '',
      video_file: null,
      quiz: {
        title: 'New quiz',
        description: '',
        passing_score: 50,
        time_limit_minutes: null,
        questions: [],
      },
    },

    assignment: {
      title: 'New assignment',
      meta: 'Assignment',
      content: '',
      video_url: '',
      video_file: null,
      assignment: {
        title: 'New assignment',
        instructions: '',
        due_date: '',
        max_score: 100,
      },
    },
  }

  form.lessons.push({
    id: ++lessonIdSeq,
    type,
    isEditing: true,
    ...defaults[type],
  })
}

function removeLesson(index) {
  form.lessons.splice(index, 1)
}

function editLesson(index) {
  form.lessons[index].isEditing = !form.lessons[index].isEditing
}

function addObjective() {
  form.objectives.push('')
}

function removeObjective(index) {
  form.objectives.splice(index, 1)
}

function toggleTag(tag) {
  const index = form.tags.indexOf(tag)

  if (index === -1) {
    form.tags.push(tag)
  } else {
    form.tags.splice(index, 1)
  }
}

function validate() {
  errors.title = form.title.trim() ? '' : 'Title is required'
  errors.description = form.description.trim() ? '' : 'Description is required'
  errors.category = form.category ? '' : 'Please select a category'

  return !errors.title && !errors.description && !errors.category
}

function validateContentStep() {
  if (form.lessons.length === 0) {
    showToast('Please add at least one lesson')
    return false
  }

  const emptyTitle = form.lessons.some((lesson) => !lesson.title.trim())

  if (emptyTitle) {
    showToast('Each lesson needs a title')
    return false
  }

  return true
}

async function createCourse() {
  const payload = {
    title: form.title,
    description: form.description,
    category: form.category,

    level: form.level.toLowerCase(),
    language: form.language,
    duration_hours: form.duration || 0,
    has_certificate: form.settings.completionCertificate,
    tags: form.tags,

    lessons: form.lessons.map((lesson, index) => ({
      title: lesson.title,
      content: lesson.content || '',
      video_url: lesson.video_url || '',
      video_file: lesson.video_file || null,

      lesson_type: lesson.type,
      order_number: index + 1,

      quiz: lesson.type === 'quiz'
        ? {
            title: lesson.title,
            description: lesson.content || '',
            passing_score: lesson.quiz.passing_score,
            time_limit_minutes: lesson.quiz.time_limit_minutes,
            questions: lesson.quiz.questions,
          }
        : null,

      assignment: lesson.type === 'assignment'
        ? {
            title: lesson.title,
            instructions: lesson.assignment.instructions,
            due_date: lesson.assignment.due_date || null,
            max_score: lesson.assignment.max_score,
          }
        : null,
    })),

    is_free: form.pricing === 'free',
    price: form.pricing === 'free' ? 0 : form.price,
    is_published: form.settings.publishImmediately,
  }

  const token = localStorage.getItem('access_token')
  console.log('ACCESS TOKEN:', token)

if (!token) {
  alert('No token found. Please login again.')
  throw new Error('No access token found')
}

  const response = await axios.post(
    'http://127.0.0.1:8000/api/courses/',
    payload,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  return response.data
}

async function handleNext() {
  if (step.value === 1 && !validate()) return
  if (step.value === 2 && !validateContentStep()) return

  if (step.value < totalSteps) {
    step.value++
  } else {
    try {
      const course = await createCourse()

      showToast('Course created successfully')
      step.value = 5

      emit('save-draft', {
        ...form,
        id: course.id,
      })
    } catch (error) {
      console.error(error)
      showToast('Failed to create course')
    }
  }
}

function saveDraft() {
  emit('save-draft', {
    ...form
  })

  showToast('Draft saved')
}

function resetForm() {
  Object.assign(form, {
    title: '',
    description: '',
    category: '',
    level: 'Beginner',
    language: 'English',
    duration: null,
    certificate: 'yes',
    thumbnail: '',
    tags: [],
    lessons: [],
    objectives: [],
    pricing: 'free',
    price: null,
    discountPrice: null,

    settings: {
      publishImmediately: true,
      allowPreviews: true,
      discussionForum: false,
      completionCertificate: true,
      enrollmentCap: false,
    },

    startDate: new Date().toISOString().split('T')[0],
    enrollDeadline: '',
  })

  lessonIdSeq = 0
  step.value = 1
}

function showToast(message) {
  toast.message = message
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 2500)
}
</script>