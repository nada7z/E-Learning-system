<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ isStudent ? 'My Assignments' : 'Assignments' }}</h1>
        <p class="page-sub">
          {{ isStudent ? 'View your assignment submissions, grades, and feedback' : `${filteredAssignments.length}
          assignments
          across ${courses.length} courses` }}
        </p>
      </div>

      <button v-if="!isStudent" class="btn btn-primary" @click="openCreate">
        + New Assignment
      </button>
    </div>

    <div class="filters-bar">
      <div class="search-wrap">
        <span class="search-icon">
          <Search :size="16" />
        </span>
        <input v-model="search" class="input search-input" placeholder="Search assignments…" />
      </div>

      <select v-model="filterCourse" class="input filter-select">
        <option value="">All courses</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
      </select>

      <select v-model="filterStatus" class="input filter-select">
        <option value="">All statuses</option>
        <option value="open">Open</option>
        <option value="due_soon">Due soon</option>
        <option value="past_due">Past due</option>
      </select>

      <div v-if="!isStudent" class="tab-bar">
        <button class="tab" :class="{ active: view === 'list' }" @click="view = 'list'">List</button>
        <button class="tab" :class="{ active: view === 'grade' }" @click="view = 'grade'">Grade</button>
      </div>
    </div>

    <template v-if="view === 'list'">
      <div v-if="!filteredAssignments.length" class="empty-state">
        <div class="empty-icon">📋</div>
        <p class="empty-title">No assignments found</p>
        <p class="empty-sub">Try adjusting your filters.</p>
        <button v-if="!isStudent" class="btn btn-primary" @click="openCreate">+ New Assignment</button>
      </div>

      <div v-else class="assignment-list">
        <div v-for="a in filteredAssignments" :key="a.id" class="assignment-card">
          <div class="card-accent" :class="deadlineClass(a.deadline)" />

          <div class="card-body">
            <div class="card-top">
              <div class="card-info">
                <span class="course-badge">{{ a.course_title }}</span>
                <h3 class="assign-title">{{ a.title }}</h3>
                <p class="assign-desc">{{ a.description }}</p>
              </div>

              <div class="card-meta">
                <div class="meta-item">
                  <span class="meta-label">Deadline</span>
                  <span class="meta-val" :class="deadlineClass(a.deadline)">
                    {{ formatDate(a.deadline) }}
                  </span>
                </div>

                <div class="meta-item">
                  <span class="meta-label">Max score</span>
                  <span class="meta-val">{{ a.max_score }} pts</span>
                </div>

                <div v-if="!isStudent" class="meta-item">
                  <span class="meta-label">Submissions</span>
                  <span class="meta-val">{{ a.submissions_count }} / {{ a.enrolled_count }}</span>
                </div>

                <span class="status-badge" :class="deadlineClass(a.deadline)">
                  {{ deadlineLabel(a.deadline) }}
                </span>
              </div>
            </div>

            <div v-if="!isStudent" class="submission-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{
                  width: submissionRate(a) + '%',
                  background: deadlineFill(a.deadline)
                }" />
              </div>
              <span class="progress-pct">{{ submissionRate(a) }}% submitted</span>
            </div>
          </div>

          <div class="card-actions">
            <template v-if="isStudent">
              <div class="student-result-box">
                <template v-if="getSubmission(a.id)">
                  <span class="status-badge status-green">✓ Submitted</span>

                  <p class="result-line">
                    <strong>Grade:</strong>
                    {{ getSubmission(a.id).grade ?? 'Not graded yet' }}
                    <span v-if="getSubmission(a.id).grade != null">/ {{ a.max_score }}</span>
                  </p>

                  <p class="result-line">
                    <strong>Feedback:</strong>
                    {{ getSubmission(a.id).feedback || 'No feedback yet' }}
                  </p>
                </template>

                <template v-else>
                  <span class="status-badge status-warn">Not submitted yet</span>
                  <p class="result-line text-muted">
                    Submit this assignment from the course detail page.
                  </p>
                </template>
              </div>
            </template>

            <template v-else>
              <button class="btn btn-ghost btn-sm" @click="openEdit(a)">Edit</button>
              <button class="btn btn-primary btn-sm" @click="openGrade(a)">Grade →</button>
              <button class="icon-btn danger" @click="confirmDelete(a)" title="Delete assignment">🗑</button>
            </template>
          </div>
        </div>
      </div>
    </template>

    <template v-if="!isStudent && view === 'grade'">
      <div class="grade-selector">
        <span class="grade-selector-label">Assignment:</span>
        <select v-model="gradeTarget" class="input filter-select" style="flex:1; max-width:360px">
          <option value="">Select an assignment to grade</option>
          <option v-for="a in assignments" :key="a.id" :value="a.id">{{ a.title }}</option>
        </select>
      </div>

      <div v-if="!gradeTarget" class="empty-state">
        <div class="empty-icon">✏️</div>
        <p class="empty-title">Select an assignment</p>
        <p class="empty-sub">Choose an assignment above to see and grade student submissions.</p>
      </div>

      <template v-else>
        <div class="grade-stats">
          <div class="stat-pill"><span>📬</span> {{ currentAssignment?.submissions_count }} submitted</div>
          <div class="stat-pill"><span>⏳</span> {{ currentAssignment?.enrolled_count - currentAssignment?.graded_count
          }} pending grade</div>
          <div class="stat-pill"><span>✅</span> {{ currentAssignment?.graded_count }} graded</div>
          <div class="stat-pill"><span>📊</span> Avg {{ currentAssignment?.avg_grade ?? '—' }} pts</div>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Submitted</th>
                <th>File</th>
                <th>Grade</th>
                <th>Feedback</th>
                <th>Status</th>
                <th>Save</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="sub in currentSubmissions" :key="sub.id">
                <td>
                  <div class="student-cell">
                    <div class="avatar-sm" :style="{ background: sub.avatar_color + '22', color: sub.avatar_color }">
                      {{ initials(sub.student_name) }}
                    </div>
                    {{ sub.student_name }}
                  </div>
                </td>

                <td class="text-muted text-sm">{{ formatDate(sub.submitted_at) }}</td>

                <td>
                  <a class="file-link" :href="sub.file_url" target="_blank">
                    📎 {{ sub.file_name }}
                  </a>
                </td>

                <td>
                  <input v-model.number="sub.grade" class="input grade-input" type="number" :min="0"
                    :max="currentAssignment.max_score" :placeholder="'/ ' + currentAssignment.max_score" />
                </td>

                <td>
                  <input v-model="sub.feedback" class="input" style="min-width:180px"
                    placeholder="Optional feedback…" />
                </td>

                <td>
                  <span class="status-badge" :class="sub.grade != null ? 'status-green' : 'status-warn'">
                    {{ sub.grade != null ? 'Graded' : 'Pending' }}
                  </span>
                </td>

                <td>
                  <button class="btn btn-primary btn-sm" :disabled="sub.grade == null" @click="saveGrade(sub)">
                    Save
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>

    <Transition name="modal">
      <div v-if="modal.open" class="modal-backdrop" @click.self="modal.open = false">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">{{ modal.editing ? 'Edit Assignment' : 'New Assignment' }}</h2>
            <button class="icon-btn" @click="modal.open = false">✕</button>
          </div>

          <div class="modal-body">
            <div class="field">
              <label class="label">Course <span class="req">*</span></label>
              <select v-model="modal.form.course" class="input" :class="{ error: modal.errors.course }">
                <option value="">Select course</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
              </select>
              <span v-if="modal.errors.course" class="err-msg">⚠ {{ modal.errors.course }}</span>
            </div>

            <div class="field">
              <label class="label">Title <span class="req">*</span></label>
              <input v-model="modal.form.title" class="input" :class="{ error: modal.errors.title }" />
              <span v-if="modal.errors.title" class="err-msg">⚠ {{ modal.errors.title }}</span>
            </div>

            <div class="field">
              <label class="label">Description / Instructions <span class="req">*</span></label>
              <textarea v-model="modal.form.description" class="input" rows="5"
                :class="{ error: modal.errors.description }" />
              <span v-if="modal.errors.description" class="err-msg">⚠ {{ modal.errors.description }}</span>
            </div>

            <div class="grid-2">
              <div class="field">
                <label class="label">Deadline <span class="req">*</span></label>
                <input v-model="modal.form.deadline" class="input" type="datetime-local"
                  :class="{ error: modal.errors.deadline }" />
                <span v-if="modal.errors.deadline" class="err-msg">⚠ {{ modal.errors.deadline }}</span>
              </div>

              <div class="field">
                <label class="label">Max score</label>
                <input v-model.number="modal.form.max_score" class="input" type="number" min="1" />
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-ghost" @click="modal.open = false">Cancel</button>
            <button class="btn btn-primary" @click="saveAssignment">
              {{ modal.editing ? 'Update Assignment' : 'Create Assignment' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="modal">
      <div v-if="deleteConfirm.open" class="modal-backdrop" @click.self="deleteConfirm.open = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2 class="modal-title">Delete assignment?</h2>
            <button class="icon-btn" @click="deleteConfirm.open = false">✕</button>
          </div>

          <div class="modal-body">
            <p class="text-muted">
              "<strong>{{ deleteConfirm.target?.title }}</strong>" and all submissions will be deleted.
            </p>
          </div>

          <div class="modal-footer">
            <button class="btn btn-ghost" @click="deleteConfirm.open = false">Cancel</button>
            <button class="btn btn-danger" @click="deleteAssignment">Delete permanently</button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="toast">
      <div v-if="toast.visible" class="toast">{{ toast.message }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { Search } from 'lucide-vue-next'

const courses = ref([])
const assignments = ref([])
const submissions = ref([])

const loading = ref(false)
const search = ref('')
const filterCourse = ref('')
const filterStatus = ref('')
const view = ref('list')
const gradeTarget = ref('')

const user = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    return {}
  }
})

const isStudent = computed(() => {
  return user.value?.role?.toLowerCase() === 'student'
})

const modal = reactive({
  open: false,
  editing: false,
  _id: null,
  form: blankForm(),
  errors: {},
})

const deleteConfirm = reactive({
  open: false,
  target: null,
})

const toast = reactive({
  visible: false,
  message: '',
})

const filteredAssignments = computed(() => {
  return assignments.value.filter((a) => {
    const term = search.value.toLowerCase()

    const matchSearch =
      !term ||
      a.title?.toLowerCase().includes(term) ||
      a.course_title?.toLowerCase().includes(term)

    const matchCourse =
      !filterCourse.value ||
      Number(a.course) === Number(filterCourse.value)

    const matchStatus =
      !filterStatus.value ||
      deadlineKey(a.deadline) === filterStatus.value

    return matchSearch && matchCourse && matchStatus
  })
})

const currentAssignment = computed(() => {
  return assignments.value.find(
    (a) => Number(a.id) === Number(gradeTarget.value)
  ) || null
})

const currentSubmissions = computed(() => {
  return submissions.value.filter((s) => {
    return (
      Number(s.assignment_id) === Number(gradeTarget.value) ||
      Number(s.assignment) === Number(gradeTarget.value)
    )
  })
})

function hasSubmitted(assignmentId) {
  return submissions.value.some((s) => {
    return (
      Number(s.assignment_id) === Number(assignmentId) ||
      Number(s.assignment) === Number(assignmentId)
    )
  })
}

function getSubmission(assignmentId) {
  return submissions.value.find((s) => {
    return (
      Number(s.assignment_id) === Number(assignmentId) ||
      Number(s.assignment) === Number(assignmentId)
    )
  }) || null
}

function authHeaders() {
  const token = localStorage.getItem('access_token')

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

async function fetchData() {
  loading.value = true

  try {
    const [coursesRes, assignmentsRes, submissionsRes] = await Promise.all([
      axios.get('http://127.0.0.1:8000/api/courses/', authHeaders()),
      axios.get('http://127.0.0.1:8000/api/assignments/', authHeaders()),
      axios.get('http://127.0.0.1:8000/api/submissions/', authHeaders()),
    ])

    courses.value = coursesRes.data || []
    assignments.value = assignmentsRes.data || []
    submissions.value = submissionsRes.data || []

    console.log('SUBMISSIONS:', submissions.value)
  } catch (error) {
    console.error(error)
    showToast('Failed to load assignments')
  } finally {
    loading.value = false
  }
}

function blankForm() {
  return {
    course: '',
    title: '',
    description: '',
    deadline: '',
    max_score: 100,
  }
}

function openCreate() {
  modal.form = blankForm()
  modal.errors = {}
  modal.editing = false
  modal._id = null
  modal.open = true
}

function openEdit(a) {
  modal.form = {
    course: a.course,
    title: a.title,
    description: a.description,
    deadline: a.deadline?.slice(0, 16),
    max_score: a.max_score,
  }

  modal.errors = {}
  modal.editing = true
  modal._id = a.id
  modal.open = true
}

function openGrade(a) {
  gradeTarget.value = a.id
  view.value = 'grade'
}

function validateModal() {
  const e = {}

  if (!modal.form.course) e.course = 'Please select a course'
  if (!modal.form.title.trim()) e.title = 'Title is required'
  if (!modal.form.description.trim()) e.description = 'Instructions are required'
  if (!modal.form.deadline) e.deadline = 'Deadline is required'

  modal.errors = e

  return !Object.keys(e).length
}

async function saveAssignment() {
  if (!validateModal()) return

  const payload = {
    course: modal.form.course,
    title: modal.form.title,
    description: modal.form.description,
    deadline: modal.form.deadline,
    max_score: modal.form.max_score || 100,
  }

  try {
    if (modal.editing) {
      await axios.patch(
        `http://127.0.0.1:8000/api/assignments/${modal._id}/`,
        payload,
        authHeaders()
      )

      showToast('Assignment updated ✅')
    } else {
      await axios.post(
        'http://127.0.0.1:8000/api/assignments/',
        payload,
        authHeaders()
      )

      showToast('Assignment created ✅')
    }

    modal.open = false
    await fetchData()
  } catch (error) {
    console.error(error)
    showToast('Failed to save assignment')
  }
}

function confirmDelete(a) {
  deleteConfirm.target = a
  deleteConfirm.open = true
}

async function deleteAssignment() {
  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/assignments/${deleteConfirm.target.id}/`,
      authHeaders()
    )

    deleteConfirm.open = false
    await fetchData()
    showToast('Assignment deleted')
  } catch (error) {
    console.error(error)
    showToast('Failed to delete assignment')
  }
}

async function saveGrade(sub) {
  try {
    await axios.patch(
      `http://127.0.0.1:8000/api/submissions/${sub.id}/`,
      {
        grade: sub.grade,
        feedback: sub.feedback,
      },
      authHeaders()
    )

    await fetchData()
    showToast(`Saved grade for ${sub.student_name}`)
  } catch (error) {
    console.error(error)
    showToast('Failed to save grade')
  }
}

function submissionRate(a) {
  if (!a.enrolled_count) return 0
  return Math.round((a.submissions_count / a.enrolled_count) * 100)
}

function deadlineKey(deadline) {
  const diff = (new Date(deadline) - Date.now()) / 3600000

  if (diff < 0) return 'past_due'
  if (diff < 48) return 'due_soon'

  return 'open'
}

function deadlineClass(deadline) {
  return {
    past_due: 'status-red',
    due_soon: 'status-warn',
    open: 'status-green',
  }[deadlineKey(deadline)]
}

function deadlineFill(deadline) {
  return {
    past_due: '#C62828',
    due_soon: '#F57C00',
    open: '#3D5AFE',
  }[deadlineKey(deadline)]
}

function deadlineLabel(deadline) {
  return {
    past_due: 'Past due',
    due_soon: 'Due soon',
    open: 'Open',
  }[deadlineKey(deadline)]
}

function formatDate(dt) {
  if (!dt) return '—'

  return new Date(dt).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function initials(name) {
  if (!name) return '?'

  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function showToast(msg) {
  toast.message = msg
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 2600)
}

onMounted(() => {
  fetchData()
})
</script>

<style src="/src/assets/AssignmentsView.css" scoped></style>