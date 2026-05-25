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
              <span class="quiz-meta-item">⏱ {{ q.time_limit_minutes ? q.time_limit_minutes + ' min' : 'No limit'
                }}</span>
              <span class="quiz-meta-item">🏆 Pass {{ q.passing_score }}%</span>
              <span class="quiz-meta-item">👥 {{ q.attempts_count }} attempts</span>
            </div>

            <!-- Pass rate bar -->
            <div v-if="q.attempts_count" class="pass-rate-row">
              <span class="pass-label">Pass rate</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{
                  width: q.pass_rate + '%',
                  background: q.pass_rate >= 70 ? '#00897B' : q.pass_rate >= 40 ? '#F57C00' : '#C62828'
                }" />
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
          <div class="stat-pill">✅ {{currentAttempts.filter(a => a.passed).length}} passed</div>
          <div class="stat-pill">❌ {{currentAttempts.filter(a => !a.passed).length}} failed</div>
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
                    <div class="avatar-sm"
                      :style="{ background: attempt.avatar_color + '22', color: attempt.avatar_color }">
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
                      <div class="mini-fill" :style="{
                        width: attempt.score + '%',
                        background: attempt.passed ? '#00897B' : '#C62828'
                      }" />
                    </div>
                    <span class="mini-pass-line" :style="{ left: currentQuiz.passing_score + '%' }"
                      title="Pass threshold" />
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
                <input v-model.number="builder.quiz.passing_score" class="input" type="number" min="0" max="100"
                  style="width:90px" />
              </div>
              <div class="setting-item">
                <label class="label">Time limit (min)</label>
                <input v-model.number="builder.quiz.time_limit_minutes" class="input" type="number" min="1"
                  placeholder="None" style="width:90px" />
              </div>
              <div class="setting-item">
                <label class="label">Published</label>
                <div class="toggle" :class="{ on: builder.quiz.is_published }" role="switch"
                  :aria-checked="builder.quiz.is_published" tabindex="0"
                  @click="builder.quiz.is_published = !builder.quiz.is_published"
                  @keydown.enter="builder.quiz.is_published = !builder.quiz.is_published">
                  <div class="toggle-knob" />
                </div>
              </div>
            </div>

            <!-- Question list -->
            <div class="q-list">
              <div v-for="(q, qi) in builder.questions" :key="q._uid" class="q-card" :class="{ expanded: q._open }">
                <!-- Question header row -->
                <div class="q-header" @click="q._open = !q._open">
                  <div class="q-num">Q{{ qi + 1 }}</div>
                  <div class="q-preview">
                    <span class="q-text-preview">{{ q.text || 'Untitled question' }}</span>
                    <span class="q-type-badge">{{ typeLabel(q.question_type) }}</span>
                  </div>
                  <div class="q-pts">{{ q.points }} pt{{ q.points !== 1 ? 's' : '' }}</div>
                  <div class="q-header-actions" @click.stop>
                    <button class="icon-btn" @click="moveQuestion(qi, -1)" :disabled="qi === 0"
                      title="Move up">↑</button>
                    <button class="icon-btn" @click="moveQuestion(qi, 1)"
                      :disabled="qi === builder.questions.length - 1" title="Move down">↓</button>
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
                    <label class="label mt-3">Answer options <span class="hint-inline">(check the correct
                        one)</span></label>
                    <div class="options-list">
                      <div v-for="(opt, oi) in q.options" :key="oi" class="option-row"
                        :class="{ 'option-correct': opt.is_correct }">
                        <label class="correct-check" :title="q.question_type === 'true_false' ? '' : 'Mark as correct'">
                          <input type="radio" :name="'correct-' + q._uid" :checked="opt.is_correct"
                            @change="setCorrect(q, oi)" />
                        </label>
                        <input v-model="opt.text" class="input" :placeholder="'Option ' + (oi + 1)"
                          :readonly="q.question_type === 'true_false'" />
                        <button v-if="q.question_type === 'multiple_choice'" class="icon-btn danger"
                          :disabled="q.options.length <= 2" @click="removeOption(q, oi)"
                          title="Remove option">🗑</button>
                      </div>
                    </div>
                    <button v-if="q.question_type === 'multiple_choice'" class="add-opt-btn" @click="addOption(q)">+ Add
                      option</button>
                  </template>

                  <!-- Short answer -->
                  <template v-else>
                    <div class="field mt-3" style="margin-bottom:0">
                      <label class="label">Accepted answer <span class="hint-inline">(used for
                          auto-grading)</span></label>
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
            <span class="q-count-label">{{ builder.questions.length }} question{{ builder.questions.length !== 1 ? 's' :
              ''
              }}</span>
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
              <input v-model="modal.form.title" class="input" :class="{ error: modal.errors.title }"
                placeholder="e.g. JavaScript Fundamentals Quiz" />
              <span v-if="modal.errors.title" class="err-msg">⚠ {{ modal.errors.title }}</span>
            </div>
            <div class="field">
              <label class="label">Description</label>
              <textarea v-model="modal.form.description" class="input" rows="3"
                placeholder="Short description for students…" />
            </div>
            <div class="grid-3">
              <div class="field" style="margin-bottom:0">
                <label class="label">Passing score (%)</label>
                <input v-model.number="modal.form.passing_score" class="input" type="number" min="0" max="100" />
              </div>
              <div class="field" style="margin-bottom:0">
                <label class="label">Time limit (min)</label>
                <input v-model.number="modal.form.time_limit_minutes" class="input" type="number" min="1"
                  placeholder="None" />
              </div>
              <div class="field" style="margin-bottom:0">
                <label class="label">Published</label>
                <div class="toggle mt-1" :class="{ on: modal.form.is_published }" role="switch"
                  :aria-checked="modal.form.is_published" tabindex="0"
                  @click="modal.form.is_published = !modal.form.is_published"
                  @keydown.enter="modal.form.is_published = !modal.form.is_published">
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
              "<strong>{{ deleteConfirm.target?.title }}</strong>" and all student attempt records will be permanently
              removed.
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
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

const courses = ref([])
const quizzes = ref([])
const attempts = ref([])

const loading = ref(false)

const search = ref('')
const filterCourse = ref('')
const filterStatus = ref('')
const view = ref('list')
const resultsTarget = ref('')

const modal = reactive({
  open: false,
  editing: false,
  _id: null,
  form: blankForm(),
  errors: {},
})

const builder = reactive({
  open: false,
  quiz: null,
  questions: [],
})

const deleteConfirm = reactive({
  open: false,
  target: null,
})

const toast = reactive({
  visible: false,
  message: '',
})

let _uid = 0

const filteredQuizzes = computed(() => {
  return quizzes.value.filter((q) => {
    const term = search.value.toLowerCase()

    const matchesSearch =
      !term ||
      q.title?.toLowerCase().includes(term) ||
      q.course_title?.toLowerCase().includes(term)

    const matchesCourse =
      !filterCourse.value ||
      Number(q.course) === Number(filterCourse.value)

    const matchesStatus =
      !filterStatus.value ||
      (
        filterStatus.value === 'published'
          ? q.is_published
          : !q.is_published
      )

    return matchesSearch && matchesCourse && matchesStatus
  })
})

const currentQuiz = computed(() => {
  return quizzes.value.find(
    (q) => Number(q.id) === Number(resultsTarget.value)
  ) || null
})

const currentAttempts = computed(() => {
  return attempts.value.filter(
    (a) => Number(a.quiz_id) === Number(resultsTarget.value)
  )
})

const avgScore = computed(() => {
  if (!currentAttempts.value.length) return '—'

  const avg =
    currentAttempts.value.reduce(
      (sum, attempt) => sum + Number(attempt.score || 0),
      0
    ) / currentAttempts.value.length

  return avg.toFixed(1) + '%'
})

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
    const [coursesRes, quizzesRes, attemptsRes] =
      await Promise.all([
        axios.get(
          'http://127.0.0.1:8000/api/courses/',
          authHeaders()
        ),
        axios.get(
          'http://127.0.0.1:8000/api/quizzes/',
          authHeaders()
        ),
        axios.get(
          'http://127.0.0.1:8000/api/quiz-attempts/',
          authHeaders()
        ),
      ])

    courses.value = coursesRes.data
    quizzes.value = quizzesRes.data
    attempts.value = attemptsRes.data
  } catch (error) {
    console.error(error)
    showToast('Failed to load quizzes')
  } finally {
    loading.value = false
  }
}

function blankForm() {
  return {
    course: '',
    title: '',
    description: '',
    passing_score: 70,
    time_limit_minutes: null,
    is_published: true,
  }
}

function typeLabel(type) {
  return {
    multiple_choice: 'MC',
    true_false: 'T/F',
    short_answer: 'SA',
  }[type] || type
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

function makeQuestion(type) {
  const base = {
    _uid: ++_uid,
    _open: true,
    text: '',
    question_type: type,
    points: 1,
    order_number: 1,
    options: [],
  }

  if (type === 'multiple_choice') {
    base.options = [
      { text: '', is_correct: true },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
    ]
  } else if (type === 'true_false') {
    base.options = [
      { text: 'True', is_correct: true },
      { text: 'False', is_correct: false },
    ]
  } else {
    base.options = [
      { text: '', is_correct: true },
    ]
  }

  return base
}

function openBuilder(quiz) {
  builder.quiz = {
    ...quiz,
  }

  builder.questions = (quiz.questions || []).map((question) => ({
    ...question,
    _uid: ++_uid,
    _open: false,
    options: question.options || [],
  }))

  builder.open = true
}

function addQuestion(type) {
  const question = makeQuestion(type)

  question.order_number = builder.questions.length + 1

  builder.questions.push(question)
}

function removeQuestion(index) {
  builder.questions.splice(index, 1)

  builder.questions.forEach((question, i) => {
    question.order_number = i + 1
  })
}

function moveQuestion(index, direction) {
  const target = index + direction

  if (
    target < 0 ||
    target >= builder.questions.length
  ) {
    return
  }

  const current = builder.questions[index]

  builder.questions[index] = builder.questions[target]
  builder.questions[target] = current

  builder.questions.forEach((question, i) => {
    question.order_number = i + 1
  })
}

function onTypeChange(question) {
  if (question.question_type === 'true_false') {
    question.options = [
      { text: 'True', is_correct: true },
      { text: 'False', is_correct: false },
    ]
  } else if (question.question_type === 'short_answer') {
    question.options = [
      { text: '', is_correct: true },
    ]
  } else {
    question.options = [
      { text: '', is_correct: true },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
    ]
  }
}

function setCorrect(question, correctIndex) {
  question.options.forEach((option, index) => {
    option.is_correct = index === correctIndex
  })
}

function addOption(question) {
  question.options.push({
    text: '',
    is_correct: false,
  })
}

function removeOption(question, optionIndex) {
  if (question.options.length <= 2) return

  question.options.splice(optionIndex, 1)

  if (!question.options.some((option) => option.is_correct)) {
    question.options[0].is_correct = true
  }
}

async function saveBuilder() {
  if (!builder.quiz) return

  const payload = {
    course: builder.quiz.course,
    lesson: builder.quiz.lesson || null,
    title: builder.quiz.title,
    description: builder.quiz.description || '',
    passing_score: builder.quiz.passing_score || 70,
    time_limit_minutes:
      builder.quiz.time_limit_minutes || null,
    is_published: builder.quiz.is_published,
    questions: builder.questions.map((question, index) => ({
      text: question.text,
      question_type: question.question_type,
      points: question.points || 1,
      order_number: index + 1,
      options: question.options.map((option) => ({
        text: option.text,
        is_correct: option.is_correct,
      })),
    })),
  }

  try {
    await axios.patch(
      `http://127.0.0.1:8000/api/quizzes/${builder.quiz.id}/`,
      payload,
      authHeaders()
    )

    builder.open = false
    await fetchData()
    showToast('Quiz saved ✅')
  } catch (error) {
    console.error(error)
    showToast('Failed to save quiz')
  }
}

function openCreate() {
  modal.form = blankForm()
  modal.errors = {}
  modal.editing = false
  modal._id = null
  modal.open = true
}

function openEdit(quiz) {
  modal.form = {
    course: quiz.course,
    title: quiz.title,
    description: quiz.description,
    passing_score: quiz.passing_score,
    time_limit_minutes: quiz.time_limit_minutes,
    is_published: quiz.is_published,
  }

  modal.errors = {}
  modal.editing = true
  modal._id = quiz.id
  modal.open = true
}

function validateModal() {
  const errors = {}

  if (!modal.form.course) {
    errors.course = 'Please select a course'
  }

  if (!modal.form.title.trim()) {
    errors.title = 'Title is required'
  }

  modal.errors = errors

  return !Object.keys(errors).length
}

async function saveQuiz() {
  if (!validateModal()) return

  const payload = {
    course: modal.form.course,
    title: modal.form.title,
    description: modal.form.description || '',
    passing_score: modal.form.passing_score || 70,
    time_limit_minutes:
      modal.form.time_limit_minutes || null,
    is_published: modal.form.is_published,
    questions: modal.editing
      ? undefined
      : [],
  }

  try {
    if (modal.editing) {

      await axios.patch(
        `http://127.0.0.1:8000/api/quizzes/${modal._id}/`,
        payload,
        authHeaders()
      )

      showToast('Quiz updated ✅')

    } else {

      const response = await axios.post(
        'http://127.0.0.1:8000/api/quizzes/',
        payload,
        authHeaders()
      )

      const course = courses.value.find(
        (c) => Number(c.id) === Number(modal.form.course)
      )

      if (course) {

        if (!course.lessons) {
          course.lessons = []
        }

        course.lessons.push({
          id: response.data.id,
          lesson_type: 'quiz',
          title: response.data.title,
          content: response.data.description || '',
          quiz: response.data,
        })
      }

      showToast('Quiz created ✅')

      openBuilder(response.data)
    }

    modal.open = false

    await fetchData()

  } catch (error) {
    console.error(error)
    showToast('Failed to save quiz')
  }
}

function confirmDelete(quiz) {
  deleteConfirm.target = quiz
  deleteConfirm.open = true
}

async function deleteQuiz() {
  if (!deleteConfirm.target) return

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/quizzes/${deleteConfirm.target.id}/`,
      authHeaders()
    )

    deleteConfirm.open = false
    await fetchData()
    showToast('Quiz deleted')
  } catch (error) {
    console.error(error)
    showToast('Failed to delete quiz')
  }
}

function showToast(message) {
  toast.message = message
  toast.visible = true

  setTimeout(() => {
    toast.visible = false
  }, 2600)
}

onMounted(() => {
  fetchData()
})
</script>

<style src="./src/assets/QuizzesView.css"></style>