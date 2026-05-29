<template>
    <div class="page">

        <div class="page-header">
            <div>
                <h1 class="page-title">My Quizzes</h1>
                <p class="page-sub">
                    View your quiz results and scores
                </p>
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
                    <div class="student-result-box">
                        <template v-if="getAttempts(quiz.id).length">
                            <p class="result-line">
                                <strong>Total attempts:</strong>
                                {{ getAttempts(quiz.id).length }}
                            </p>

                            <p class="result-line">
                                <strong>Best grade:</strong>
                                {{ Math.round(bestAttempt(quiz.id).score) }}%
                            </p>

                            <p class="result-line">
                                <strong>Latest grade:</strong>
                                {{ Math.round(latestAttempt(quiz.id).score) }}%
                            </p>

                            <button class="btn btn-outline" @click="openHistory(quiz)">
                                See attempt history
                            </button>
                        </template>

                        <template v-else>
                            <span class="status-badge status-warn">Not taken yet</span>

                            <p class="result-line">
                                Take this quiz from the course detail page.
                            </p>
                        </template>
                    </div>
                </div>

            </div>
        </div>

        <!-- ── Quiz modal ── -->
        <Transition name="modal">
            <div v-if="historyModal.open" class="modal-backdrop" @click.self="closeHistory">
                <div class="modal-card">
                    <div class="modal-header">
                        <div>
                            <h2 class="modal-title">
                                Attempt history
                            </h2>
                            <p class="modal-sub">
                                {{ historyModal.quiz?.title }}
                            </p>
                        </div>

                        <button class="modal-close" @click="closeHistory">
                            ×
                        </button>
                    </div>

                    <div class="modal-body">
                        <div v-for="(attempt, index) in getAttempts(historyModal.quiz.id)" :key="attempt.id"
                            class="history-attempt-row">
                            <div>
                                <strong>Attempt {{ index + 1 }}</strong>
                                <p>
                                    {{ new Date(attempt.submitted_at).toLocaleString() }}
                                </p>
                            </div>

                            <div class="history-score">
                                <span class="status-badge" :class="attempt.passed ? 'status-green' : 'status-red'">
                                    {{ attempt.passed ? 'Passed' : 'Failed' }}
                                </span>

                                <strong>{{ Math.round(attempt.score) }}%</strong>
                            </div>
                        </div>
                    </div>

                    <div class="modal-actions">
                        <button class="btn btn-outline" @click="closeHistory">
                            Close
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
const attempts = ref([])
const loading = ref(false)
const toast = ref('')
const historyModal = ref({
    open: false,
    quiz: null,
})

function authHeaders() {
    const token = localStorage.getItem('access_token')
    return { headers: { Authorization: `Bearer ${token}` } }
}

async function fetchQuizzes() {
    loading.value = true

    try {
        const [quizzesRes, attemptsRes] = await Promise.all([
            axios.get(
                'http://127.0.0.1:8000/api/quizzes/',
                authHeaders()
            ),
            axios.get(
                'http://127.0.0.1:8000/api/quiz-attempts/',
                authHeaders()
            ),
        ])

        quizzes.value = quizzesRes.data || []
        attempts.value = attemptsRes.data || []
    } catch (error) {
        console.error(error)
        showToast('Failed to load quizzes')
    } finally {
        loading.value = false
    }
}

function getAttempts(quizId) {
    if (!quizId) return []

    return attempts.value.filter((a) => {
        return (
            Number(a.quiz_id) === Number(quizId) ||
            Number(a.quiz) === Number(quizId)
        )
    })
}

function bestAttempt(quizId) {
    const list = getAttempts(quizId)
    if (!list.length) return null

    return [...list].sort((a, b) => Number(b.score) - Number(a.score))[0]
}

function latestAttempt(quizId) {
    const list = getAttempts(quizId)
    if (!list.length) return null

    return [...list].sort((a, b) => {
        return new Date(b.submitted_at) - new Date(a.submitted_at)
    })[0]
}

function openHistory(quiz) {
    historyModal.value = {
        open: true,
        quiz,
    }
}

function closeHistory() {
    historyModal.value = {
        open: false,
        quiz: null,
    }
}

function showToast(message) {
    toast.value = message
    setTimeout(() => { toast.value = '' }, 3000)
}

onMounted(fetchQuizzes)
</script>

<style src="./src/assets/StudentQuizzesView.css"></style>