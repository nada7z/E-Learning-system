<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">My Certificates</h1>
      <p class="page-sub">Certificates earned from completed courses</p>
    </div>

    <div v-if="loading" class="card">
      Loading certificates...
    </div>

    <div v-else-if="error" class="card error-card">
      {{ error }}
    </div>

    <div v-else-if="certificates.length === 0" class="card empty-certificates">
      <div class="empty-icon">🎓</div>
      <h3>No certificates yet</h3>
      <p>
        Complete a course by passing all quizzes, assignments, and the final exam.
      </p>
    </div>

    <div v-else class="cert-grid">
      <div v-for="(certificate, index) in certificates" :key="certificate.id" class="card cert-card"
        @click="activeCertificate = index">
        <div class="cert-thumb">🎓</div>

        <div class="cert-course">
          {{ certificate.course_title }}
        </div>

        <div class="cert-date">
          Issued {{ formatDate(certificate.issued_at) }}
        </div>

        <div class="cert-code">
          Code: {{ certificate.certificate_code }}
        </div>

        <button class="btn btn-primary btn-sm" @click.stop="activeCertificate = index">
          View Certificate
        </button>
      </div>
    </div>

    <div v-if="selected" class="certificate">
      <div class="cert-border"></div>

      <div class="cert-seal">🎓</div>

      <div class="cert-label">
        Certificate of Completion
      </div>

      <div class="cert-small">
        This is to certify that
      </div>

      <div class="cert-student">
        {{ selected.student_name }}
      </div>

      <div class="cert-small cert-margin">
        has successfully completed the course
      </div>

      <div class="cert-title">
        {{ selected.course_title }}
      </div>

      <div class="cert-code-large">
        Certificate Code: {{ selected.certificate_code }}
      </div>

      <div class="cert-date-large">
        Issued on {{ formatDate(selected.issued_at) }}
      </div>

      <a v-if="selected.pdf_url" :href="selected.pdf_url" target="_blank" class="btn btn-primary">
        Download PDF
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

const loading = ref(false)
const error = ref('')
const certificates = ref([])
const activeCertificate = ref(null)

const selected = computed(() => {
  if (activeCertificate.value === null) return null
  return certificates.value[activeCertificate.value] || null
})

function authHeaders() {
  const token = localStorage.getItem('access_token')

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

async function fetchCertificates() {
  loading.value = true
  error.value = ''

  try {
    const res = await axios.get(
      `${API_BASE}/certificates/my-certificates/`,
      authHeaders()
    )

    certificates.value = res.data || []

    if (certificates.value.length > 0) {
      activeCertificate.value = 0
    }
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load certificates.'
  } finally {
    loading.value = false
  }
}

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleDateString()
}

onMounted(() => {
  fetchCertificates()
})
</script>

<style scoped>
.cert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.cert-card {
  cursor: pointer;
}

.cert-thumb {
  height: 80px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin-bottom: 16px;
  background: var(--accent-light, #EEF1FF);
}

.cert-course {
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 4px;
}

.cert-date {
  font-size: 13px;
  color: var(--text2);
  margin-bottom: 8px;
}

.cert-code {
  font-size: 12px;
  color: var(--text3);
  margin-bottom: 12px;
}

.empty-certificates {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.error-card {
  color: #dc2626;
}

.certificate {
  background: white;
  border-radius: 24px;
  padding: 48px;
  text-align: center;
  position: relative;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.cert-border {
  position: absolute;
  inset: 16px;
  border: 2px solid var(--accent, #4f46e5);
  border-radius: 18px;
  pointer-events: none;
}

.cert-seal {
  font-size: 52px;
  margin-bottom: 12px;
}

.cert-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .15em;
  color: var(--text2);
  margin-bottom: 12px;
}

.cert-small {
  font-family: Sora, sans-serif;
  font-size: 13px;
  color: var(--text2);
  margin-bottom: 8px;
}

.cert-margin {
  margin: 16px 0 8px;
}

.cert-student {
  font-family: Sora, sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
  padding: 8px 0;
  border-bottom: 2px solid var(--accent, #4f46e5);
  display: inline-block;
  min-width: 200px;
}

.cert-title {
  font-family: Sora, sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--accent, #4f46e5);
  margin-bottom: 16px;
}

.cert-code-large,
.cert-date-large {
  font-size: 13px;
  color: var(--text2);
  margin-bottom: 10px;
}
</style>