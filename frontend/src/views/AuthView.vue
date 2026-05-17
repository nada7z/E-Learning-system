<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <div style="display:flex;align-items:center;gap:10px;justify-content:center;margin-bottom:8px">
          <div class="logo-icon">EF</div>
          <span style="font-family:Sora,sans-serif;font-weight:700;font-size:22px">EduFlow</span>
        </div>
        <p style="font-size:14px;color:var(--text2)">Professional Learning Management System</p>
      </div>

      <div class="role-tabs">
        <div v-for="r in roles" :key="r" class="role-tab" 
             :class="{ active: form.role === r }" 
             @click="form.role = r">
          {{ r.charAt(0).toUpperCase() + r.slice(1) }}
        </div>
      </div>

      <div class="tab-bar" style="margin-bottom:24px;width:100%">
        <div class="tab flex-1" style="text-align:center" 
             :class="{ active: authTab === 'login' }" 
             @click="authTab = 'login'">Sign In</div>
        <div class="tab flex-1" style="text-align:center" 
             :class="{ active: authTab === 'register' }" 
             @click="authTab = 'register'">Register</div>
      </div>

      <!-- Login Form -->
      <div v-if="authTab === 'login'">
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input class="form-input" type="email" v-model="form.email" placeholder="you@example.com" />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input class="form-input" type="password" v-model="form.password" placeholder="••••••••" />
        </div>
        <div class="flex items-center justify-between mt-2 mb-4">
          <label style="font-size:13px;display:flex;align-items:center;gap:6px;cursor:pointer">
            <input type="checkbox" style="accent-color:var(--accent)" /> Remember me
          </label>
          <span style="font-size:13px;color:var(--accent);cursor:pointer">Forgot password?</span>
        </div>
        <button class="btn btn-primary w-full" style="justify-content:center;padding:13px" 
                @click="handleSubmit" :disabled="loading">
          {{ loading ? 'Signing In...' : 'Sign In →' }}
        </button>
      </div>

      <!-- Register Form -->
      <div v-else>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">First Name</label>
            <input class="form-input" v-model="form.first_name" placeholder="John" />
          </div>
          <div class="form-group">
            <label class="form-label">Last Name</label>
            <input class="form-input" v-model="form.last_name" placeholder="Doe" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Email</label>
          <input class="form-input" type="email" v-model="form.email" placeholder="you@example.com" />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input class="form-input" type="password" v-model="form.password" placeholder="Create password" />
        </div>
        <button class="btn btn-primary w-full mt-2" style="justify-content:center;padding:13px" 
                @click="handleSubmit" :disabled="loading">
          {{ loading ? 'Creating Account...' : 'Create Account →' }}
        </button>
      </div>

      <div style="text-align:center;margin-top:20px">
        <span style="font-size:12px;color:var(--text3)">Demo: Choose role then Sign In</span>
      </div>

      <div class="flex items-center justify-center gap-3 mt-4">
        <span style="font-size:13px;color:var(--text2)">Dark mode</span>
        <div class="dark-toggle" :class="{ on: dark }" @click="$emit('toggle-dark')">
          <div class="dark-toggle-knob"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({ dark: Boolean })
const emit = defineEmits(['toggle-dark', 'success'])

const roles = ['student', 'teacher', 'admin']
const authTab = ref('login')
const loading = ref(false)

const form = ref({
  email: '',
  password: '',
  role: 'student',
  first_name: '',
  last_name: ''
})

// Axios instance
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json'
  }
})

const handleSubmit = async () => {
  // Basic validation
  if (!form.value.email || !form.value.password) {
    alert("Email and password are required!")
    return
  }

  // Extra validation for register
  if (
    authTab.value === 'register' &&
    (!form.value.first_name || !form.value.last_name)
  ) {
    alert("First name and last name are required!")
    return
  }

  loading.value = true

  // Choose endpoint
  const endpoint =
    authTab.value === 'login'
      ? 'auth/login/'
      : 'auth/register/'

  // Payload
  const payload =
    authTab.value === 'register'
      ? {
          username: form.value.email, // required by Django serializer
          email: form.value.email,
          password: form.value.password,
          first_name: form.value.first_name,
          last_name: form.value.last_name,
          role: form.value.role
        }
      : {
          email: form.value.email,
          password: form.value.password
        }

  try {
    const response = await api.post(endpoint, payload)

    const data = response.data

    // Save tokens if they exist
    if (data.access) {
      localStorage.setItem('access_token', data.access)
    }

    if (data.refresh) {
      localStorage.setItem('refresh_token', data.refresh)
    }

    // Save user data
    const userData = data.user || data
    localStorage.setItem('user', JSON.stringify(userData))

    emit('success', userData)

    // Success messages
    if (authTab.value === 'register') {
      alert('Account created successfully! 🎉')
      authTab.value = 'login'
    } else {
      alert(`Welcome ${userData.first_name || userData.email}! 👋`)
    }

    if (userData.role === 'student') {
  router.push('/student-dashboard')
}
else if (userData.role === 'teacher') {
  router.push('/teacher-dashboard')
}
else if (userData.role === 'admin') {
  router.push('/admin-dashboard')
}

  } catch (error) {
    console.error(error)

    const fallbackMsg =
      authTab.value === 'login'
        ? 'Login failed. Please check your credentials.'
        : 'Registration failed. Please check your information.'

    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.email?.[0] ||
      error.response?.data?.password?.[0] ||
      error.response?.data?.username?.[0] ||
      error.response?.data?.role?.[0] ||
      fallbackMsg

    alert(errorMsg)

  } finally {
    loading.value = false
  }
}
</script>