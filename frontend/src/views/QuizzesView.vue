<template>
  <div class="page">

    <!-- Page header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Quizzes</h1>
        <p class="page-sub">{{ quizzes.length }} quiz{{ quizzes.length !== 1 ? 'zes' : '' }} across your courses</p>
      </div>
      <button class="btn btn-primary" @click="openCreate">+ New Quiz</button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input v-model="search" class="input search-input" placeholder="Search quizzes…" />
      </div>

      <select v-model="filterCourse" class="input filter-select">
        <option value="">All courses</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
      </select>

      <select v-model="filterStatus" class="input filter-select">
        <option value="">All</option>
        <option value="published">Published</option>
        <option value="draft">Draft</option>
      </select>

      <div class="tab-bar">
        <button class="tab" :class="{ active: view === 'list' }" @click="view = 'list'">Quizzes</button>
        <button class="tab" :class="{ active: view === 'results' }" @click="view = 'results'">Results</button>
      </div>
    </div>

    <!-- ── LIST VIEW ── -->
    <template v-if="view === 'list'">
      <div v-if="!filteredQuizzes.length" class="empty-state">
        <div class="empty-icon">🎯</div>
        <p class="empty-title">No quizzes yet</p>
        <p class="empty-sub">Create your first quiz to assess student knowledge.</p>
        <button class="btn btn-primary" @click="openCreate">+ New Quiz</button>
      </div>

      <div v-else class="quiz-grid">
        <div v-for="q in filteredQuizzes" :key="q.id" class="quiz-card">
          <div class="quiz-card-head">
            <div class="quiz-thumb">🎯</div>
            <span class="pub-badge" :class="q.is_published ? 'pub' : 'draft'">
              {{ q.is_published ? 'Published' : 'Draft' }}
            </span>
          </div>

          <div class="quiz-card-body">
            <span class="course-badge">{{ q.course_title }}</span>
            <h3 class="quiz-title">{{ q.title }}</h3>
            <p v-if="q.description" class="quiz-desc">{{ q.description }}</p>

            <div class="quiz-meta-row">
              <span class="quiz-meta-item">📝 {{ q.questions_count }} Q</span>
              <span class="quiz-meta-item">⏱ {{ q.time_limit_minutes ? q.time_limit_minutes + ' min' : 'No limit' }}</span>
              <span class="quiz-meta-item">🏆 Pass {{ q.passing_score }}%</span>
              <span class="quiz-meta-item">👥 {{ q.attempts_count }} attempts</span>
            </div>

            <!-- Pass rate bar -->
            <div v-if="q.attempts_count" class="pass-rate-row">
              <span class="pass-label">Pass rate</span>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{
                    width: q.pass_rate + '%',
                    background: q.pass_rate >= 70 ? '#00897B' : q.pass_rate >= 40 ? '#F57C00' : '#C62828'
                  }"
                />
              </div>
              <span class="pass-pct">{{ q.pass_rate }}%</span>
            </div>
          </div>

          <div class="quiz-card-footer">
            <button class="btn btn-ghost btn-sm" @click="openEdit(q)">Edit</button>
            <button class="btn btn-primary btn-sm" @click="openBuilder(q)">Build questions →</button>
            <button class="icon-btn danger" @click="confirmDelete(q)" title="Delete">🗑</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── RESULTS VIEW ── -->
    <template v-if="view === 'results'">
      <div class="grade-selector">
        <span class="grade-selector-label">Quiz:</span>
        <select v-model="resultsTarget" class="input filter-select" style="flex:1;max-width:360px">
          <option value="">Select a quiz</option>
          <option v-for="q in quizzes" :key="q.id" :value="q.id">{{ q.title }}</option>
        </select>
      </div>

      <div v-if="!resultsTarget" class="empty-state">
        <div class="empty-icon">📊</div>
        <p class="empty-title">Select a quiz above</p>
        <p class="empty-sub">View student attempt results, scores, and pass/fail breakdown.</p>
      </div>

      <template v-else>
        <div class="grade-stats">
          <div class="stat-pill">📬 {{ currentAttempts.length }} attempts</div>
          <div class="stat-pill">✅ {{ currentAttempts.filter(a => a.passed).length }} passed</div>
          <div class="stat-pill">❌ {{ currentAttempts.filter(a => !a.passed).length }} failed</div>
          <div class="stat-pill">📊 Avg {{ avgScore }}</div>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Score</th>
                <th>Result</th>
                <th>Submitted</th>
                <th>Breakdown</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="attempt in currentAttempts" :key="attempt.id">
                <td>
                  <div class="student-cell">
                    <div class="avatar-sm" :style="{ background: attempt.avatar_color + '22', color: attempt.avatar_color }">
                      {{ initials(attempt.student_name) }}
                    </div>
                    {{ attempt.student_name }}
                  </div>
                </td>
                <td>
                  <span class="score-chip" :class="attempt.passed ? 'score-pass' : 'score-fail'">
                    {{ attempt.score.toFixed(1) }}%
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="attempt.passed ? 'status-green' : 'status-red'">
                    {{ attempt.passed ? '✅ Passed' : '❌ Failed' }}
                  </span>
                </td>
                <td class="text-muted text-sm">{{ formatDate(attempt.submitted_at) }}</td>
                <td>
                  <div class="mini-bar-wrap">
                    <div class="mini-bar">
                      <div
                        class="mini-fill"
                        :style="{
                          width: attempt.score + '%',
                          background: attempt.passed ? '#00897B' : '#C62828'
                        }"
                      />
                    </div>
                    <span class="mini-pass-line" :style="{ left: currentQuiz.passing_score + '%' }" title="Pass threshold" />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>

    <!-- ── QUESTION BUILDER PANEL ── -->
    <Transition name="slide-right">
      <div v-if="builder.open" class="builder-overlay" @click.self="builder.open = false">
        <div class="builder-panel">
          <div class="builder-header">
            <div>
              <h2 class="builder-title">Question Builder</h2>
              <p class="builder-sub">{{ builder.quiz?.title }}</p>
            </div>
            <button class="icon-btn" @click="builder.open = false">✕</button>
          </div>

          <div class="builder-body">
            <!-- Quiz settings strip -->
            <div class="quiz-settings-strip">
              <div class="setting-item">
                <label class="label">Passing score (%)</label>
                <input v-model.number="builder.quiz.passing_score" class="input" type="number" min="0" max="100" style="width:90px" />
              </div>
              <div class="setting-item">
                <label class="label">Time limit (min)</label>
                <input v-model.number="builder.quiz.time_limit_minutes" class="input" type="number" min="1" placeholder="None" style="width:90px" />
              </div>
              <div class="setting-item">
                <label class="label">Published</label>
                <div
                  class="toggle"
                  :class="{ on: builder.quiz.is_published }"
                  role="switch"
                  :aria-checked="builder.quiz.is_published"
                  tabindex="0"
                  @click="builder.quiz.is_published = !builder.quiz.is_published"
                  @keydown.enter="builder.quiz.is_published = !builder.quiz.is_published"
                >
                  <div class="toggle-knob" />
                </div>
              </div>
            </div>

            <!-- Question list -->
            <div class="q-list">
              <div
                v-for="(q, qi) in builder.questions"
                :key="q._uid"
                class="q-card"
                :class="{ expanded: q._open }"
              >
                <!-- Question header row -->
                <div class="q-header" @click="q._open = !q._open">
                  <div class="q-num">Q{{ qi + 1 }}</div>
                  <div class="q-preview">
                    <span class="q-text-preview">{{ q.text || 'Untitled question' }}</span>
                    <span class="q-type-badge">{{ typeLabel(q.question_type) }}</span>
                  </div>
                  <div class="q-pts">{{ q.points }} pt{{ q.points !== 1 ? 's' : '' }}</div>
                  <div class="q-header-actions" @click.stop>
                    <button class="icon-btn" @click="moveQuestion(qi, -1)" :disabled="qi === 0" title="Move up">↑</button>
                    <button class="icon-btn" @click="moveQuestion(qi, 1)"  :disabled="qi === builder.questions.length - 1" title="Move down">↓</button>
                    <button class="icon-btn danger" @click="removeQuestion(qi)" title="Delete">🗑</button>
                  </div>
                  <span class="chevron">{{ q._open ? '▲' : '▼' }}</span>
                </div>

                <!-- Expanded editor -->
                <div v-if="q._open" class="q-editor">
                  <div class="field">
                    <label class="label">Question text <span class="req">*</span></label>
                    <textarea v-model="q.text" class="input" rows="2" placeholder="Enter your question…" />
                  </div>

                  <div class="grid-3">
                    <div class="field" style="margin-bottom:0">
                      <label class="label">Type</label>
                      <select v-model="q.question_type" class="input" @change="onTypeChange(q)">
                        <option value="multiple_choice">Multiple choice</option>
                        <option value="true_false">True / False</option>
                        <option value="short_answer">Short answer</option>
                      </select>
                    </div>
                    <div class="field" style="margin-bottom:0">
                      <label class="label">Points</label>
                      <input v-model.number="q.points" class="input" type="number" min="1" />
                    </div>
                    <div class="field" style="margin-bottom:0">
                      <label class="label">Order</label>
                      <input v-model.number="q.order_number" class="input" type="number" min="1" />
                    </div>
                  </div>

                  <!-- Multiple choice / True-False options -->
                  <template v-if="q.question_type !== 'short_answer'">
                    <label class="label mt-3">Answer options <span class="hint-inline">(check the correct one)</span></label>
                    <div class="options-list">
                      <div
                        v-for="(opt, oi) in q.options"
                        :key="oi"
                        class="option-row"
                        :class="{ 'option-correct': opt.is_correct }"
                      >
                        <label class="correct-check" :title="q.question_type === 'true_false' ? '' : 'Mark as correct'">
                          <input
                            type="radio"
                            :name="'correct-' + q._uid"
                            :checked="opt.is_correct"
                            @change="setCorrect(q, oi)"
                          />
                        </label>
                        <input
                          v-model="opt.text"
                          class="input"
                          :placeholder="'Option ' + (oi + 1)"
                          :readonly="q.question_type === 'true_false'"
                        />
                        <button
                          v-if="q.question_type === 'multiple_choice'"
                          class="icon-btn danger"
                          :disabled="q.options.length <= 2"
                          @click="removeOption(q, oi)"
                          title="Remove option"
                        >🗑</button>
                      </div>
                    </div>
                    <button
                      v-if="q.question_type === 'multiple_choice'"
                      class="add-opt-btn"
                      @click="addOption(q)"
                    >+ Add option</button>
                  </template>

                  <!-- Short answer -->
                  <template v-else>
                    <div class="field mt-3" style="margin-bottom:0">
                      <label class="label">Accepted answer <span class="hint-inline">(used for auto-grading)</span></label>
                      <input v-model="q.options[0].text" class="input" placeholder="Expected answer text…" />
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <!-- Add question types -->
            <div class="add-q-grid">
              <button class="add-q-btn" @click="addQuestion('multiple_choice')">+ Multiple choice</button>
              <button class="add-q-btn" @click="addQuestion('true_false')">+ True / False</button>
              <button class="add-q-btn" @click="addQuestion('short_answer')">+ Short answer</button>
            </div>
          </div>

          <div class="builder-footer">
            <span class="q-count-label">{{ builder.questions.length }} question{{ builder.questions.length !== 1 ? 's' : '' }}</span>
            <button class="btn btn-ghost" @click="builder.open = false">Cancel</button>
            <button class="btn btn-primary" @click="saveBuilder">Save quiz</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── CREATE / EDIT MODAL ── -->
    <Transition name="modal">
      <div v-if="modal.open" class="modal-backdrop" @click.self="modal.open = false">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">{{ modal.editing ? 'Edit Quiz' : 'New Quiz' }}</h2>
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
              <input v-model="modal.form.title" class="input" :class="{ error: modal.errors.title }" placeholder="e.g. JavaScript Fundamentals Quiz" />
              <span v-if="modal.errors.title" class="err-msg">⚠ {{ modal.errors.title }}</span>
            </div>
            <div class="field">
              <label class="label">Description</label>
              <textarea v-model="modal.form.description" class="input" rows="3" placeholder="Short description for students…" />
            </div>
            <div class="grid-3">
              <div class="field" style="margin-bottom:0">
                <label class="label">Passing score (%)</label>
                <input v-model.number="modal.form.passing_score" class="input" type="number" min="0" max="100" />
              </div>
              <div class="field" style="margin-bottom:0">
                <label class="label">Time limit (min)</label>
                <input v-model.number="modal.form.time_limit_minutes" class="input" type="number" min="1" placeholder="None" />
              </div>
              <div class="field" style="margin-bottom:0">
                <label class="label">Published</label>
                <div
                  class="toggle mt-1"
                  :class="{ on: modal.form.is_published }"
                  role="switch"
                  :aria-checked="modal.form.is_published"
                  tabindex="0"
                  @click="modal.form.is_published = !modal.form.is_published"
                  @keydown.enter="modal.form.is_published = !modal.form.is_published"
                >
                  <div class="toggle-knob" />
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="modal.open = false">Cancel</button>
            <button class="btn btn-primary" @click="saveQuiz">
              {{ modal.editing ? 'Update Quiz' : 'Create & Build Questions →' }}
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
            <h2 class="modal-title">Delete quiz?</h2>
            <button class="icon-btn" @click="deleteConfirm.open = false">✕</button>
          </div>
          <div class="modal-body">
            <p class="text-muted" style="font-size:14px">
              "<strong>{{ deleteConfirm.target?.title }}</strong>" and all student attempt records will be permanently removed.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="deleteConfirm.open = false">Cancel</button>
            <button class="btn btn-danger" @click="deleteQuiz">Delete permanently</button>
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

// ── Mock data (replace with api.get('/quizzes/') in onMounted) ───────────────
const courses = ref([
  { id: 1, title: 'Full-Stack Web Development' },
  { id: 2, title: 'Data Science with Python'   },
  { id: 3, title: 'UI/UX Design Fundamentals'  },
])

const quizzes = ref([
  {
    id: 1, course: 1, course_title: 'Full-Stack Web Development',
    title: 'JavaScript Basics Quiz',
    description: 'Test your knowledge of core JS concepts including variables, scope, and ES6.',
    passing_score: 70, time_limit_minutes: 20, is_published: true,
    questions_count: 10, attempts_count: 28, pass_rate: 75,
    questions: [],
  },
  {
    id: 2, course: 1, course_title: 'Full-Stack Web Development',
    title: 'REST API Design Quiz',
    description: 'HTTP methods, status codes, and REST principles.',
    passing_score: 60, time_limit_minutes: null, is_published: true,
    questions_count: 8, attempts_count: 22, pass_rate: 54,
    questions: [],
  },
  {
    id: 3, course: 2, course_title: 'Data Science with Python',
    title: 'Pandas & NumPy Fundamentals',
    description: '',
    passing_score: 75, time_limit_minutes: 30, is_published: false,
    questions_count: 0, attempts_count: 0, pass_rate: 0,
    questions: [],
  },
])

const attempts = ref([
  { id: 1, quiz_id: 1, student_name: 'Alice Martin',  score: 90,  passed: true,  submitted_at: '2024-08-05T14:20:00', avatar_color: '#3D5AFE' },
  { id: 2, quiz_id: 1, student_name: 'Bob Chen',      score: 60,  passed: false, submitted_at: '2024-08-06T09:10:00', avatar_color: '#00897B' },
  { id: 3, quiz_id: 1, student_name: 'Carol Davis',   score: 80,  passed: true,  submitted_at: '2024-08-06T11:30:00', avatar_color: '#7C3AED' },
  { id: 4, quiz_id: 1, student_name: 'David Kim',     score: 50,  passed: false, submitted_at: '2024-08-07T08:55:00', avatar_color: '#DB2777' },
  { id: 5, quiz_id: 2, student_name: 'Eva Lopez',     score: 87.5,passed: true,  submitted_at: '2024-08-04T16:40:00', avatar_color: '#F57C00' },
])

// ── State ─────────────────────────────────────────────────────────────────────
const search        = ref('')
const filterCourse  = ref('')
const filterStatus  = ref('')
const view          = ref('list')
const resultsTarget = ref('')

const modal = reactive({
  open: false, editing: false, _id: null,
  form: blankForm(),
  errors: {},
})

const builder = reactive({
  open: false,
  quiz: null,
  questions: [],
})

const deleteConfirm = reactive({ open: false, target: null })
const toast = reactive({ visible: false, message: '' })

let _uid = 0

// ── Computed ──────────────────────────────────────────────────────────────────
const filteredQuizzes = computed(() =>
  quizzes.value.filter(q => {
    const ms = !search.value ||
      q.title.toLowerCase().includes(search.value.toLowerCase()) ||
      q.course_title.toLowerCase().includes(search.value.toLowerCase())
    const mc = !filterCourse.value || q.course === filterCourse.value
    const mp = !filterStatus.value ||
      (filterStatus.value === 'published' ? q.is_published : !q.is_published)
    return ms && mc && mp
  })
)

const currentQuiz = computed(() => quizzes.value.find(q => q.id === resultsTarget.value) ?? null)
const currentAttempts = computed(() => attempts.value.filter(a => a.quiz_id === resultsTarget.value))
const avgScore = computed(() => {
  if (!currentAttempts.value.length) return '—'
  const avg = currentAttempts.value.reduce((s, a) => s + a.score, 0) / currentAttempts.value.length
  return avg.toFixed(1) + '%'
})

// ── Helpers ───────────────────────────────────────────────────────────────────
function blankForm() {
  return { course: '', title: '', description: '', passing_score: 70, time_limit_minutes: null, is_published: true }
}

function typeLabel(t) {
  return { multiple_choice: 'MC', true_false: 'T/F', short_answer: 'SA' }[t] ?? t
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

function makeQuestion(type) {
  const base = { _uid: ++_uid, _open: true, text: '', question_type: type, points: 1, order_number: 1, options: [] }
  if (type === 'multiple_choice') {
    base.options = [
      { text: '', is_correct: true  },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
    ]
  } else if (type === 'true_false') {
    base.options = [
      { text: 'True',  is_correct: true  },
      { text: 'False', is_correct: false },
    ]
  } else {
    base.options = [{ text: '', is_correct: true }]
  }
  return base
}

// ── Builder actions ───────────────────────────────────────────────────────────
function openBuilder(quiz) {
  builder.quiz = { ...quiz }
  // In production: load questions from api.get(`/quizzes/${quiz.id}/questions/`)
  builder.questions = (quiz.questions ?? []).map(q => ({ ...q, _uid: ++_uid, _open: false }))
  builder.open = true
}

function addQuestion(type) {
  const q = makeQuestion(type)
  q.order_number = builder.questions.length + 1
  builder.questions.push(q)
}

function removeQuestion(qi) {
  builder.questions.splice(qi, 1)
  builder.questions.forEach((q, i) => { q.order_number = i + 1 })
}

function moveQuestion(qi, dir) {
  const target = qi + dir
  if (target < 0 || target >= builder.questions.length) return
  const tmp = builder.questions[qi]
  builder.questions[qi] = builder.questions[target]
  builder.questions[target] = tmp
  builder.questions.forEach((q, i) => { q.order_number = i + 1 })
}

function onTypeChange(q) {
  if (q.question_type === 'true_false') {
    q.options = [{ text: 'True', is_correct: true }, { text: 'False', is_correct: false }]
  } else if (q.question_type === 'short_answer') {
    q.options = [{ text: '', is_correct: true }]
  } else {
    q.options = [
      { text: '', is_correct: true  },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
    ]
  }
}

function setCorrect(q, correctIdx) {
  q.options.forEach((o, i) => { o.is_correct = i === correctIdx })
}

function addOption(q) {
  q.options.push({ text: '', is_correct: false })
}

function removeOption(q, oi) {
  if (q.options.length <= 2) return
  q.options.splice(oi, 1)
  if (!q.options.some(o => o.is_correct)) q.options[0].is_correct = true
}

function saveBuilder() {
  // In production:
  // await api.put(`/quizzes/${builder.quiz.id}/`, { ...builder.quiz, questions: builder.questions })
  const idx = quizzes.value.findIndex(q => q.id === builder.quiz.id)
  if (idx !== -1) {
    Object.assign(quizzes.value[idx], {
      ...builder.quiz,
      questions_count: builder.questions.length,
      is_published: builder.quiz.is_published,
    })
  }
  builder.open = false
  showToast('Quiz saved ✅')
}

// ── Quiz CRUD ─────────────────────────────────────────────────────────────────
function openCreate() {
  modal.form    = blankForm()
  modal.errors  = {}
  modal.editing = false
  modal._id     = null
  modal.open    = true
}

function openEdit(q) {
  modal.form    = { course: q.course, title: q.title, description: q.description, passing_score: q.passing_score, time_limit_minutes: q.time_limit_minutes, is_published: q.is_published }
  modal.errors  = {}
  modal.editing = true
  modal._id     = q.id
  modal.open    = true
}

function validateModal() {
  const e = {}
  if (!modal.form.course)         e.course = 'Please select a course'
  if (!modal.form.title.trim())   e.title  = 'Title is required'
  modal.errors = e
  return !Object.keys(e).length
}

function saveQuiz() {
  if (!validateModal()) return

  if (modal.editing) {
    // await api.patch(`/quizzes/${modal._id}/`, modal.form)
    const idx = quizzes.value.findIndex(q => q.id === modal._id)
    if (idx !== -1) Object.assign(quizzes.value[idx], {
      ...modal.form,
      course_title: courses.value.find(c => c.id === modal.form.course)?.title ?? '',
    })
    showToast('Quiz updated ✅')
    modal.open = false
  } else {
    // const res = await api.post('/quizzes/', modal.form)
    const newQuiz = {
      id: Date.now(), ...modal.form,
      course_title: courses.value.find(c => c.id === modal.form.course)?.title ?? '',
      questions_count: 0, attempts_count: 0, pass_rate: 0, questions: [],
    }
    quizzes.value.push(newQuiz)
    modal.open = false
    // Jump straight into builder
    openBuilder(newQuiz)
    showToast('Quiz created — add your questions below')
  }
}

function confirmDelete(q) {
  deleteConfirm.target = q
  deleteConfirm.open   = true
}

function deleteQuiz() {
  // await api.delete(`/quizzes/${deleteConfirm.target.id}/`)
  quizzes.value = quizzes.value.filter(q => q.id !== deleteConfirm.target.id)
  deleteConfirm.open = false
  showToast('Quiz deleted')
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
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 24px; flex-wrap: wrap;
}
.search-wrap  { position: relative; flex: 1; min-width: 200px; }
.search-icon  { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); font-size: 14px; }
.search-input { padding-left: 34px !important; }
.filter-select { min-width: 160px; }

.tab-bar { display: flex; background: #F0EEE9; border-radius: 10px; padding: 3px; gap: 3px; }
.tab {
  padding: 7px 16px; border-radius: 8px; font-size: 13px; font-weight: 500;
  cursor: pointer; color: #6B6860; background: transparent; border: none;
  font-family: inherit; transition: all .2s;
}
.tab.active { background: #fff; color: #1A1916; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); }

/* ── Input ── */
.input {
  width: 100%; background: #F6F5F2; border: 1px solid #E5E2DA;
  border-radius: 10px; padding: 9px 12px; font-size: 14px;
  color: #1A1916; font-family: inherit; outline: none;
  transition: border .2s, box-shadow .2s;
}
.input:focus { border-color: #3D5AFE; box-shadow: 0 0 0 3px rgba(61,90,254,.1); }
.input.error { border-color: #C62828; }
textarea.input { resize: vertical; }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border-radius: 10px; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all .2s; border: none; font-family: inherit;
}
.btn-primary { background: #3D5AFE; color: #fff; }
.btn-primary:hover { background: #1939B7; }
.btn-ghost { background: transparent; color: #6B6860; border: 1px solid #E5E2DA; }
.btn-ghost:hover { background: #F0EEE9; color: #1A1916; }
.btn-danger { background: #FFEBEE; color: #C62828; }
.btn-danger:hover { background: #FFCDD2; }
.btn-sm { padding: 6px 14px; font-size: 13px; border-radius: 8px; }
.icon-btn {
  width: 30px; height: 30px; border-radius: 8px; border: 1px solid #E5E2DA;
  background: transparent; display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 14px; color: #6B6860; transition: background .15s; font-family: inherit;
}
.icon-btn:hover { background: #F0EEE9; }
.icon-btn.danger:hover { background: #FFEBEE; }
.icon-btn:disabled { opacity: .3; cursor: not-allowed; }

/* ── Quiz grid ── */
.quiz-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.quiz-card {
  background: #fff; border: 1px solid #E5E2DA; border-radius: 16px;
  overflow: hidden; display: flex; flex-direction: column;
  transition: box-shadow .2s, transform .2s;
}
.quiz-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,.07); transform: translateY(-2px); }

.quiz-card-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 16px 0; 
}
.quiz-thumb { font-size: 32px; }
.pub-badge {
  padding: 4px 10px; border-radius: 99px; font-size: 11px; font-weight: 700;
}
.pub-badge.pub   { background: #E0F2F1; color: #00897B; }
.pub-badge.draft { background: #F0EEE9; color: #6B6860; }

.quiz-card-body { flex: 1; padding: 12px 16px 16px; }
.course-badge {
  display: inline-block; background: #EEF1FF; color: #1939B7;
  font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 99px; margin-bottom: 6px;
}
.quiz-title { font-size: 15px; font-weight: 700; color: #1A1916; margin-bottom: 4px; }
.quiz-desc  { font-size: 13px; color: #9C9A94; line-height: 1.5; margin-bottom: 10px; }

.quiz-meta-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.quiz-meta-item {
  background: #F6F5F2; border: 1px solid #E5E2DA; border-radius: 99px;
  padding: 3px 9px; font-size: 12px; color: #6B6860;
}

.pass-rate-row { display: flex; align-items: center; gap: 8px; }
.pass-label { font-size: 12px; color: #9C9A94; white-space: nowrap; }
.progress-bar { flex: 1; height: 6px; background: #F0EEE9; border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 99px; transition: width .4s; }
.pass-pct { font-size: 12px; font-weight: 600; color: #6B6860; white-space: nowrap; }

.quiz-card-footer {
  display: flex; align-items: center; gap: 8px; padding: 12px 16px;
  border-top: 1px solid #F0EEE9;
}

/* ── Results ── */
.grade-selector { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.grade-selector-label { font-size: 14px; font-weight: 600; color: #6B6860; white-space: nowrap; }
.grade-stats { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.stat-pill {
  display: flex; align-items: center; gap: 6px;
  background: #F6F5F2; border: 1px solid #E5E2DA;
  border-radius: 99px; padding: 6px 14px; font-size: 13px; font-weight: 500; color: #1A1916;
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
.score-chip {
  display: inline-block; padding: 4px 10px; border-radius: 99px;
  font-size: 13px; font-weight: 700;
}
.score-pass { background: #E0F2F1; color: #00897B; }
.score-fail { background: #FFEBEE; color: #C62828; }

.status-badge {
  display: inline-block; padding: 3px 10px; border-radius: 99px;
  font-size: 12px; font-weight: 600;
}
.status-green { background: #E0F2F1; color: #00897B; }
.status-red   { background: #FFEBEE; color: #C62828; }
.status-warn  { background: #FFF3E0; color: #F57C00; }

.mini-bar-wrap { position: relative; display: flex; align-items: center; min-width: 120px; }
.mini-bar { flex: 1; height: 8px; background: #F0EEE9; border-radius: 99px; overflow: hidden; }
.mini-fill { height: 100%; border-radius: 99px; transition: width .4s; }
.mini-pass-line {
  position: absolute; top: -3px; width: 2px; height: 14px;
  background: #1A1916; border-radius: 1px; pointer-events: none;
}

.text-muted { color: #9C9A94; }
.text-sm    { font-size: 13px; }

/* ── Builder panel ── */
.builder-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; justify-content: flex-end; z-index: 300;
}
.builder-panel {
  width: 100%; max-width: 680px; height: 100%;
  background: #fff; display: flex; flex-direction: column;
  box-shadow: -8px 0 40px rgba(0,0,0,.15);
}
.builder-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 20px 24px; border-bottom: 1px solid #E5E2DA; flex-shrink: 0;
}
.builder-title { font-size: 18px; font-weight: 700; color: #1A1916; margin-bottom: 3px; }
.builder-sub   { font-size: 13px; color: #9C9A94; }
.builder-body  { flex: 1; overflow-y: auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.builder-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid #E5E2DA; background: #FAFAF8; flex-shrink: 0;
}
.q-count-label { font-size: 13px; color: #9C9A94; margin-right: auto; }

/* Quiz settings strip */
.quiz-settings-strip {
  display: flex; gap: 20px; flex-wrap: wrap; align-items: flex-end;
  background: #F6F5F2; border: 1px solid #E5E2DA; border-radius: 12px; padding: 14px 16px;
}
.setting-item { display: flex; flex-direction: column; gap: 5px; }

/* Questions */
.q-list { display: flex; flex-direction: column; gap: 10px; }
.q-card {
  border: 1px solid #E5E2DA; border-radius: 14px; overflow: hidden;
  transition: border-color .2s;
}
.q-card.expanded { border-color: #3D5AFE; }

.q-header {
  display: flex; align-items: center; gap: 10px; padding: 12px 14px;
  cursor: pointer; background: #FAFAF8; user-select: none;
}
.q-header:hover { background: #F0EEE9; }

.q-num {
  width: 26px; height: 26px; border-radius: 7px; background: #E5E2DA;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #6B6860; flex-shrink: 0;
}
.q-card.expanded .q-num { background: #3D5AFE; color: #fff; }

.q-preview { flex: 1; display: flex; align-items: center; gap: 8px; min-width: 0; }
.q-text-preview {
  font-size: 14px; color: #1A1916; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; flex: 1;
}
.q-type-badge {
  flex-shrink: 0; font-size: 10px; font-weight: 700; padding: 2px 7px;
  border-radius: 99px; background: #EEF1FF; color: #3D5AFE;
}

.q-pts { font-size: 13px; font-weight: 600; color: #6B6860; white-space: nowrap; flex-shrink: 0; }
.q-header-actions { display: flex; gap: 4px; flex-shrink: 0; }
.chevron { font-size: 10px; color: #9C9A94; flex-shrink: 0; }

.q-editor {
  padding: 16px; border-top: 1px solid #E5E2DA;
  display: flex; flex-direction: column; gap: 12px;
}

/* Options */
.options-list { display: flex; flex-direction: column; gap: 8px; }
.option-row {
  display: grid; grid-template-columns: 24px 1fr 30px; gap: 8px;
  align-items: center; padding: 8px 10px; border-radius: 10px;
  border: 1px solid #E5E2DA; transition: border .2s, background .2s;
}
.option-row.option-correct { border-color: #00897B; background: #F0FBF9; }
.correct-check { display: flex; align-items: center; justify-content: center; cursor: pointer; }
.correct-check input { accent-color: #00897B; width: 16px; height: 16px; cursor: pointer; }
.add-opt-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px; border-radius: 8px; border: 1px dashed #D3D1C7;
  background: transparent; color: #6B6860; font-size: 13px; cursor: pointer;
  font-family: inherit; transition: all .15s;
}
.add-opt-btn:hover { background: #EEF1FF; color: #3D5AFE; border-color: #85B7EB; }

/* Add question grid */
.add-q-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.add-q-btn {
  padding: 10px; border-radius: 10px; border: 1px dashed #D3D1C7;
  background: transparent; color: #6B6860; font-size: 13px; cursor: pointer;
  font-family: inherit; text-align: center; transition: all .15s;
}
.add-q-btn:hover { background: #EEF1FF; color: #3D5AFE; border-color: #85B7EB; }
@media (max-width: 480px) { .add-q-grid { grid-template-columns: 1fr; } }

/* ── Toggle ── */
.toggle {
  width: 40px; height: 22px; border-radius: 11px; background: #D3D1C7;
  position: relative; cursor: pointer; transition: background .25s; flex-shrink: 0;
}
.toggle.on { background: #3D5AFE; }
.toggle-knob {
  width: 16px; height: 16px; border-radius: 50%; background: #fff;
  position: absolute; top: 3px; left: 3px; transition: transform .25s;
}
.toggle.on .toggle-knob { transform: translateX(18px); }
.mt-1 { margin-top: 4px; }

/* ── Field ── */
.field   { margin-bottom: 16px; }
.label   { display: block; font-size: 13px; font-weight: 600; color: #6B6860; margin-bottom: 5px; }
.req     { color: #C62828; margin-left: 2px; }
.err-msg { display: block; font-size: 12px; color: #A32D2D; margin-top: 4px; }
.hint-inline { font-size: 12px; font-weight: 400; color: #9C9A94; }
.mt-3   { margin-top: 12px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
@media (max-width: 500px) { .grid-3 { grid-template-columns: 1fr; } }

/* ── Modal ── */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; z-index: 200; padding: 16px;
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
.modal-title  { font-size: 17px; font-weight: 700; color: #1A1916; }
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

/* ── Transitions ── */
.modal-enter-active, .modal-leave-active { transition: all .25s ease; }
.modal-enter-from, .modal-leave-to       { opacity: 0; transform: scale(.96); }

.slide-right-enter-active, .slide-right-leave-active { transition: all .3s ease; }
.slide-right-enter-from, .slide-right-leave-to       { opacity: 0; transform: translateX(40px); }
</style>