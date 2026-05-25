<template>
    <div class="learn-page">

        <!-- Top bar -->
        <div class="learn-topbar">
            <button class="btn btn-ghost btn-sm" @click="goBack">
                ← Back to courses
            </button>

            <div class="topbar-center">
                <span class="topbar-title">
                    {{ course?.title || 'Loading course...' }}
                </span>
            </div>

            <div class="topbar-right">
                <div class="progress-pill">
                    <div class="progress-bar-sm">
                        <div class="progress-fill-sm" :style="{ width: overallProgress + '%' }"></div>
                    </div>

                    <span class="progress-text">
                        {{ overallProgress }}% complete
                    </span>
                </div>

                <button class="icon-btn" title="Settings" @click="showToast('Settings coming soon')">
                    ⚙️
                </button>
            </div>
        </div>

        <!-- Main layout -->
        <div class="learn-layout">

            <!-- Sidebar -->
            <aside class="lesson-sidebar" :class="{ collapsed: sidebarCollapsed }">
                <div class="sidebar-header">
                    <span v-if="!sidebarCollapsed" class="sidebar-title">
                        Course content
                    </span>

                    <button class="icon-btn collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed"
                        :title="sidebarCollapsed ? 'Expand' : 'Collapse'">
                        {{ sidebarCollapsed ? '▶' : '◀' }}
                    </button>
                </div>

                <div v-if="!sidebarCollapsed" class="lesson-list">
                    <div v-for="(lesson, i) in (course?.lessons || [])" :key="lesson.id" class="lesson-item" :class="{
                        active: activeLesson?.id === lesson.id,
                        done: lesson.completed
                    }" @click="selectLesson(lesson)">
                        <div class="lesson-num" :class="{
                            done: lesson.completed,
                            active: activeLesson?.id === lesson.id
                        }">
                            <span v-if="lesson.completed">✓</span>
                            <span v-else>{{ i + 1 }}</span>
                        </div>

                        <div class="lesson-info">
                            <span class="lesson-title-text">
                                {{ lesson.title }}
                            </span>

                            <span class="lesson-meta-text">
                                {{ lessonIcon(lesson.type) }}
                                {{ lesson.meta }}
                            </span>
                        </div>

                        <span v-if="activeLesson?.id === lesson.id" class="active-dot"></span>
                    </div>
                </div>

                <div v-else class="lesson-list-collapsed">
                    <div v-for="(lesson, i) in (course?.lessons || [])" :key="lesson.id" class="lesson-icon-item"
                        :class="{
                            active: activeLesson?.id === lesson.id,
                            done: lesson.completed
                        }" :title="lesson.title" @click="selectLesson(lesson)">
                        <span>
                            {{ lesson.completed ? '✓' : i + 1 }}
                        </span>
                    </div>
                </div>
            </aside>

            <!-- Main -->
            <main class="lesson-main">

                <!-- Welcome -->
                <div v-if="!activeLesson" class="welcome-screen">
                    <div class="welcome-emoji">🎓</div>

                    <h2 class="welcome-title">
                        Welcome back, {{ studentName }}!
                    </h2>

                    <p class="welcome-sub">
                        Pick up where you left off or start from the beginning.
                    </p>

                    <button class="btn btn-primary" @click="resumeCourse">
                        {{
                            lastLesson
                                ? 'Continue: ' + lastLesson.title
                                : 'Start course'
                        }}
                        →
                    </button>
                </div>

                <template v-else>

                    <!-- Header -->
                    <div class="lesson-header">
                        <div>
                            <div class="lesson-breadcrumb">
                                <span class="type-badge" :class="'type-' + activeLesson.type">
                                    {{ activeLesson.type }}
                                </span>

                                <span class="lesson-index">
                                    Lesson {{ activeLessonIndex + 1 }}
                                    of {{ course?.lessons?.length || 0 }}
                                </span>
                            </div>

                            <h1 class="lesson-heading">
                                {{ activeLesson.title }}
                            </h1>
                        </div>

                        <div class="lesson-header-actions">
                            <button v-if="!activeLesson.completed" class="btn btn-primary btn-sm"
                                @click="markComplete(activeLesson)">
                                ✓ Mark complete
                            </button>

                            <span v-else class="done-chip">
                                ✓ Completed
                            </span>
                        </div>
                    </div>

                    <!-- VIDEO -->
                    <template v-if="activeLesson.type === 'video'">
                        <div v-if="
                            activeLesson.video_file ||
                            activeLesson.video_file_url ||
                            activeLesson.video_url
                        " class="video-player">
                            <video class="lesson-video" controls>
                                <source :src="activeLesson.video_file ||
                                    activeLesson.video_file_url ||
                                    activeLesson.video_url
                                    " type="video/mp4" />
                            </video>
                        </div>

                        <div class="content-tabs">
                            <div class="tab-bar">
                                <button class="tab" :class="{ active: contentTab === 'overview' }"
                                    @click="contentTab = 'overview'">
                                    Overview
                                </button>

                                <button class="tab" :class="{ active: contentTab === 'resources' }"
                                    @click="contentTab = 'resources'">
                                    Resources
                                </button>

                                <button class="tab" :class="{ active: contentTab === 'notes' }"
                                    @click="contentTab = 'notes'">
                                    My notes
                                </button>

                                <button class="tab" :class="{ active: contentTab === 'discussion' }"
                                    @click="contentTab = 'discussion'">
                                    Discussion
                                </button>
                            </div>

                            <div v-if="contentTab === 'overview'" class="tab-content">
                                <p class="lesson-desc">
                                    {{
                                        activeLesson.description ??
                                        `Learn the core concepts covered in this video lesson.
                                    Follow along and pause whenever you need to practice.`
                                    }}
                                </p>
                            </div>

                            <div v-if="contentTab === 'resources'" class="tab-content">
                                <div class="resource-list">
                                    <div v-for="(r, i) in activeLesson.resources ?? defaultResources" :key="i"
                                        class="resource-row">
                                        <span class="res-icon">
                                            {{
                                                r.type === 'pdf'
                                                    ? '📄'
                                                    : r.type === 'zip'
                                                        ? '📦'
                                                        : '🔗'
                                            }}
                                        </span>

                                        <span class="res-name">
                                            {{ r.name }}
                                        </span>

                                        <button class="btn btn-ghost btn-sm" @click="showToast('Downloading…')">
                                            ↓ Download
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div v-if="contentTab === 'notes'" class="tab-content">
                                <textarea v-model="myNote" class="input notes-textarea" rows="8"
                                    placeholder="Write your personal notes here…"></textarea>

                                <button class="btn btn-primary btn-sm mt-2" @click="showToast('Notes saved ✅')">
                                    Save notes
                                </button>
                            </div>
                        </div>
                    </template>

                    <!-- READING -->
                    <template v-else-if="activeLesson.type === 'reading'">
                        <div class="reading-content card">
                            <div class="reading-meta">
                                <span>
                                    📖 Reading · {{ activeLesson.meta }}
                                </span>
                            </div>

                            <div class="reading-body">
                                <p>
                                    {{
                                        activeLesson.content ??
                                        `This reading covers the foundational concepts you need
                                    before moving into the video lessons.
                                    Take your time and make sure you understand
                                    each section before continuing.`
                                    }}
                                </p>

                                <p>Key points to understand:</p>

                                <ul>
                                    <li>The difference between front-end and back-end development</li>
                                    <li>How HTTP requests and responses work</li>
                                    <li>What a REST API is</li>
                                    <li>Why we separate our data layer from our presentation layer</li>
                                </ul>
                            </div>
                        </div>
                    </template>

                    <!-- ASSIGNMENT -->
                    <template v-else-if="activeLesson.type === 'assignment'">
                        <div class="assignment-shell card">
                            <div class="assign-instructions card-inner">
                                <h4 class="assign-instructions-title">
                                    Instructions
                                </h4>

                                <p>
                                    {{
                                        activeLesson.assignment?.instructions ??
                                        `Build the project described below following the requirements.
                                    Submit a ZIP file containing your complete source
                                    code and a README with setup instructions.`
                                    }}
                                </p>
                            </div>
                        </div>
                    </template>

                    <!-- NAV -->
                    <div class="lesson-nav">
                        <button class="btn btn-ghost" :disabled="activeLessonIndex === 0" @click="prevLesson">
                            ← Previous
                        </button>

                        <button class="btn btn-primary"
                            :disabled="activeLessonIndex === (course?.lessons?.length || 0) - 1" @click="nextLesson">
                            Next lesson →
                        </button>
                    </div>
                </template>
            </main>
        </div>

        <!-- Toast -->
        <Transition name="toast">
            <div v-if="toast.visible" class="toast">
                {{ toast.message }}
            </div>
        </Transition>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const API_BASE = 'http://127.0.0.1:8000/api'

const courses = ref([])
const loading = ref(false)
const error = ref('')

const enrolledMap = reactive({})

const search = ref('')
const filterCategory = ref('')
const filterLevel = ref('')
const filterPrice = ref('')
const viewMode = ref('grid')
const enrolling = ref(false)
const toast = reactive({ visible: false, message: '' })
const overlay = reactive({ open: false, course: null })

const categories = computed(() => [
    ...new Set(courses.value.map(c => c.category).filter(Boolean))
])

const filteredCourses = computed(() => {
    return courses.value.filter(c => {
        const s = search.value.toLowerCase()

        const matchSearch =
            !s ||
            c.title?.toLowerCase().includes(s) ||
            c.teacher?.toLowerCase().includes(s) ||
            c.category?.toLowerCase().includes(s)

        const matchCat =
            !filterCategory.value ||
            c.category === filterCategory.value

        const matchLevel =
            !filterLevel.value ||
            c.level === filterLevel.value

        const matchPrice =
            !filterPrice.value ||
            (filterPrice.value === 'free' ? c.is_free : !c.is_free)

        return matchSearch && matchCat && matchLevel && matchPrice
    })
})

const activeFilters = computed(() => {
    const f = []

    if (filterCategory.value) {
        f.push({ key: 'filterCategory', label: filterCategory.value })
    }

    if (filterLevel.value) {
        f.push({ key: 'filterLevel', label: filterLevel.value })
    }

    if (filterPrice.value) {
        f.push({
            key: 'filterPrice',
            label: filterPrice.value === 'free' ? 'Free only' : 'Paid only'
        })
    }

    return f
})

function formatLevel(level) {
    if (!level) return 'Beginner'
    return level.charAt(0).toUpperCase() + level.slice(1)
}

function mapCourse(course) {
    return {
        id: course.id,
        title: course.title,
        description: course.description,
        category: course.category,
        level: formatLevel(course.level),
        language: course.language || 'English',
        duration_hours: course.duration_hours || 0,
        lessons_count: course.lessons_count || 0,
        enrolled_count: course.enrolled_count || 0,
        rating: course.rating || 0,
        reviews: course.reviews || 0,
        is_free: course.is_free,
        price: course.price || 0,
        original_price: null,
        has_certificate: course.has_certificate || false,
        teacher: course.teacher_name || 'Teacher',
        thumb: '📚',
        thumbBg: '#EEF1FF',
        objectives: course.objectives || [],
        requirements: course.requirements || [],
        curriculum_preview: course.curriculum_preview || []
    }
}

async function fetchCourses() {
    loading.value = true
    error.value = ''

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.get(`${API_BASE}/courses/`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })

        courses.value = response.data.map(mapCourse)

        response.data.forEach(course => {
            if (course.is_enrolled) {
                enrolledMap[course.id] = course.progress_percentage || 0
            }
        })
    } catch (err) {
        console.error(err)
        error.value = 'Failed to load courses.'
    } finally {
        loading.value = false
    }
}

function isEnrolled(id) {
    return id in enrolledMap
}

function enrolledProgress(id) {
    return enrolledMap[id] ?? 0
}

function lessonIcon(type) {
    return {
        video: '▶',
        reading: '📄',
        quiz: '📝',
        assignment: '📋'
    }[type] ?? '▶'
}

function clearFilter(key) {
    if (key === 'filterCategory') filterCategory.value = ''
    if (key === 'filterLevel') filterLevel.value = ''
    if (key === 'filterPrice') filterPrice.value = ''
}

function clearAllFilters() {
    filterCategory.value = ''
    filterLevel.value = ''
    filterPrice.value = ''
    search.value = ''
}

function openOverview(course) {
    overlay.course = course
    overlay.open = true
}

async function enroll(course) {
    if (!course || isEnrolled(course.id)) return

    enrolling.value = true

    try {
        const token = localStorage.getItem('access_token')

        await axios.post(
            `${API_BASE}/courses/${course.id}/enroll/`,
            {},
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        )

        enrolledMap[course.id] = 0
        showToast(`Enrolled in "${course.title}" 🎉`)
    } catch (err) {
        console.error(err)
        showToast('Failed to enroll.')
    } finally {
        enrolling.value = false
    }
}

function goToLearn(course) {
    overlay.open = false
    router.push(`/courses/${course.id}`)
}

function showToast(msg) {
    toast.message = msg
    toast.visible = true

    setTimeout(() => {
        toast.visible = false
    }, 3000)
}

onMounted(() => {
    fetchCourses()
})
</script>

<style src="./src/assets/CourseLearn.css"></style>