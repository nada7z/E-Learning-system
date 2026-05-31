<template>
    <div class="course-detail-page">
        <div v-if="loading" class="state-box">
            Loading course...
        </div>

        <div v-else-if="error" class="state-box error">
            {{ error }}
        </div>

        <div v-else-if="course" class="course-layout">
            <main class="course-main">
                <button class="back-btn" @click="$emit('navigate', 'courses')">
                    ← Back to courses
                </button>

                <div class="course-header">
                    <p class="breadcrumb">Courses / {{ course.category }}</p>

                    <h1>{{ course.title }}</h1>

                    <p class="description">
                        {{ course.description }}
                    </p>

                    <div class="course-meta">
                        <span>{{ course.level }}</span>
                        <span>{{ course.language }}</span>
                        <span>{{ course.duration_hours }} hours</span>
                        <span>{{ courseItems.length }} items</span>
                    </div>

                    <div v-if="isStudent" class="course-progress-box">
                        <div class="course-progress-top">
                            <span>Course progress</span>
                            <strong>{{ courseProgress }}%</strong>
                        </div>

                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: courseProgress + '%' }"></div>
                        </div>
                    </div>
                </div>

                <div v-if="
                    selectedLesson?.lesson_type === 'video' &&
                    (
                        selectedLesson?.video_file_url ||
                        selectedLesson?.video_file ||
                        selectedLesson?.video_url
                    )
                " class="video-card">
                    <video v-if="selectedLesson.video_file_url || selectedLesson.video_file" class="lesson-video"
                        controls :src="selectedLesson.video_file_url || selectedLesson.video_file"></video>

                    <iframe v-else-if="selectedLesson.video_url" class="lesson-video"
                        :src="formatVideoUrl(selectedLesson.video_url)" allowfullscreen></iframe>
                </div>

                <div class="lesson-content-card">
                    <div class="tabs">
                        <button v-for="(tab, index) in tabs" :key="tab" class="tab-btn"
                            :class="{ active: activeTab === index }" @click="activeTab = index">
                            {{ tab }}
                        </button>
                    </div>

                    <section v-if="activeTab === 0">
                        <div class="lesson-title-line">
                            <h2>{{ selectedLesson?.title || course.title }}</h2>

                            <button v-if="
                                isStudent &&
                                selectedLesson &&
                                selectedLesson.lesson_type !== 'quiz' &&
                                selectedLesson.lesson_type !== 'assignment'
                            " class="lesson-complete-btn big" :class="{ completed: isCompleted(selectedLesson) }"
                                @click="markCompleted(selectedLesson)">
                                <CheckIcon :size="20" />
                            </button>
                        </div>

                        <p class="lesson-text">
                            {{ selectedLesson?.content || selectedLesson?.description || 'No content yet.' }}
                        </p>

                        <button v-if="
                            isStudent &&
                            selectedLesson &&
                            selectedLesson.lesson_type !== 'quiz' &&
                            selectedLesson.lesson_type !== 'assignment'
                        " class="primary-action" :disabled="isCompleted(selectedLesson)"
                            @click="markCompleted(selectedLesson)">
                            {{ isCompleted(selectedLesson) ? 'Completed' : 'Mark as completed' }}
                        </button>

                        <div v-if="selectedLesson?.lesson_type === 'assignment'" class="activity-box">
                            <h3>Submit assignment</h3>

                            <p>
                                {{ selectedLesson.assignment?.description || selectedLesson.content }}
                            </p>

                            <p v-if="selectedLesson.assignment?.deadline">
                                <strong>Deadline:</strong>
                                {{ formatDate(selectedLesson.assignment.deadline) }}
                            </p>

                            <p>
                                <strong>Max score:</strong>
                                {{ selectedLesson.assignment?.max_score || 100 }}
                            </p>

                            <textarea v-model="assignmentForm.text_answer" class="answer-box"
                                placeholder="Write your answer..."></textarea>

                            <input class="file-input" type="file" @change="handleAssignmentFile" />

                            <button class="primary-action" :disabled="submitting || isCompleted(selectedLesson)"
                                @click="submitAssignment">
                                {{ isCompleted(selectedLesson) ? 'Submitted' : submitting ?
                                    'Submitting...' : 'Submit assignment' }}
                            </button>
                        </div>

                        <div v-if="selectedLesson?.lesson_type === 'quiz'" class="activity-box">
                            <h3>Answer quiz</h3>

                            <p>
                                {{ selectedLesson.quiz?.description || selectedLesson.content }}
                            </p>

                            <p>
                                <strong>Passing score:</strong>
                                {{ selectedLesson.quiz?.passing_score || 50 }}%
                            </p>

                            <div v-for="(question, qIndex) in selectedLesson.quiz?.questions || []" :key="question.id"
                                class="question-card">
                                <h3>Question {{ qIndex + 1 }}</h3>
                                <p>{{ question.text }}</p>

                                <textarea v-if="question.question_type === 'short_answer'"
                                    v-model="quizAnswers[question.id].text_answer" class="answer-box"
                                    placeholder="Write your answer..."></textarea>

                                <label v-else v-for="option in question.options || []" :key="option.id" class="option"
                                    :class="{
                                        selected: quizAnswers[question.id]?.selected_option === option.id
                                    }">
                                    <input type="radio" :name="`question-${question.id}`" :value="option.id"
                                        v-model="quizAnswers[question.id].selected_option" />
                                    {{ option.text }}
                                </label>
                            </div>

                            <button class="primary-action" :disabled="submitting || isCompleted(selectedLesson)"
                                @click="submitQuiz">
                                {{ isCompleted(selectedLesson) ? 'Quiz submitted' : submitting ? 'Submitting...' :
                                    'Submit quiz' }}
                            </button>
                        </div>
                    </section>

                    <section v-if="activeTab === 1">
                        <h2>Resources</h2>
                        <p class="lesson-text">Resources are not added yet.</p>
                    </section>

                    <section v-if="activeTab === 2">
                        <div class="discussion-card">
                            <h2>Course discussion</h2>
                            <p class="lesson-text">
                                Ask questions, discuss lessons, and get answers from the teacher.
                            </p>

                            <div class="discussion-form">
                                <textarea v-model="discussionText" class="discussion-input"
                                    placeholder="Write your message..." rows="3"></textarea>

                                <button class="primary-action" :disabled="discussionLoading || !discussionText.trim()"
                                    @click="submitDiscussion">
                                    {{ discussionLoading ? 'Posting...' : 'Post message' }}
                                </button>
                            </div>

                            <div v-if="discussionMessages.length" class="discussion-list">
                                <div v-for="message in discussionMessages" :key="message.id" class="discussion-message">
                                    <div class="discussion-header">
                                        <strong>{{ message.author_name }}</strong>

                                        <span v-if="message.is_teacher" class="teacher-badge">
                                            Teacher
                                        </span>
                                    </div>

                                    <p>{{ message.message }}</p>

                                    <small>
                                        {{ new Date(message.created_at).toLocaleString() }}
                                    </small>
                                </div>
                            </div>

                            <p v-else class="lesson-text">
                                No messages yet. Start the discussion.
                            </p>
                        </div>
                    </section>

                    <section v-if="activeTab === 3">
                        <div class="review-card">
                            <h2>Course reviews</h2>

                            <div v-if="canReviewCourse" class="review-form">
                                <h3>
                                    {{ myReview ? 'Update your review' : 'Leave a review' }}
                                </h3>

                                <div class="stars">
                                    <button v-for="star in 5" :key="star" type="button"
                                        :class="{ active: star <= reviewForm.rating }"
                                        @click="reviewForm.rating = star">
                                        ★
                                    </button>
                                </div>

                                <textarea v-model="reviewForm.review" class="answer-box"
                                    placeholder="Write your review..."></textarea>

                                <button class="primary-action" @click="submitReview">
                                    {{ myReview ? 'Update review' : 'Submit review' }}
                                </button>
                            </div>

                            <p v-else-if="isStudent" class="lesson-text">
                                Complete and pass this course to leave a review.
                            </p>

                            <div v-if="reviews.length" class="reviews-list">
                                <div v-for="review in reviews" :key="review.id" class="single-review">
                                    <strong>{{ review.student_name }}</strong>

                                    <span>
                                        {{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}
                                    </span>

                                    <p>{{ review.review }}</p>
                                </div>
                            </div>

                            <p v-else class="lesson-text">
                                No reviews yet.
                            </p>
                        </div>
                    </section>
                </div>
            </main>

            <aside class="course-sidebar">
                <div class="sidebar-card">
                    <h3>Course content</h3>

                    <p class="small-muted">
                        {{ courseItems.length }} items
                    </p>

                    <div class="lesson-list">
                        <div v-for="(lesson, index) in courseItems" :key="lesson.uid" class="lesson-row" :class="{
                            active: selectedLesson?.uid === lesson.uid,
                            completed: isCompleted(lesson)
                        }" @click="selectLesson(lesson)">
                            <button v-if="isStudent" class="lesson-complete-btn"
                                :class="{ completed: isCompleted(lesson) }" @click.stop="markCompleted(lesson)">
                                <CheckIcon :size="20" />
                            </button>

                            <div v-else class="lesson-number">
                                {{ index + 1 }}
                            </div>

                            <div class="lesson-info">
                                <strong>{{ lesson.title }}</strong>
                                <span>
                                    {{ lessonTypeIcon(lesson.lesson_type) }}
                                    {{ lessonTypeLabel(lesson.lesson_type) }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="sidebar-card">
                    <h3>Course info</h3>

                    <p>
                        <strong>Teacher:</strong>
                        {{ course.teacher_name || 'Teacher' }}
                    </p>

                    <p>
                        <strong>Category:</strong>
                        {{ course.category }}
                    </p>

                    <p>
                        <strong>Certificate:</strong>
                        {{ course.has_certificate ? 'Yes' : 'No' }}
                    </p>

                    <p>
                        <strong>Price:</strong>
                        {{ course.is_free ? 'Free' : course.price }}
                    </p>
                </div>
            </aside>

            <div v-if="toast" class="toast">
                {{ toast }}
            </div>
        </div>
    </div>

    <Transition name="modal">
        <div v-if="showCompletionModal" class="completion-backdrop">
            <div class="completion-modal">
                <div class="completion-icon">
                    🎉
                </div>

                <h1>Course Completed!</h1>

                <p>
                    Congratulations! You successfully completed this course
                    and earned your certificate.
                </p>

                <div class="completion-actions">
                    <button class="secondary-btn" @click="showCompletionModal = false">
                        Stay here
                    </button>

                    <button class="primary-btn" @click="$router.push({ name: 'Certificates' })">
                        View Certificate
                    </button>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import {
    CheckIcon,
} from 'lucide-vue-next'

const route = useRoute()

defineEmits(['navigate', 'toast'])

const course = ref(null)
const quizzes = ref([])
const assignments = ref([])
const selectedLesson = ref(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref(0)
const submitting = ref(false)
const toast = ref('')
const showCompletionModal = ref(false)

const completedItems = ref([])
const quizAnswers = ref({})
const reviews = ref([])
const myReview = ref(null)

const discussionMessages = ref([])
const discussionText = ref('')
const discussionLoading = ref(false)

const reviewForm = reactive({
    rating: 5,
    review: '',
})

const canReviewCourse = computed(() => {
    return isStudent.value && courseProgress.value >= 100
})

const assignmentForm = reactive({
    text_answer: '',
    file: null,
})

const tabs = ['Overview', 'Resources', 'Discussions', 'Reviews']

const user = computed(() => {
    try {
        return JSON.parse(localStorage.getItem('user') || '{}')
    } catch {
        return {}
    }
})

const isStudent = computed(() => {
    return user.value?.role === 'student'
})

const courseItems = computed(() => {
    const lessons = (course.value?.lessons || []).map((lesson) => ({
        ...lesson,
        uid: `lesson-${lesson.id}`,
    }))

    const quizItems = quizzes.value.map((quiz) => ({
        uid: `quiz-${quiz.id}`,
        id: quiz.id,
        title: quiz.title,
        content: quiz.description || '',
        lesson_type: 'quiz',
        quiz,
    }))

    const assignmentItems = assignments.value.map((assignment) => ({
        uid: `assignment-${assignment.id}`,
        id: assignment.id,
        title: assignment.title,
        content: assignment.description || '',
        lesson_type: 'assignment',
        assignment,
    }))

    return [...lessons, ...quizItems, ...assignmentItems]
})

const courseProgress = computed(() => {
    if (!courseItems.value.length) return 0

    return Math.round(
        (completedItems.value.length / courseItems.value.length) * 100
    )
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

function progressKey() {
    return `course-progress-${route.params.id}`
}

function lessonTypeLabel(type) {
    const labels = {
        video: 'Video lesson',
        text: 'Text lesson',
        document: 'Document',
        quiz: 'Quiz',
        assignment: 'Assignment',
        exam: 'Final exam',
        final_exam: 'Final exam',
    }

    return labels[type] || 'Lesson'
}

function loadProgress() {
    const saved = localStorage.getItem(progressKey())
    completedItems.value = saved ? JSON.parse(saved) : []
}

function saveProgress() {
    localStorage.setItem(
        progressKey(),
        JSON.stringify(completedItems.value)
    )
}

function isCompleted(item) {
    return completedItems.value.includes(item?.uid)
}

async function markCompleted(item) {
    if (!item?.uid) return

    if (!completedItems.value.includes(item.uid)) {
        completedItems.value.push(item.uid)
        saveProgress()
    }

    const progress = courseProgress.value || 0

    console.log('COURSE PROGRESS:', progress)

    if (progress >= 100) {
        await generateCertificate()
        showCompletionModal.value = true
        showToast('🎉 Congratulations! Certificate unlocked.')
        return
    }

    showToast('Marked as completed ✅')
}

function selectLesson(lesson) {
    selectedLesson.value = lesson
    activeTab.value = 0

    if (lesson.lesson_type === 'quiz') {
        initQuizAnswers(lesson.quiz)
    }

    if (lesson.lesson_type === 'assignment') {
        assignmentForm.text_answer = ''
        assignmentForm.file = null
    }
}

async function fetchCourse() {
    loading.value = true
    error.value = ''

    try {
        const [courseRes, quizzesRes, assignmentsRes] = await Promise.all([
            axios.get(
                `http://127.0.0.1:8000/api/courses/${route.params.id}/`,
                authHeaders()
            ),
            axios.get(
                'http://127.0.0.1:8000/api/quizzes/',
                authHeaders()
            ),
            axios.get(
                'http://127.0.0.1:8000/api/assignments/',
                authHeaders()
            ),
        ])

        course.value = courseRes.data

        quizzes.value = (quizzesRes.data || []).filter(
            (quiz) => Number(quiz.course) === Number(route.params.id)
        )

        assignments.value = (assignmentsRes.data || []).filter(
            (assignment) => Number(assignment.course) === Number(route.params.id)
        )

        loadProgress()

        selectedLesson.value = courseItems.value.length
            ? courseItems.value[0]
            : null

        if (selectedLesson.value?.lesson_type === 'quiz') {
            initQuizAnswers(selectedLesson.value.quiz)
        }
    } catch (err) {
        console.error(err)
        error.value = 'Failed to load course.'
    } finally {
        loading.value = false
    }
}

async function fetchReviews() {
    try {
        const res = await axios.get(
            `http://127.0.0.1:8000/api/courses/${route.params.id}/reviews/`,
            authHeaders()
        )

        reviews.value = res.data.reviews || []
        myReview.value = res.data.my_review

        if (myReview.value) {
            reviewForm.rating = myReview.value.rating
            reviewForm.review = myReview.value.review || ''
        }
    } catch (err) {
        console.error(err)
    }
}

async function submitReview() {
    if (!canReviewCourse.value) {
        showToast('Complete and pass the course first.')
        return
    }

    try {
        const res = await axios.post(
            `http://127.0.0.1:8000/api/courses/${route.params.id}/reviews/`,
            {
                rating: reviewForm.rating,
                review: reviewForm.review,
            },
            authHeaders()
        )

        myReview.value = res.data
        await fetchReviews()
        showToast('Review saved ⭐')
    } catch (err) {
        console.error(err)
        showToast(err.response?.data?.detail || 'Failed to submit review')
    }
}

async function fetchDiscussions() {
    try {
        const res = await axios.get(
            `http://127.0.0.1:8000/api/courses/${route.params.id}/discussions/`,
            authHeaders()
        )

        discussionMessages.value = res.data || []
    } catch (err) {
        console.error(err)
    }
}

async function submitDiscussion() {
    if (!discussionText.value.trim()) return

    discussionLoading.value = true

    try {
        const res = await axios.post(
            `http://127.0.0.1:8000/api/courses/${route.params.id}/discussions/`,
            {
                message: discussionText.value,
            },
            authHeaders()
        )

        discussionMessages.value.push(res.data)
        discussionText.value = ''
    } catch (err) {
        console.error(err)
        toast.value = 'Could not post message.'
    } finally {
        discussionLoading.value = false
    }
}

function initQuizAnswers(quiz) {
    quizAnswers.value = {}

        ; (quiz?.questions || []).forEach((question) => {
            quizAnswers.value[question.id] = {
                question: question.id,
                selected_option: null,
                text_answer: '',
            }
        })
}

async function submitQuiz() {
    if (!selectedLesson.value?.quiz) return

    const quiz = selectedLesson.value.quiz

    if (!Object.keys(quizAnswers.value).length) {
        initQuizAnswers(quiz)
    }

    const payload = {
        quiz: quiz.id,
        answers: Object.values(quizAnswers.value).map((answer) => ({
            question: answer.question,
            selected_option: answer.selected_option || null,
            text_answer: answer.text_answer || '',
        })),
    }

    submitting.value = true

    try {
        const res = await axios.post(
            'http://127.0.0.1:8000/api/quiz-attempts/',
            payload,
            authHeaders()
        )

        const score = Number(res.data.score || 0)
        const passingScore = Number(quiz.passing_score || 50)

        if (score >= passingScore) {
            await markCompleted(selectedLesson.value)
            showToast(`Quiz passed ✅ Score: ${score.toFixed(1)}%`)
        } else {
            showToast(`Quiz failed ❌ Score: ${score.toFixed(1)}%`)
        }
    } catch (err) {
        console.error(err)
        showToast('Failed to submit quiz')
    } finally {
        submitting.value = false
    }
}

function handleAssignmentFile(event) {
    assignmentForm.file = event.target.files[0] || null
}

async function submitAssignment() {
    if (!selectedLesson.value?.assignment) return

    if (!assignmentForm.text_answer.trim() && !assignmentForm.file) {
        showToast('Write an answer or upload a file')
        return
    }

    const data = new FormData()
    data.append('assignment', selectedLesson.value.assignment.id)
    data.append('text_answer', assignmentForm.text_answer)

    if (assignmentForm.file) {
        data.append('file', assignmentForm.file)
    }

    submitting.value = true

    try {
        await axios.post(
            'http://127.0.0.1:8000/api/submissions/',
            data,
            authHeaders({
                'Content-Type': 'multipart/form-data',
            })
        )

        await markCompleted(selectedLesson.value)

        assignmentForm.text_answer = ''
        assignmentForm.file = null

        showToast('Assignment submitted')
    } catch (err) {
        console.error(err)
        showToast('Failed to submit assignment')
    } finally {
        submitting.value = false
    }
}

function lessonTypeIcon(type) {
    const icons = {
        video: '▶',
        reading: '📖',
        quiz: '📝',
        assignment: '📋',
    }

    return icons[type] || '📘'
}

function formatDate(value) {
    if (!value) return ''
    return new Date(value).toLocaleString()
}

function formatVideoUrl(url) {
    if (!url) return ''

    if (url.includes('youtube.com/watch?v=')) {
        const videoId = url.split('v=')[1]?.split('&')[0]
        return `https://www.youtube.com/embed/${videoId}`
    }

    if (url.includes('youtu.be/')) {
        const videoId = url.split('youtu.be/')[1]?.split('?')[0]
        return `https://www.youtube.com/embed/${videoId}`
    }

    return url
}

function showToast(message) {
    toast.value = message

    setTimeout(() => {
        toast.value = ''
    }, 2600)
}

function canEarnCertificate() {
    return courseItems.value.every((item) => {
        if (item.lesson_type === 'quiz') {
            return completedItems.value.includes(item.uid)
        }

        if (item.lesson_type === 'assignment') {
            return completedItems.value.includes(item.uid)
        }

        return completedItems.value.includes(item.uid)
    })
}

async function generateCertificate() {
    try {
        await axios.post(
            'http://127.0.0.1:8000/api/certificates/generate/',
            {
                course_id: course.value.id,
            },
            authHeaders()
        )
    } catch (err) {
        console.error(err)
        showToast('Course completed, but certificate was not generated.')
    }
}

async function checkCertificateOnLoad() {
    if (courseProgress.value >= 100) {
        console.log('COURSE ALREADY 100%, GENERATING CERTIFICATE...')
        await generateCertificate()
    }
}

onMounted(async () => {
    await fetchCourse()
    await fetchReviews()
    await fetchDiscussions()
    await checkCertificateOnLoad()
})
</script>

<style scoped>
.course-detail-page {
    padding: 28px;
    background: #f7f6f2;
    min-height: 100vh;
}

.state-box {
    background: white;
    border-radius: 16px;
    padding: 24px;
    font-weight: 600;
}

.state-box.error {
    color: #dc2626;
}

.course-layout {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 24px;
}

.course-main {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.back-btn {
    width: fit-content;
    border: none;
    background: transparent;
    font-weight: 600;
    cursor: pointer;
}

.course-header {
    background: white;
    padding: 28px;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
}

.breadcrumb {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 10px;
}

.course-header h1 {
    font-size: 34px;
    margin: 0 0 12px;
}

.description {
    color: #4b5563;
    line-height: 1.6;
    max-width: 850px;
}

.course-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 18px;
}

.course-meta span {
    background: #eef2ff;
    color: #4338ca;
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
}

.course-progress-box {
    margin-top: 22px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 16px;
}

.course-progress-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 14px;
    color: #4b5563;
}

.course-progress-top strong {
    color: #111827;
}

.progress-bar {
    height: 9px;
    background: #e5e7eb;
    border-radius: 999px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #4f46e5;
    border-radius: 999px;
    transition: width 0.3s ease;
}

.video-card {
    background: #111827;
    border-radius: 20px;
    min-height: 360px;
    overflow: hidden;
    display: flex;
}

.lesson-video {
    width: 100%;
    height: 360px;
    border: none;
    object-fit: cover;
}

.lesson-content-card {
    background: white;
    padding: 24px;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
}

.tabs {
    display: flex;
    gap: 10px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 22px;
    padding-bottom: 12px;
}

.tab-btn {
    border: none;
    background: transparent;
    padding: 9px 12px;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
}

.tab-btn.active {
    background: #eef2ff;
    color: #4f46e5;
}

.lesson-title-line {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.lesson-content-card h2 {
    margin: 0 0 14px;
}

.lesson-text {
    color: #4b5563;
    line-height: 1.8;
    white-space: pre-line;
}

.activity-box,
.question-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px;
    margin-top: 18px;
}

.option {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    margin-top: 8px;
    cursor: pointer;
}

.option.selected {
    border-color: #4f46e5;
    background: #eef2ff;
    color: #4338ca;
    font-weight: 700;
}

.answer-box {
    width: 100%;
    min-height: 120px;
    margin-top: 12px;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #d1d5db;
    resize: vertical;
    font-family: inherit;
}

.file-input {
    display: block;
    margin-top: 12px;
    padding: 10px;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 12px;
}

.primary-action {
    margin-top: 16px;
    border: none;
    background: #4f46e5;
    color: white;
    padding: 11px 18px;
    border-radius: 12px;
    font-weight: 700;
    cursor: pointer;
}

.primary-action:disabled {
    opacity: 0.55;
    cursor: not-allowed;
}

.course-sidebar {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.sidebar-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 20px;
}

.sidebar-card h3 {
    margin-top: 0;
}

.small-muted {
    color: #6b7280;
    font-size: 13px;
}

.lesson-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.lesson-row {
    width: 100%;
    border: 1px solid #e5e7eb;
    background: white;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 14px;
    text-align: left;
    cursor: pointer;
}

.lesson-row.active {
    border-color: #4f46e5;
    background: #eef2ff;
}

.lesson-row.completed {
    border-color: #10b981;
}

.lesson-number,
.lesson-complete-btn {
    width: 32px;
    height: 32px;
    min-width: 32px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-weight: 800;
}

.lesson-number {
    background: #e5e7eb;
    color: #111827;
}

.lesson-complete-btn {
    border: 2px solid #4f46e5;
    background: white;
    color: #4f46e5;
    cursor: pointer;
    transition: all 0.2s ease;
}

.lesson-complete-btn:hover {
    transform: scale(1.06);
}

.lesson-complete-btn.completed {
    background: #10b981;
    border-color: #10b981;
    color: white;
}

.lesson-complete-btn.big {
    width: 38px;
    height: 38px;
    min-width: 38px;
}

.lesson-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.lesson-info span {
    color: #6b7280;
    font-size: 12px;
}

.toast {
    position: fixed;
    right: 24px;
    bottom: 24px;
    background: #111827;
    color: white;
    padding: 12px 18px;
    border-radius: 14px;
    font-weight: 600;
    z-index: 100;
}

@media (max-width: 1000px) {
    .course-layout {
        grid-template-columns: 1fr;
    }
}

.completion-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    backdrop-filter: blur(6px);
}

.completion-modal {
    width: min(520px, 92vw);
    background: white;
    border-radius: 28px;
    padding: 42px;
    text-align: center;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
}

.completion-icon {
    width: 92px;
    height: 92px;
    margin: 0 auto 20px;
    border-radius: 50%;
    background: linear-gradient(135deg,
            #4f46e5,
            #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 42px;
    color: white;
}

.completion-modal h1 {
    margin: 0 0 12px;
    font-size: 34px;
}

.completion-modal p {
    color: #6b7280;
    line-height: 1.7;
    margin-bottom: 30px;
}

.completion-actions {
    display: flex;
    justify-content: center;
    gap: 14px;
}

.primary-btn,
.secondary-btn {
    border: none;
    border-radius: 14px;
    padding: 13px 22px;
    font-weight: 700;
    cursor: pointer;
}

.primary-btn {
    background: #4f46e5;
    color: white;
}

.secondary-btn {
    background: #eef2ff;
    color: #4338ca;
}

.modal-enter-active,
.modal-leave-active {
    transition: 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
    transform: scale(0.96);
}

.review-card {
    background: white;
    padding: 24px;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
}

.review-form {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 18px;
}

.stars {
    display: flex;
    gap: 6px;
    margin: 12px 0;
}

.stars button {
    border: none;
    background: transparent;
    font-size: 30px;
    color: #d1d5db;
    cursor: pointer;
}

.stars button.active {
    color: #f59e0b;
}

.reviews-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.single-review {
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px;
    background: #f9fafb;
}

.single-review span {
    display: block;
    color: #f59e0b;
    margin: 6px 0;
}

.discussion-card {
    background: white;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.discussion-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 18px 0;
}

.discussion-input {
    width: 100%;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px;
    resize: vertical;
    font-family: inherit;
}

.discussion-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.discussion-message {
    border: 1px solid #eef2ff;
    background: #f8fafc;
    border-radius: 14px;
    padding: 14px;
}

.discussion-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}

.teacher-badge {
    background: #3d5afe;
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 999px;
}

.discussion-message p {
    margin: 0 0 8px;
    color: #334155;
}

.discussion-message small {
    color: #64748b;
}
</style>