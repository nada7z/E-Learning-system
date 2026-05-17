<template>
  <div class="page">

    <!-- Page header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Assignments</h1>
        <p class="page-sub">
          {{ filteredAssignments.length }} assignment{{ filteredAssignments.length !== 1 ? 's' : '' }}
          across {{ courses.length }} course{{ courses.length !== 1 ? 's' : '' }}
        </p>
      </div>
      <button class="btn btn-primary" @click="openCreate">
        + New Assignment
      </button>
    </div>

    <!-- Filters bar -->
    <div class="filters-bar">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input
          v-model="search"
          class="input search-input"
          placeholder="Search assignments…"
        />
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

      <div class="tab-bar">
        <button class="tab" :class="{ active: view === 'list' }" @click="view = 'list'">List</button>
        <button class="tab" :class="{ active: view === 'grade' }" @click="view = 'grade'">Grade</button>
      </div>
    </div>

    <!-- ── LIST VIEW ── -->
    <template v-if="view === 'list'">
      <!-- Empty state -->
      <div v-if="!filteredAssignments.length" class="empty-state">
        <div class="empty-icon">📋</div>
        <p class="empty-title">No assignments found</p>
        <p class="empty-sub">Try adjusting your filters or create a new assignment.</p>
        <button class="btn btn-primary" @click="openCreate">+ New Assignment</button>
      </div>

      <div v-else class="assignment-list">
        <div
          v-for="a in filteredAssignments"
          :key="a.id"
          class="assignment-card"
        >
          <!-- Left accent -->
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
                <div class="meta-item">
                  <span class="meta-label">Submissions</span>
                  <span class="meta-val">{{ a.submissions_count }} / {{ a.enrolled_count }}</span>
                </div>
                <span class="status-badge" :class="deadlineClass(a.deadline)">
                  {{ deadlineLabel(a.deadline) }}
                </span>
              </div>
            </div>

            <!-- Submission progress -->
            <div class="submission-progress">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{
                    width: submissionRate(a) + '%',
                    background: deadlineFill(a.deadline)
                  }"
                />
              </div>
              <span class="progress-pct">{{ submissionRate(a) }}% submitted</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="card-actions">
            <button class="btn btn-ghost btn-sm" @click="openEdit(a)">Edit</button>
            <button class="btn btn-primary btn-sm" @click="openGrade(a)">Grade →</button>
            <button class="icon-btn danger" @click="confirmDelete(a)" title="Delete assignment">🗑</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── GRADE VIEW ── -->
    <template v-if="view === 'grade'">
      <!-- Assignment selector -->
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
          <div class="stat-pill"><span>📬</span> {{ currentAssignment.submissions_count }} submitted</div>
          <div class="stat-pill"><span>⏳</span> {{ currentAssignment.enrolled_count - currentAssignment.graded_count }} pending grade</div>
          <div class="stat-pill"><span>✅</span> {{ currentAssignment.graded_count }} graded</div>
          <div class="stat-pill"><span>📊</span> Avg {{ currentAssignment.avg_grade ?? '—' }} pts</div>
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
                  <div class="grade-input-wrap">
                    <input
                      v-model.number="sub.grade"
                      class="input grade-input"
                      type="number"
                      :min="0"
                      :max="currentAssignment.max_score"
                      :placeholder="'/ ' + currentAssignment.max_score"
                    />
                  </div>
                </td>
                <td>
                  <input
                    v-model="sub.feedback"
                    class="input"
                    style="min-width:180px"
                    placeholder="Optional feedback…"
                  />
                </td>
                <td>
                  <span class="status-badge" :class="sub.grade != null ? 'status-green' : 'status-warn'">
                    {{ sub.grade != null ? 'Graded' : 'Pending' }}
                  </span>
                </td>
                <td>
                  <button
                    class="btn btn-primary btn-sm"
                    :disabled="sub.grade == null"
                    @click="saveGrade(sub)"
                  >
                    Save
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>

    <!-- ── MODAL: Create / Edit ── -->
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
              <input
                v-model="modal.form.title"
                class="input"
                :class="{ error: modal.errors.title }"
                placeholder="e.g. Build a REST API with Django"
              />
              <span v-if="modal.errors.title" class="err-msg">⚠ {{ modal.errors.title }}</span>
            </div>

            <div class="field">
              <label class="label">Description / Instructions <span class="req">*</span></label>
              <textarea
                v-model="modal.form.description"
                class="input"
                rows="5"
                :class="{ error: modal.errors.description }"
                placeholder="Explain what the student must submit…"
              />
              <span v-if="modal.errors.description" class="err-msg">⚠ {{ modal.errors.description }}</span>
            </div>

            <div class="grid-2">
              <div class="field">
                <label class="label">Deadline <span class="req">*</span></label>
                <input
                  v-model="modal.form.deadline"
                  class="input"
                  type="datetime-local"
                  :class="{ error: modal.errors.deadline }"
                />
                <span v-if="modal.errors.deadline" class="err-msg">⚠ {{ modal.errors.deadline }}</span>
              </div>
              <div class="field">
                <label class="label">Max score (pts)</label>
                <input v-model.number="modal.form.max_score" class="input" type="number" min="1" placeholder="100" />
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

    <!-- ── DELETE CONFIRM ── -->
    <Transition name="modal">
      <div v-if="deleteConfirm.open" class="modal-backdrop" @click.self="deleteConfirm.open = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2 class="modal-title">Delete assignment?</h2>
            <button class="icon-btn" @click="deleteConfirm.open = false">✕</button>
          </div>
          <div class="modal-body">
            <p class="text-muted" style="font-size:14px">
              "<strong>{{ deleteConfirm.target?.title }}</strong>" and all its submissions will be permanently deleted.
              This cannot be undone.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="deleteConfirm.open = false">Cancel</button>
            <button class="btn btn-danger" @click="deleteAssignment">Delete permanently</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.visible" class="toast">{{ toast.message }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
// import api from '@/services/api'   // ← uncomment to wire Axios

// ── Mock data (replace with api.get('/assignments/') in onMounted) ──────────
const avatarColors = ['#3D5AFE', '#00897B', '#7C3AED', '#DB2777', '#F57C00']

const courses = ref([
  { id: 1, title: 'Full-Stack Web Development' },
  { id: 2, title: 'Data Science with Python'   },
  { id: 3, title: 'UI/UX Design Fundamentals'  },
])

const assignments = ref([
  {
    id: 1,
    course: 1, course_title: 'Full-Stack Web Development',
    title: 'Build a REST API with Django',
    description: 'Create a fully documented REST API using Django REST Framework. Include authentication, CRUD endpoints, and pagination.',
    deadline: '2024-08-10T23:59:00',
    max_score: 100,
    submissions_count: 18,
    enrolled_count: 24,
    graded_count: 12,
    avg_grade: 84,
  },
  {
    id: 2,
    course: 1, course_title: 'Full-Stack Web Development',
    title: 'Vue.js SPA — Todo App',
    description: 'Build a single-page todo application with Vue 3, Pinia for state management, and LocalStorage persistence.',
    deadline: '2024-07-28T23:59:00',
    max_score: 80,
    submissions_count: 22,
    enrolled_count: 24,
    graded_count: 22,
    avg_grade: 71,
  },
  {
    id: 3,
    course: 2, course_title: 'Data Science with Python',
    title: 'EDA on Titanic Dataset',
    description: 'Perform exploratory data analysis on the Titanic dataset. Produce at least 5 visualizations and a written summary.',
    deadline: '2024-08-20T23:59:00',
    max_score: 60,
    submissions_count: 5,
    enrolled_count: 31,
    graded_count: 0,
    avg_grade: null,
  },
])

const submissions = ref([
  { id: 1, assignment_id: 1, student_name: 'Alice Martin',  submitted_at: '2024-08-08T14:22:00', file_url: '#', file_name: 'api_project.zip',  grade: 92, feedback: 'Excellent work!',    avatar_color: '#3D5AFE' },
  { id: 2, assignment_id: 1, student_name: 'Bob Chen',      submitted_at: '2024-08-09T09:11:00', file_url: '#', file_name: 'django_api.zip',   grade: null, feedback: '',             avatar_color: '#00897B' },
  { id: 3, assignment_id: 1, student_name: 'Carol Davis',   submitted_at: '2024-08-07T20:05:00', file_url: '#', file_name: 'submission.zip',   grade: 78, feedback: 'Good effort.',    avatar_color: '#7C3AED' },
  { id: 4, assignment_id: 1, student_name: 'David Kim',     submitted_at: '2024-08-10T11:33:00', file_url: '#', file_name: 'rest_api.zip',     grade: null, feedback: '',             avatar_color: '#DB2777' },
  { id: 5, assignment_id: 2, student_name: 'Eva Lopez',     submitted_at: '2024-07-26T18:44:00', file_url: '#', file_name: 'todo_app.zip',     grade: 75, feedback: 'Nice UI.',        avatar_color: '#F57C00' },
])

// ── State ────────────────────────────────────────────────────────────────────
const search       = ref('')
const filterCourse = ref('')
const filterStatus = ref('')
const view         = ref('list')
const gradeTarget  = ref('')

const modal = reactive({
  open: false, editing: false,
  form: blankForm(),
  errors: {},
})

const deleteConfirm = reactive({ open: false, target: null })
const toast = reactive({ visible: false, message: '' })

// ── Computed ─────────────────────────────────────────────────────────────────
const filteredAssignments = computed(() => {
  return assignments.value.filter(a => {
    const matchSearch = !search.value ||
      a.title.toLowerCase().includes(search.value.toLowerCase()) ||
      a.course_title.toLowerCase().includes(search.value.toLowerCase())
    const matchCourse = !filterCourse.value || a.course === filterCourse.value
    const matchStatus = !filterStatus.value || deadlineKey(a.deadline) === filterStatus.value
    return matchSearch && matchCourse && matchStatus
  })
})

const currentAssignment = computed(() =>
  assignments.value.find(a => a.id === gradeTarget.value) ?? null
)

const currentSubmissions = computed(() =>
  submissions.value.filter(s => s.assignment_id === gradeTarget.value)
)

// ── Helpers ──────────────────────────────────────────────────────────────────
function blankForm() {
  return { course: '', title: '', description: '', deadline: '', max_score: 100 }
}

function submissionRate(a) {
  if (!a.enrolled_count) return 0
  return Math.round(a.submissions_count / a.enrolled_count * 100)
}

function deadlineKey(deadline) {
  const diff = (new Date(deadline) - Date.now()) / 3600000
  if (diff < 0)   return 'past_due'
  if (diff < 48)  return 'due_soon'
  return 'open'
}

function deadlineClass(deadline) {
  return {
    past_due: 'status-red',
    due_soon: 'status-warn',
    open:     'status-green',
  }[deadlineKey(deadline)]
}

function deadlineFill(deadline) {
  return { past_due: '#C62828', due_soon: '#F57C00', open: '#3D5AFE' }[deadlineKey(deadline)]
}

function deadlineLabel(deadline) {
  return { past_due: 'Past due', due_soon: 'Due soon', open: 'Open' }[deadlineKey(deadline)]
}

function formatDate(dt) {
  return new Date(dt).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function initials(name) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
}

// ── Actions ──────────────────────────────────────────────────────────────────
function openCreate() {
  modal.form    = blankForm()
  modal.errors  = {}
  modal.editing = false
  modal.open    = true
}

function openEdit(a) {
  modal.form    = { course: a.course, title: a.title, description: a.description, deadline: a.deadline.slice(0, 16), max_score: a.max_score }
  modal.errors  = {}
  modal.editing = true
  modal._id     = a.id
  modal.open    = true
}

function openGrade(a) {
  gradeTarget.value = a.id
  view.value = 'grade'
}

function validateModal() {
  const e = {}
  if (!modal.form.course)       e.course      = 'Please select a course'
  if (!modal.form.title.trim()) e.title       = 'Title is required'
  if (!modal.form.description.trim()) e.description = 'Instructions are required'
  if (!modal.form.deadline)     e.deadline    = 'Deadline is required'
  modal.errors = e
  return !Object.keys(e).length
}

function saveAssignment() {
  if (!validateModal()) return

  // ── API call would go here ──
  // if (modal.editing) await api.patch(`/assignments/${modal._id}/`, modal.form)
  // else               await api.post('/assignments/', modal.form)

  if (modal.editing) {
    const idx = assignments.value.findIndex(a => a.id === modal._id)
    if (idx !== -1) Object.assign(assignments.value[idx], {
      ...modal.form,
      course_title: courses.value.find(c => c.id === modal.form.course)?.title ?? '',
    })
    showToast('Assignment updated ✅')
  } else {
    assignments.value.push({
      id: Date.now(),
      ...modal.form,
      course_title: courses.value.find(c => c.id === modal.form.course)?.title ?? '',
      submissions_count: 0, enrolled_count: 0, graded_count: 0, avg_grade: null,
    })
    showToast('Assignment created ✅')
  }

  modal.open = false
}

function confirmDelete(a) {
  deleteConfirm.target = a
  deleteConfirm.open   = true
}

function deleteAssignment() {
  // await api.delete(`/assignments/${deleteConfirm.target.id}/`)
  assignments.value = assignments.value.filter(a => a.id !== deleteConfirm.target.id)
  deleteConfirm.open = false
  showToast('Assignment deleted')
}

function saveGrade(sub) {
  // await api.patch(`/submissions/${sub.id}/`, { grade: sub.grade, feedback: sub.feedback })
  showToast(`Saved grade for ${sub.student_name}`)
}

function showToast(msg) {
  toast.message = msg
  toast.visible = true
  setTimeout(() => { toast.visible = false }, 2600)
}
</script>

<style scoped>
/* ── Layout ── */
.page { padding: 32px 24px; max-width: 1100px; margin: 0 auto; font-family: 'DM Sans', system-ui, sans-serif; }

.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 24px; gap: 16px; flex-wrap: wrap;
}
.page-title { font-size: 24px; font-weight: 700; color: var(--text, #1A1916); margin-bottom: 4px; }
.page-sub   { font-size: 14px; color: #6B6860; }

/* ── Filters ── */
.filters-bar {
  display: flex; align-items: center; gap: 10px; margin-bottom: 24px; flex-wrap: wrap;
}
.search-wrap { position: relative; flex: 1; min-width: 200px; }
.search-icon { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); font-size: 14px; }
.search-input { padding-left: 34px !important; }
.filter-select { min-width: 160px; }

.tab-bar { display: flex; background: #F0EEE9; border-radius: 10px; padding: 3px; gap: 3px; }
.tab {
  padding: 7px 16px; border-radius: 8px; font-size: 13px; font-weight: 500;
  cursor: pointer; color: #6B6860; background: transparent; border: none;
  font-family: inherit; transition: all .2s;
}
.tab.active { background: #fff; color: #1A1916; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); }

/* ── Input base ── */
.input {
  width: 100%; background: #F6F5F2; border: 1px solid #E5E2DA;
  border-radius: 10px; padding: 9px 12px; font-size: 14px;
  color: #1A1916; font-family: inherit; outline: none; transition: border .2s, box-shadow .2s;
}
.input:focus  { border-color: #3D5AFE; box-shadow: 0 0 0 3px rgba(61,90,254,.1); }
.input.error  { border-color: #C62828; }
textarea.input { resize: vertical; }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border-radius: 10px; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all .2s; border: none; font-family: inherit;
}
.btn-primary { background: #3D5AFE; color: #fff; }
.btn-primary:hover { background: #1939B7; }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; }
.btn-ghost { background: transparent; color: #6B6860; border: 1px solid #E5E2DA; }
.btn-ghost:hover { background: #F0EEE9; color: #1A1916; }
.btn-danger { background: #FFEBEE; color: #C62828; }
.btn-danger:hover { background: #FFCDD2; }
.btn-sm { padding: 6px 14px; font-size: 13px; border-radius: 8px; }
.icon-btn {
  width: 30px; height: 30px; border-radius: 8px; border: 1px solid #E5E2DA;
  background: transparent; display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 14px; color: #6B6860; transition: background .15s;
}
.icon-btn:hover { background: #F0EEE9; }
.icon-btn.danger:hover { background: #FFEBEE; }

/* ── Assignment cards ── */
.assignment-list { display: flex; flex-direction: column; gap: 14px; }
.assignment-card {
  display: flex; align-items: stretch;
  background: #fff; border: 1px solid #E5E2DA; border-radius: 16px; overflow: hidden;
  transition: box-shadow .2s, transform .2s;
}
.assignment-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,.07); transform: translateY(-1px); }

.card-accent { width: 5px; flex-shrink: 0; }
.status-red   { background: #C62828; }
.status-warn  { background: #F57C00; }
.status-green { background: #00897B; }

.card-body { flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.card-top  { display: flex; gap: 20px; flex-wrap: wrap; }

.card-info { flex: 1; min-width: 200px; }
.course-badge {
  display: inline-block; background: #EEF1FF; color: #1939B7;
  font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 99px; margin-bottom: 6px;
}
.assign-title { font-size: 16px; font-weight: 700; color: #1A1916; margin-bottom: 4px; }
.assign-desc  { font-size: 13px; color: #6B6860; line-height: 1.5; }

.card-meta {
  display: grid; grid-template-columns: repeat(3, auto); gap: 10px 20px;
  align-content: start;
}
.meta-item { display: flex; flex-direction: column; }
.meta-label { font-size: 11px; font-weight: 600; color: #9C9A94; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 2px; }
.meta-val   { font-size: 14px; font-weight: 600; color: #1A1916; }
.meta-val.status-red  { color: #C62828; }
.meta-val.status-warn { color: #F57C00; }

.status-badge {
  display: inline-block; padding: 3px 10px; border-radius: 99px;
  font-size: 11px; font-weight: 700; letter-spacing: .04em;
  align-self: start;
}
.status-badge.status-red   { background: #FFEBEE; color: #C62828; }
.status-badge.status-warn  { background: #FFF3E0; color: #F57C00; }
.status-badge.status-green { background: #E0F2F1; color: #00897B; }

.submission-progress { display: flex; align-items: center; gap: 10px; }
.progress-bar  { flex: 1; height: 6px; background: #F0EEE9; border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 99px; transition: width .4s; }
.progress-pct  { font-size: 12px; font-weight: 600; color: #6B6860; white-space: nowrap; }

.card-actions {
  display: flex; flex-direction: column; justify-content: center; gap: 8px;
  padding: 16px; border-left: 1px solid #F0EEE9;
}

/* ── Grade view ── */
.grade-selector { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.grade-selector-label { font-size: 14px; font-weight: 600; color: #6B6860; white-space: nowrap; }

.grade-stats {
  display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;
}
.stat-pill {
  display: flex; align-items: center; gap: 6px;
  background: #F6F5F2; border: 1px solid #E5E2DA; border-radius: 99px;
  padding: 6px 14px; font-size: 13px; font-weight: 500; color: #1A1916;
}

.table-wrap { overflow-x: auto; border-radius: 14px; border: 1px solid #E5E2DA; }
table { width: 100%; border-collapse: collapse; background: #fff; }
thead th {
  padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: .06em; color: #9C9A94;
  border-bottom: 1px solid #E5E2DA; white-space: nowrap; background: #FAFAF8;
}
tbody td { padding: 12px 16px; font-size: 14px; color: #1A1916; border-bottom: 1px solid #F0EEE9; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #FAFAF8; }

.student-cell { display: flex; align-items: center; gap: 10px; }
.avatar-sm {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; flex-shrink: 0;
}
.grade-input-wrap { display: flex; align-items: center; }
.grade-input { width: 80px !important; text-align: center; }
.file-link { font-size: 13px; color: #3D5AFE; text-decoration: none; }
.file-link:hover { text-decoration: underline; }
.text-muted { color: #9C9A94; }
.text-sm    { font-size: 13px; }

/* ── Field helpers ── */
.field   { margin-bottom: 16px; }
.label   { display: block; font-size: 13px; font-weight: 600; color: #6B6860; margin-bottom: 5px; }
.req     { color: #C62828; margin-left: 2px; }
.err-msg { display: block; font-size: 12px; color: #A32D2D; margin-top: 4px; }
.grid-2  { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 560px) { .grid-2 { grid-template-columns: 1fr; } }

/* ── Modal ── */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 16px;
}
.modal {
  background: #fff; border-radius: 20px; width: 100%; max-width: 560px;
  box-shadow: 0 24px 64px rgba(0,0,0,.18); overflow: hidden;
}
.modal-sm { max-width: 420px; }
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px; border-bottom: 1px solid #E5E2DA;
}
.modal-title { font-size: 17px; font-weight: 700; color: #1A1916; }
.modal-body   { padding: 24px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid #E5E2DA; background: #FAFAF8;
}

/* ── Empty state ── */
.empty-state { text-align: center; padding: 64px 24px; }
.empty-icon  { font-size: 52px; margin-bottom: 12px; }
.empty-title { font-size: 18px; font-weight: 700; color: #1A1916; margin-bottom: 6px; }
.empty-sub   { font-size: 14px; color: #9C9A94; margin-bottom: 20px; }

/* ── Toast ── */
.toast {
  position: fixed; bottom: 24px; right: 24px; z-index: 999;
  background: #1A1916; color: #F0EEE9;
  padding: 12px 20px; border-radius: 12px; font-size: 14px; font-weight: 500;
}
.toast-enter-active, .toast-leave-active { transition: all .3s ease; }
.toast-enter-from, .toast-leave-to       { opacity: 0; transform: translateY(8px); }

/* ── Modal transition ── */
.modal-enter-active, .modal-leave-active { transition: all .25s ease; }
.modal-enter-from, .modal-leave-to       { opacity: 0; transform: scale(.96); }
</style>