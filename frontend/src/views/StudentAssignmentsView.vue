<template>
    <div class="page">
        <div class="page-header">
            <div>
                <h1 class="page-title">My Assignments</h1>
                <p class="page-sub">View your assignment submissions, grades, and feedback</p>
            </div>
        </div>

        <div v-if="loading" class="page-sub" style="padding:60px 0;text-align:center">
            Loading assignments…
        </div>

        <div v-else-if="!assignments.length" class="empty-state">
            <div class="empty-icon">📚</div>
            <p class="empty-title">No assignments available</p>
            <p class="empty-sub">Assignments will appear here once your teacher creates them.</p>
        </div>

        <div v-else class="quiz-grid">
            <div v-for="assignment in assignments" :key="assignment.id" class="quiz-card">
                <div class="quiz-card-hero">
                    <span class="quiz-hero-emoji">📚</span>
                    <span class="quiz-hero-chip">{{ assignment.course_title }}</span>
                </div>

                <div class="quiz-card-body">
                    <h3 class="quiz-title">{{ assignment.title }}</h3>

                    <p v-if="assignment.description" class="quiz-desc">
                        {{ assignment.description }}
                    </p>

                    <div class="quiz-pills">
                        <span class="pill">🏆 Max {{ assignment.max_score }}</span>
                        <span class="pill">📅 {{ formatDate(assignment.deadline) }}</span>
                    </div>
                </div>

                <div class="quiz-card-footer">
                    <div class="student-result-box">
                        <template v-if="getSubmission(assignment.id)">
                            <span class="status-badge status-green">✓ Submitted</span>

                            <p class="result-line">
                                <strong>Grade:</strong>
                                {{ getSubmission(assignment.id).grade ?? 'Not graded yet' }}
                                <span v-if="getSubmission(assignment.id).grade != null">
                                    / {{ assignment.max_score }}
                                </span>
                            </p>

                            <p class="result-line">
                                <strong>Feedback:</strong>
                                {{ getSubmission(assignment.id).feedback || 'No feedback yet' }}
                            </p>
                        </template>

                        <template v-else>
                            <span class="status-badge status-warn">Not submitted yet</span>
                            <p class="result-line text-muted">
                                Submit this assignment from the course detail page.
                            </p>
                        </template>
                    </div>
                </div>
            </div>
        </div>

        <Transition name="modal">
            <div v-if="activeAssignment" class="modal-backdrop" @click.self="activeAssignment = null">
                <div class="modal">
                    <div class="modal-header">
                        <div>
                            <h2 class="modal-title">{{ activeAssignment.title }}</h2>
                            <p class="modal-sub">{{ activeAssignment.course_title }}</p>
                        </div>

                        <button class="close-btn" @click="activeAssignment = null">
                            ✕
                        </button>
                    </div>

                    <div class="modal-body">
                        <div class="question-block">
                            <div class="question-meta">
                                <span class="q-index">📚</span>
                                <span class="q-pts">{{ activeAssignment.max_score }} pts</span>
                            </div>

                            <p class="q-text">{{ activeAssignment.description }}</p>

                            <textarea v-model="form.text_answer" class="short-answer" rows="6"
                                placeholder="Write your answer here…"></textarea>

                            <input class="file-input" type="file" @change="handleFile" />
                        </div>
                    </div>

                    <div class="modal-footer">
                        <button class="btn btn-ghost" @click="activeAssignment = null">
                            Cancel
                        </button>

                        <button class="btn btn-primary" :disabled="submitting" @click="submitAssignment">
                            <span v-if="submitting" class="spinner"></span>
                            {{ submitting ? 'Submitting…' : 'Submit assignment' }}
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

const assignments = ref([])
const submissions = ref([])
const loading = ref(false)
const toast = ref('')

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
        const [assignmentsRes, submissionsRes] = await Promise.all([
            axios.get(
                'http://127.0.0.1:8000/api/assignments/',
                authHeaders()
            ),
            axios.get(
                'http://127.0.0.1:8000/api/submissions/',
                authHeaders()
            ),
        ])

        assignments.value = assignmentsRes.data || []
        submissions.value = submissionsRes.data || []
    } catch (error) {
        console.error(error)
        showToast('Failed to load assignments')
    } finally {
        loading.value = false
    }
}

function getSubmission(assignmentId) {
    return submissions.value.find((s) => {
        return (
            Number(s.assignment_id) === Number(assignmentId) ||
            Number(s.assignment) === Number(assignmentId)
        )
    }) || null
}

function formatDate(date) {
    if (!date) return 'No deadline'

    return new Date(date).toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    })
}

function showToast(message) {
    toast.value = message

    setTimeout(() => {
        toast.value = ''
    }, 3000)
}

onMounted(fetchData)
</script>

<style src="./src/assets/StudentQuizzesView.css"></style>

<style scoped>
.file-input {
    background: #ffffff;
    border: 1px solid #e5e2da;
    border-radius: 10px;
    padding: 10px 13px;
    font-family: inherit;
    font-size: 14px;
    color: #6b6860;
}
</style>