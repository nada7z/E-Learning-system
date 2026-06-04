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

        <button class="certificate-btn" @click="viewCertificate(certificate)">
          View Certificate
        </button>
      </div>
    </div>

    <div v-if="selectedCertificate" class="certificate-preview">
      <div class="certificate">
        <div class="certificate-icon">
          🎓
        </div>

        <h3>CERTIFICATE OF COMPLETION</h3>

        <p>This is to certify that</p>

        <h1>
          {{ selectedCertificate.student_name }}
        </h1>

        <p>
          has successfully completed
        </p>

        <h2>
          {{ selectedCertificate.course_title }}
        </h2>

        <p>
          Issued {{ formatDate(selectedCertificate.issued_at) }}
        </p>

        <p>
          {{ selectedCertificate.certificate_code }}
        </p>

        <button class="close-btn" @click="closeCertificate">
          Close
        </button>
      </div>
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

const selectedCertificate = ref(null)

function viewCertificate(certificate) {
  selectedCertificate.value = certificate
}

function closeCertificate() {
  selectedCertificate.value = null
}

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
.certificates-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 6px;
  color: var(--text, #0f172a);
}

.page-header p {
  margin: 0;
  color: var(--text2, #64748b);
  font-size: 14px;
}

.cert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, 360px);
  gap: 18px;
  margin-bottom: 28px;
  justify-content: start;
}

.cert-card {
  background: #fff;
  border: 1px solid #e5e0d6;
  border-radius: 18px;
  padding: 18px;
  cursor: pointer;
}

.cert-card.active {
  border-color: #9ca3af;
}

.cert-thumb {
  height: 80px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  margin-bottom: 16px;
  background: #eef1ff;
}

.cert-course {
  font-weight: 800;
  font-size: 16px;
  margin-bottom: 4px;
  color: #0f172a;
}

.cert-date {
  font-size: 13px;
  color: #5f6368;
  margin-bottom: 12px;
}

.cert-code {
  display: none;
}

.cert-actions {
  display: flex;
  gap: 8px;
}

.certificate-btn {
  flex: 1;
  border: none;
  border-radius: 9px;
  padding: 10px 14px;
  background: #3d5afe;
  color: white;
  font-weight: 800;
  font-size: 14px;
  cursor: pointer;
}

.certificate-btn:hover {
  background: #304ffe;
}

.download-btn {
  width: 44px;
  border: 1px solid #e5e0d6;
  border-radius: 10px;
  background: white;
  color: #555;
  font-size: 16px;
  cursor: pointer;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 8px 0 16px;
}

.preview-header h2 {
  font-size: 22px;
  font-weight: 800;
  margin: 0;
}

.close-btn {
  border: 1px solid #e5e0d6;
  border-radius: 10px;
  padding: 8px 14px;
  background: white;
  color: #555;
  font-weight: 700;
  cursor: pointer;
}

.certificate-preview {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.certificate {
  width: 100%;
  max-width: 680px;
  min-height: 460px;
  background: white;
  border-radius: 22px;
  padding: 42px 40px;
  text-align: center;
  position: relative;
  border: 1px solid #e5e0d6;
  box-shadow: 0 0 0 10px #f8f7f3;
}

.certificate::before {
  content: "";
  position: absolute;
  inset: 12px;
  border: 1px solid #e5e0d6;
  border-radius: 16px;
  pointer-events: none;
}

.certificate-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 4px solid #3d5afe;
  background: #eef1ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  margin: 0 auto 22px;
}

.certificate h3 {
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: #5f6368;
  margin: 0 0 14px;
}

.certificate p {
  font-size: 14px;
  color: #4b5563;
  margin: 0 0 16px;
}

.certificate h1 {
  font-size: 32px;
  font-weight: 900;
  color: #0f172a;
  margin: 0 auto 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3d5afe;
  display: inline-block;
  min-width: 220px;
}

.certificate h2 {
  font-size: 22px;
  font-weight: 900;
  color: #3d5afe;
  margin: 0 0 28px;
}

.certificate-footer {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  max-width: 420px;
  margin: 0 auto 20px;
}

.cert-signature {
  border-top: 1px solid #e5e0d6;
  padding-top: 10px;
  text-align: left;
}

.cert-signature strong {
  display: block;
  font-size: 14px;
  color: #0f172a;
}

.cert-signature span {
  color: #4b5563;
  font-size: 12px;
}

.cert-code-large,
.cert-date-large {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 18px;
}

.empty-certificates {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.error-card {
  color: #dc2626;
}
</style>