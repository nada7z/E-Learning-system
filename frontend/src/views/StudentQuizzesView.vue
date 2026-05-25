<template>
    <div class="page">

        <div class="page-header">
            <div>
                <h1 class="page-title">My Quizzes</h1>
                <p class="page-sub">Test your knowledge across your enrolled courses</p>
            </div>
        </div>

        <div v-if="loading" class="page-sub" style="padding:60px 0;text-align:center">
            Loading quizzes…
        </div>

        <div v-else-if="!quizzes.length" class="empty-state">
            <div class="empty-icon">🎯</div>
            <p class="empty-title">No quizzes available</p>
            <p class="empty-sub">Quizzes will appear here once your teacher publishes them.</p>
        </div>

        <div v-else class="quiz-grid">
            <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card">

                <div class="quiz-card-hero">
                    <span class="quiz-hero-emoji">🎯</span>
                    <span class="quiz-hero-chip">{{ quiz.course_title }}</span>
                </div>

                <div class="quiz-card-body">
                    <h3 class="quiz-title">{{ quiz.title }}</h3>
                    <p v-if="quiz.description" class="quiz-desc">{{ quiz.description }}</p>
                    <div class="quiz-pills">
                        <span class="pill">📝 {{ quiz.questions_count }} questions</span>
                        <span class="pill">🏆 Pass {{ quiz.passing_score }}%</span>
                        <span v-if="quiz.time_limit_minutes" class="pill">⏱ {{ quiz.time_limit_minutes }} min</span>
                    </div>
                </div>

                <div class="quiz-card-footer">
                    <button class="btn btn-primary" @click="startQuiz(quiz)">
                        Start quiz →
                    </button>
                </div>

            </div>
        </div>

        <!-- ── Quiz modal ── -->
        <Transition name="modal">
            <div v-if="activeQuiz" class="modal-backdrop" @click.self="activeQuiz = null">
                <div class="modal">

                    <div class="modal-header">
                        <div>
                            <h2 class="modal-title">{{ activeQuiz.title }}</h2>
                            <p class="modal-sub">{{ activeQuiz.course_title }}</p>
                        </div>
                        <button class="close-btn" @click="activeQuiz = null">✕</button>
                    </div>

                    <div class="modal-body">
                        <div v-for="(question, qi) in activeQuiz.questions" :key="question.id" class="question-block">
                            <div class="question-meta">
                                <span class="q-index">Q{{ qi + 1 }}</span>
                                <span class="q-pts">{{ question.points ?? 1 }} pt</span>
                            </div>

                            <p class="q-text">{{ question.text }}</p>

                            <div v-if="question.question_type === 'multiple_choice' || question.question_type === 'true_false'"
                                class="options">
                                <label v-for="option in question.options" :key="option.id" class="option"
                                    :class="{ 'option--selected': answers[question.id]?.selected_option === option.id }">
                                    <input type="radio" :name="`q-${question.id}`" :value="option.id"
                                        v-model="answers[question.id].selected_option" />
                                    <span>{{ option.text }}</span>
                                </label>
                            </div>

                            <textarea v-else v-model="answers[question.id].text_answer" class="short-answer" rows="3"
                                placeholder="Write your answer here…"></textarea>
                        </div>
                    </div>

                    <div class="modal-footer">
                        <button class="btn btn-ghost" @click="activeQuiz = null">Cancel</button>
                        <button class="btn btn-primary" :disabled="submitting" @click="submitQuiz">
                            <span v-if="submitting" class="spinner"></span>
                            {{ submitting ? 'Submitting…' : 'Submit quiz' }}
                        </button>
                    </div>

                </div>
            </div>
        </Transition>

        <Transition name="toast">
            <div v-if="toast" class="toast">{{ toast }}</div>
        </Transition>

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const quizzes = ref([])
const loading = ref(false)
const activeQuiz = ref(null)
const answers = ref({})
const submitting = ref(false)
const toast = ref('')

function authHeaders() {
    const token = localStorage.getItem('access_token')
    return { headers: { Authorization: `Bearer ${token}` } }
}

async function fetchQuizzes() {
    loading.value = true
    try {
        const res = await axios.get('http://127.0.0.1:8000/api/quizzes/', authHeaders())
        quizzes.value = res.data
    } catch (error) {
        console.error(error)
        showToast('Failed to load quizzes')
    } finally {
        loading.value = false
    }
}

function startQuiz(quiz) {
    activeQuiz.value = quiz
    answers.value = {}
    quiz.questions.forEach(q => {
        answers.value[q.id] = { question: q.id, selected_option: null, text_answer: '' }
    })
}

async function submitQuiz() {
    if (!activeQuiz.value) return
    submitting.value = true

    const payload = {
        quiz: activeQuiz.value.id,
        answers: Object.values(answers.value).map(a => ({
            question: a.question,
            selected_option: a.selected_option || null,
            text_answer: a.text_answer || '',
        })),
    }

    try {
        const res = await axios.post(
            'http://127.0.0.1:8000/api/quiz-attempts/',
            payload,
            authHeaders()
        )
        activeQuiz.value = null
        showToast(`Quiz submitted. Score: ${Number(res.data.score).toFixed(1)}%`)
    } catch (error) {
        console.error(error)
        showToast('Failed to submit quiz')
    } finally {
        submitting.value = false
    }
}

function showToast(message) {
    toast.value = message
    setTimeout(() => { toast.value = '' }, 3000)
}

onMounted(fetchQuizzes)
</script>

<style src="./src/assets/StudentQuizzesView.css"></style>