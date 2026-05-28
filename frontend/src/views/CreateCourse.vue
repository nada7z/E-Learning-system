<template>
  <div class="create-course">
    <CourseStepper :step="step" :total-steps="totalSteps" :step-labels="stepLabels" />

    <CourseBasics v-if="step === 1" :form="form" :errors="errors" :categories="categories" :levels="levels"
      :languages="languages" :thumbnail-options="thumbnailOptions" :available-tags="availableTags"
      :thumbnail-preview="thumbnailPreview" @toggle-tag="toggleTag" @thumbnail-upload="handleThumbnailUpload"
      @remove-thumbnail="removeThumbnail" />

    <CourseContent v-if="step === 2" :form="form" :lesson-types="lessonTypes" @add-lesson="addLesson"
      @edit-lesson="editLesson" @remove-lesson="removeLesson" @add-objective="addObjective"
      @remove-objective="removeObjective" />

    <CourseSettings v-if="step === 3" :form="form" :toggle-settings="toggleSettings" />

    <CourseReview v-if="step === 4" :form="form" :checklist="checklist" :selected-thumbnail-bg="selectedThumbnailBg" />

    <div v-if="step === 5" class="success-banner">
      <div class="success-icon">✓</div>
      <p class="success-title">
        {{ isEditMode ? 'Course updated!' : 'Course created!' }}
      </p>
      <p class="success-sub">
        {{
          isEditMode
            ? 'Your changes were saved successfully.'
            : 'Your course is live and ready for enrollment.'
        }}
      </p>

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

      <button class="btn" :class="step === totalSteps ? 'btn-success' : 'btn-primary'" @click="handleNext">
        {{ step === totalSteps ? finalButtonText : 'Continue' }}
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
import { computed, reactive, ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

import CourseStepper from '@/components/course/CourseStepper.vue'
import CourseBasics from '@/components/course/CourseBasics.vue'
import CourseContent from '@/components/course/CourseContent.vue'
import CourseSettings from '@/components/course/CourseSettings.vue'
import CourseReview from '@/components/course/CourseReview.vue'

import '@/assets/create-course.css'

const route = useRoute()

const isEditMode = computed(() => route.name === 'EditCourse')

const finalButtonText = computed(() => {
  return isEditMode.value
    ? 'Save changes'
    : 'Publish course'
})

const emit = defineEmits(['view-course', 'save-draft'])

const step = ref(1)
const totalSteps = 4

const thumbnailFile = ref(null)
const thumbnailPreview = ref('')

const stepLabels = ['Basics', 'Content', 'Settings', 'Review']

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

const levels = ['Beginner', 'Intermediate', 'Advanced', 'All levels']

const languages = ['English', 'French', 'Arabic', 'Spanish', 'German', 'Portuguese']

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
  return thumbnailOptions.find((o) => o.icon === form.thumbnail)?.bg || '#EEF1FF'
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
    label: 'Thumbnail selected',
    ok: !!form.thumbnail || !!thumbnailFile.value,
    val: thumbnailFile.value ? 'Image uploaded' : 'Icon selected',
  },
])

let lessonIdSeq = 0

function handleThumbnailUpload(file) {
  if (!file) return

  thumbnailFile.value = file
  thumbnailPreview.value = URL.createObjectURL(file)
  form.thumbnail = ''
}

function removeThumbnail() {
  thumbnailFile.value = null
  thumbnailPreview.value = ''

  if (form.thumbnail && form.thumbnail.startsWith('http')) {
    form.thumbnail = ''
  }
}

function addLesson(type) {
  lessonIdSeq++

  const lesson = {
    id: Date.now() + lessonIdSeq,
    type,
    title: '',
    content: '',
    meta: type.charAt(0).toUpperCase() + type.slice(1),
    isEditing: true,
  }

  if (type === 'quiz') {
    lesson.title = 'New Quiz'
    lesson.meta = 'Quiz'
    lesson.quiz = {
      passing_score: 50,
      time_limit_minutes: null,
      is_final_exam: false,
      questions: [],
    }
  }

  if (type === 'assignment') {
    lesson.title = 'New Assignment'
    lesson.meta = 'Assignment'
    lesson.assignment = {
      instructions: '',
      due_date: '',
      max_score: 100,
    }
  }

  if (type === 'reading') {
    lesson.title = 'New Reading'
    lesson.meta = 'Reading'
  }

  if (type === 'video') {
    lesson.title = 'New Video'
    lesson.meta = 'Video'
    lesson.video_url = ''
    lesson.video_file = null
  }

  form.lessons.push(lesson)
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

function buildLessonsPayload() {
  return form.lessons.map((lesson, index) => ({
    title: lesson.title,
    content: lesson.content || '',
    video_url: lesson.video_url || '',
    video_file: null,
    lesson_type: lesson.type,
    type: lesson.type,
    order_number: index + 1,

    quiz:
      lesson.type === 'quiz'
        ? {
          title: lesson.title,
          description: lesson.content || '',
          passing_score: lesson.quiz?.passing_score || 50,
          time_limit_minutes: lesson.quiz?.time_limit_minutes || null,
          is_final_exam: lesson.quiz?.is_final_exam || false,
          questions: lesson.quiz?.questions || [],
        }
        : null,

    assignment:
      lesson.type === 'assignment'
        ? {
          title: lesson.title,
          instructions: lesson.assignment?.instructions || lesson.content || '',
          due_date: lesson.assignment?.due_date || null,
          max_score: lesson.assignment?.max_score || 100,
        }
        : null,
  }))
}

async function saveCourse() {
  const token = localStorage.getItem('access_token')

  if (!token) {
    alert('No token found. Please login again.')
    throw new Error('No access token found')
  }

  const formData = new FormData()

  formData.append('title', form.title)
  formData.append('description', form.description)
  formData.append('category', form.category)
  formData.append('level', form.level.toLowerCase())
  formData.append('language', form.language)
  formData.append('duration_hours', form.duration || 0)
  formData.append('has_certificate', form.settings.completionCertificate)
  formData.append('tags', JSON.stringify(form.tags))
  formData.append('lessons', JSON.stringify(buildLessonsPayload()))
  formData.append('is_free', form.pricing === 'free')
  formData.append('price', form.pricing === 'free' ? 0 : form.price || 0)
  formData.append('is_published', form.settings.publishImmediately)

  if (thumbnailFile.value) {
    formData.append('thumbnail', thumbnailFile.value)
  }

  if (!thumbnailFile.value && !thumbnailPreview.value) {
    formData.append('remove_thumbnail', 'true')
  }

  const config = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }

  if (isEditMode.value) {
    const response = await axios.patch(
      `http://127.0.0.1:8000/api/courses/${route.params.id}/`,
      formData,
      config
    )

    return response.data
  }

  const response = await axios.post(
    'http://127.0.0.1:8000/api/courses/',
    formData,
    config
  )

  return response.data
}

async function handleNext() {
  if (step.value === 1 && !validate()) return
  if (step.value === 2 && !validateContentStep()) return

  if (step.value < totalSteps) {
    step.value++
    return
  }

  try {
    const course = await saveCourse()
    const token = localStorage.getItem('access_token')
    await saveExtraQuizAndAssignments(course.id, token)

    showToast(isEditMode.value ? 'Course updated successfully' : 'Course created successfully')
    step.value = 5

    emit('save-draft', {
      ...form,
      id: course.id,
    })
  } catch (error) {
    console.error(error)
    showToast('Failed to save course')
  }
}

function saveDraft() {
  emit('save-draft', {
    ...form,
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

  thumbnailFile.value = null
  thumbnailPreview.value = ''
  lessonIdSeq = 0
  step.value = 1
}

async function saveExtraQuizAndAssignments(courseId, token) {
  const headers = {
    Authorization: `Bearer ${token}`,
  }

  for (const lesson of form.lessons) {
    if (lesson.type === 'quiz') {
      const payload = {
        course: courseId,
        title: lesson.title,
        description: lesson.content || '',
        passing_score: lesson.quiz?.passing_score || 50,
        time_limit_minutes: lesson.quiz?.time_limit_minutes || null,
        is_published: true,
        questions: lesson.quiz?.questions || [],
      }

      if (String(lesson.id).startsWith('quiz-')) {
        const quizId = String(lesson.id).replace('quiz-', '')

        await axios.patch(
          `http://127.0.0.1:8000/api/quizzes/${quizId}/`,
          payload,
          { headers }
        )
      } else {
        await axios.post(
          'http://127.0.0.1:8000/api/quizzes/',
          payload,
          { headers }
        )
      }
    }

    if (lesson.type === 'assignment') {
      const payload = {
        course: courseId,
        title: lesson.title,
        description: lesson.content || '',
        deadline: lesson.assignment?.due_date || null,
        max_score: lesson.assignment?.max_score || 100,
      }

      if (String(lesson.id).startsWith('assignment-')) {
        const assignmentId = String(lesson.id).replace('assignment-', '')

        await axios.patch(
          `http://127.0.0.1:8000/api/assignments/${assignmentId}/`,
          payload,
          { headers }
        )
      } else {
        await axios.post(
          'http://127.0.0.1:8000/api/assignments/',
          payload,
          { headers }
        )
      }
    }
  }
}

function showToast(message) {
  toast.message = message
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 2500)
}

async function loadCourse() {
  if (!isEditMode.value) return

  try {
    const token = localStorage.getItem('access_token')

    const [courseRes, quizzesRes, assignmentsRes] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/courses/${route.params.id}/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }),

      axios.get('http://127.0.0.1:8000/api/quizzes/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }),

      axios.get('http://127.0.0.1:8000/api/assignments/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }),
    ])

    const course = courseRes.data

    form.title = course.title || ''
    form.description = course.description || ''
    form.category = course.category || ''
    form.level = course.level || 'Beginner'
    form.language = course.language || 'English'
    form.duration = course.duration_hours || null
    form.tags = course.tags || []
    form.thumbnail = course.thumbnail || ''

    if (course.thumbnail) {
      thumbnailPreview.value = course.thumbnail
    }

    form.pricing = course.is_free ? 'free' : 'paid'
    form.price = course.price || null
    form.settings.publishImmediately = course.is_published

    const normalLessons = (course.lessons || []).map((lesson, index) => ({
      id: lesson.id || index + 1,
      type: lesson.lesson_type,
      lesson_type: lesson.lesson_type,
      title: lesson.title || '',
      content: lesson.content || '',
      meta: lesson.lesson_type
        ? lesson.lesson_type.charAt(0).toUpperCase() + lesson.lesson_type.slice(1)
        : '',
      video_url: lesson.video_url || '',
      video_file: null,
      isEditing: false,
    }))

    const quizLessons = (quizzesRes.data || [])
      .filter((quiz) => Number(quiz.course) === Number(route.params.id))
      .map((quiz) => ({
        id: `quiz-${quiz.id}`,
        type: 'quiz',
        lesson_type: 'quiz',
        title: quiz.title || '',
        content: quiz.description || '',
        meta: 'Quiz',
        isEditing: false,
        quiz: {
          ...quiz,
          is_final_exam: Boolean(quiz.is_final_exam),
        },
      }))

    const assignmentLessons = (assignmentsRes.data || [])
      .filter((assignment) => Number(assignment.course) === Number(route.params.id))
      .map((assignment) => ({
        id: `assignment-${assignment.id}`,
        type: 'assignment',
        lesson_type: 'assignment',
        title: assignment.title || '',
        content: assignment.description || '',
        meta: 'Assignment',
        isEditing: false,
        assignment,
      }))

    form.lessons = [...normalLessons, ...quizLessons, ...assignmentLessons]
  } catch (error) {
    console.error(error)
    showToast('Failed to load course')
  }
}

onMounted(() => {
  loadCourse()
})
</script>