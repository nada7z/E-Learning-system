<template>
  <nav class="sidebar" :class="{ open }">
    <div class="sidebar-logo">
      <div class="logo-icon">EF</div><span class="logo-text">EduFlow</span>
    </div>
    <div class="sidebar-nav">
      <template v-if="role === 'student'">
        <NavSection label="Main" :items="studentMain" :page="page" @navigate="$emit('navigate', $event)" />
        <NavSection label="Progress" :items="studentProgress" :page="page" @navigate="$emit('navigate', $event)" />
      </template>
      <template v-else-if="role === 'teacher'">
        <NavSection label="Teaching" :items="teacherMain" :page="page" @navigate="$emit('navigate', $event)" />
        <NavSection label="Analytics" :items="teacherAnalytics" :page="page" @navigate="$emit('navigate', $event)" />
      </template>
      <template v-else-if="role === 'admin'">
        <NavSection label="Platform" :items="adminMain" :page="page" @navigate="$emit('navigate', $event)" />
        <NavSection label="Analytics" :items="adminAnalytics" :page="page" @navigate="$emit('navigate', $event)" />
      </template>
      <div class="nav-section">
        <div class="nav-label">General</div>
        <div class="nav-item notification-link" :class="{ active: page === 'notifications' }"
          @click="$emit('navigate', 'notifications')">
          <Bell class="nav-icon" />

          <span class="notification-dot" v-if="unreadCount > 0"></span>

          Notifications
        </div>
        <div class="nav-item" @click="$emit('logout')">
          <LogOut class="nav-icon" />Sign Out
        </div>
      </div>
    </div>
    <div class="sidebar-footer">
      <div class="user-chip">
        <div class="avatar" :style="avatarStyle">{{ avatarText }}</div>
        <div style="flex:1;min-width:0">
          <div
            style="font-size:14px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
            {{ displayName }}</div>
          <div style="font-size:12px;color:var(--text2);text-transform:capitalize">{{ role }}</div>
        </div>
        <div class="dark-toggle" :class="{ on: dark }" @click="$emit('toggle-dark')" style="flex-shrink:0">
          <div class="dark-toggle-knob"></div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import NavSection from './NavSection.vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Bell,
  LogOut
} from 'lucide-vue-next'
import {
  LayoutDashboard,
  BookOpen,
  PlayCircle,
  FileText,
  Target,
  Trophy,
  BarChart3,
  TrendingUp,
  Users,
  Settings
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const unreadCount = ref(0)

function goTo(path) {
  router.push(path)
}

const props = defineProps({
  page: String,
  role: String,
  dark: Boolean,
  unreadCount: Number,
  open: Boolean,
  user: Object
})

defineEmits(['navigate', 'logout', 'toggle-dark'])

const studentMain = [
  {
    page: 'student-dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard'
  },

  {
    page: 'explore-courses',
    icon: BookOpen,
    label: 'Explore Courses'
  },

  {
    page: 'courses',
    icon: BookOpen,
    label: 'My Courses'
  },

  {
    page: 'continue-learning',
    icon: PlayCircle,
    label: 'Continue Learning'
  },
]

const studentProgress = [
  {
    page: 'student/assignments',
    icon: FileText,
    label: 'Assignments'
  },

  {
    page: 'student/quizzes',
    icon: Target,
    label: 'Quizzes'
  },

  {
    page: 'certificates',
    icon: Trophy,
    label: 'Certificates'
  },
]

const teacherMain = [
  {
    page: 'teacher-dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard'
  },

  {
    page: 'courses',
    icon: BookOpen,
    label: 'My Courses'
  },

  {
    page: 'assignments',
    icon: FileText,
    label: 'Assignments'
  },

  {
    page: 'quizzes',
    icon: Target,
    label: 'Quizzes'
  },
]

const teacherAnalytics = [
  {
    page: 'student-stats',
    icon: BarChart3,
    label: 'Student Stats'
  },

  {
    page: 'course-performance',
    icon: TrendingUp,
    label: 'Course Performance'
  },
]

const adminMain = [
  {
    page: 'admin-dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard'
  },

  {
    page: 'users',
    icon: Users,
    label: 'Users'
  },

  {
    page: 'admin-courses',
    icon: BookOpen,
    label: 'Courses'
  },
]

const adminAnalytics = [
  {
    page: 'reports',
    icon: BarChart3,
    label: 'Reports'
  },
]

const currentUser = computed(() => {
  if (props.user) return props.user

  const savedUser = localStorage.getItem('user')
  return savedUser ? JSON.parse(savedUser) : null
})

const displayName = computed(() => {
  const user = currentUser.value

  if (!user) return 'User'

  const fullName =
    `${user.first_name || ''} ${user.last_name || ''}`.trim()

  return fullName || user.username || user.email || 'User'
})

const avatarText = computed(() => {
  const user = currentUser.value

  if (!user) return 'U'

  const first = user.first_name?.charAt(0) || ''
  const last = user.last_name?.charAt(0) || ''

  if (first || last)
    return `${first}${last}`.toUpperCase()

  return user.email?.charAt(0).toUpperCase() || 'U'
})

const avatarStyle = computed(() => ({
  background:
    props.role === 'student'
      ? '#EEF1FF'
      : props.role === 'teacher'
        ? '#E0F2F1'
        : '#EDE9FE',

  color:
    props.role === 'student'
      ? '#3D5AFE'
      : props.role === 'teacher'
        ? '#00897B'
        : '#7C3AED',
}))

async function fetchUnreadCount() {
  try {
    const token = localStorage.getItem('access_token')

    const res = await fetch('http://127.0.0.1:8000/api/notifications/', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    const data = await res.json()

    unreadCount.value = data.filter((n) => !n.is_read).length
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchUnreadCount()
  window.addEventListener('notifications-updated', fetchUnreadCount)
})

</script>

<style scoped>
.notification-dot {
  position: absolute;
  top: 8px;
  left: 18px;

  width: 10px;
  height: 10px;

  background: #ef4444;
  border-radius: 50%;

  border: 2px solid white;
}

.notification-link {
  position: relative;
}
</style>