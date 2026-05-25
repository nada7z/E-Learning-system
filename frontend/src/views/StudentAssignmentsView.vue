<template>
    <div class="page">
        <div class="page-header">
            <div>
                <h1 class="page-title">My Assignments</h1>
                <p class="page-sub">Submit your work for your enrolled courses</p>
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
                    <button class="btn btn-primary" @click="openSubmit(assignment)">
                        Submit assignment →
                    </button>
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
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const assignments = ref([])
const loading = ref(false)
const activeAssignment = ref(null)
const submitting = ref(false)
const toast = ref('')

const form = reactive({
    text_answer: '',
    file: null,
})

function authHeaders(extraHeaders = {}) {
    const token = localStorage.getItem('access_token')

    return {
        headers: {
            Authorization: `Bearer ${token}`,
            ...extraHeaders,
        },
    }
}

async function fetchAssignments() {
    loading.value = true

    try {
        const res = await axios.get(
            'http://127.0.0.1:8000/api/assignments/',
            authHeaders()
        )

        assignments.value = res.data
    } catch (error) {
        console.error(error)
        showToast('Failed to load assignments')
    } finally {
        loading.value = false
    }
}

function openSubmit(assignment) {
    activeAssignment.value = assignment
    form.text_answer = ''
    form.file = null
}

function handleFile(event) {
    form.file = event.target.files[0] || null
}

async function submitAssignment() {
    if (!activeAssignment.value) return

    if (!form.text_answer.trim() && !form.file) {
        showToast('Write an answer or upload a file')
        return
    }

    submitting.value = true

    const data = new FormData()
    data.append('assignment', activeAssignment.value.id)
    data.append('text_answer', form.text_answer)

    if (form.file) {
        data.append('file', form.file)
    }

    try {
        await axios.post(
            'http://127.0.0.1:8000/api/submissions/',
            data,
            authHeaders({
                'Content-Type': 'multipart/form-data',
            })
        )

        activeAssignment.value = null
        showToast('Assignment submitted ✅')
    } catch (error) {
        console.error(error)
        showToast('Failed to submit assignment')
    } finally {
        submitting.value = false
    }
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

onMounted(fetchAssignments)
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