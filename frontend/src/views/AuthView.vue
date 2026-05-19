<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <div style="display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:12px">
          <div class="logo-icon">EF</div>
          <h1 style="margin:0;font-size:24px">EduFlow</h1>
        </div>

        <p style="color:var(--text2);font-size:15px">
          Professional Learning Management System
        </p>
      </div>

      <div class="role-tabs">
        <div
          class="role-tab"
          :class="{ active: form.role === 'student' }"
          @click="form.role = 'student'"
        >
          Student
        </div>

        <div
          class="role-tab"
          :class="{ active: form.role === 'teacher' }"
          @click="form.role = 'teacher'"
        >
          Teacher
        </div>

        <div
          class="role-tab"
          :class="{ active: form.role === 'admin' }"
          @click="form.role = 'admin'"
        >
          Admin
        </div>
      </div>

      <div class="role-tabs">
        <div
          class="role-tab"
          :class="{ active: authTab === 'login' }"
          @click="authTab = 'login'"
        >
          Sign In
        </div>

        <div
          class="role-tab"
          :class="{ active: authTab === 'register' }"
          @click="authTab = 'register'"
        >
          Register
        </div>
      </div>

      <div v-if="authTab === 'register'" class="form-row">
        <div class="form-group">
          <label class="form-label">First Name</label>
          <input
            v-model="form.first_name"
            class="form-input"
            type="text"
            placeholder="First name"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Last Name</label>
          <input
            v-model="form.last_name"
            class="form-input"
            type="text"
            placeholder="Last name"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Email Address</label>
        <input
          v-model="form.email"
          class="form-input"
          type="email"
          placeholder="you@example.com"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Password</label>
        <input
          v-model="form.password"
          class="form-input"
          type="password"
          placeholder="••••••••"
        />
      </div>

      <div
        v-if="authTab === 'login'"
        style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px"
      >
        <label style="display:flex;align-items:center;gap:8px;font-size:14px">
          <input type="checkbox" />
          Remember me
        </label>

        <a style="color:var(--accent);font-size:14px" href="#">
          Forgot password?
        </a>
      </div>

      <p v-if="error" class="auth-error">
        {{ error }}
      </p>

      <button
        class="btn btn-primary"
        style="width:100%;justify-content:center;padding:13px 18px;font-size:15px"
        :disabled="loading"
        @click="handleSubmit"
      >
        {{
          loading
            ? 'Please wait...'
            : authTab === 'login'
            ? 'Sign In →'
            : 'Create Account →'
        }}
      </button>

      <p style="text-align:center;color:var(--text3);font-size:13px;margin-top:24px">
        Demo: Choose role then Sign In
      </p>

      <div style="display:flex;align-items:center;gap:12px;margin-top:18px">
        <span style="font-size:14px;color:var(--text2)">Dark mode</span>

        <div
          class="dark-toggle"
          :class="{ on: isDark }"
          @click="toggleDark"
        >
          <div class="dark-toggle-knob"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const authTab = ref('login')
const loading = ref(false)
const error = ref('')
const isDark = ref(false)

const form = reactive({
  role: 'student',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
})

watch(
  () => form.role,
  () => {
    error.value = ''
  }
)

watch(authTab, () => {
  error.value = ''
})

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

function getErrorMessage(err) {
  const data = err.response?.data

  if (!data) {
    return 'Could not connect to the server.'
  }

  if (data.detail) {
    return 'Incorrect email or password.'
  }

  if (data.email) {
    return Array.isArray(data.email)
      ? data.email[0]
      : data.email
  }

  if (data.password) {
    return Array.isArray(data.password)
      ? data.password[0]
      : data.password
  }

  if (data.username) {
    return Array.isArray(data.username)
      ? data.username[0]
      : data.username
  }

  if (data.role) {
    return Array.isArray(data.role)
      ? data.role[0]
      : data.role
  }

  if (data.message) {
    return data.message
  }

  return 'Authentication failed.'
}

async function handleSubmit() {
  error.value = ''

  if (!form.email.trim()) {
    error.value = 'Email is required.'
    return
  }

  if (!form.password.trim()) {
    error.value = 'Password is required.'
    return
  }

  if (authTab.value === 'register') {
    if (!form.first_name.trim()) {
      error.value = 'First name is required.'
      return
    }

    if (!form.last_name.trim()) {
      error.value = 'Last name is required.'
      return
    }
  }

  loading.value = true

  try {
    const url =
      authTab.value === 'register'
        ? 'http://127.0.0.1:8000/api/auth/register/'
        : 'http://127.0.0.1:8000/api/auth/login/'

    const payload =
      authTab.value === 'register'
        ? {
            username: form.email,
            email: form.email,
            password: form.password,
            first_name: form.first_name,
            last_name: form.last_name,
            role: form.role,
          }
        : {
            email: form.email,
            password: form.password,
            role: form.role,
          }

    const response = await axios.post(url, payload)
    const data = response.data
    const userData = data.user || data

    if (authTab.value === 'login' && userData.role !== form.role) {
      error.value = `This is not a ${form.role} account.`

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      return
    }

    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(userData))

    if (userData.role === 'student') {
      router.push('/student-dashboard')
    } else if (userData.role === 'teacher') {
      router.push('/teacher-dashboard')
    } else if (userData.role === 'admin') {
      router.push('/admin-dashboard')
    } else {
      router.push('/')
    }
  } catch (err) {
    console.error(err)
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-error {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 14px;
}
</style>