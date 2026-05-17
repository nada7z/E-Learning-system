<template>
  <div class="page">
    <div class="page-header"><h1 class="page-title">My Certificates</h1><p class="page-sub">Certificates earned from completed courses</p></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:32px">
      <div class="card" style="cursor:pointer" v-for="(c, i) in certificates" :key="c.id" @click="activeCertificate = i">
        <div style="height:80px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:40px;margin-bottom:16px" :style="{ background: c.color }">{{ c.thumb }}</div>
        <div style="font-weight:700;font-size:15px;margin-bottom:4px">{{ c.course }}</div>
        <div style="font-size:13px;color:var(--text2);margin-bottom:12px">Completed {{ c.date }}</div>
        <button class="btn btn-primary btn-sm" @click.stop="activeCertificate = i">View Certificate</button>
      </div>
    </div>
    <div v-if="selected" class="certificate">
      <div class="cert-border"></div><div class="cert-seal">🎓</div>
      <div style="font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.15em;color:var(--text2);margin-bottom:12px">Certificate of Completion</div>
      <div style="font-family:Sora,sans-serif;font-size:13px;color:var(--text2);margin-bottom:8px">This is to certify that</div>
      <div style="font-family:Sora,sans-serif;font-size:32px;font-weight:700;color:var(--text);margin-bottom:8px;padding:8px 0;border-bottom:2px solid var(--accent);display:inline-block;min-width:200px">Alex Student</div>
      <div style="font-size:14px;color:var(--text2);margin:16px 0 8px">has successfully completed the course</div>
      <div style="font-family:Sora,sans-serif;font-size:22px;font-weight:700;color:var(--accent);margin-bottom:24px">{{ selected.course }}</div>
      <button class="btn btn-primary" @click="$emit('toast', 'Certificate downloaded as PDF!', '📥')">↓ Download PDF</button>
    </div>
  </div>
</template>
<script setup>
import { computed, ref } from 'vue'
defineEmits(['toast'])
const activeCertificate = ref(null)
const certificates = [{ id:1, course:'UI/UX Design Fundamentals', date:'June 15, 2024', color:'#FCE7F3', thumb:'🎨' }, { id:2, course:'Web Development Basics', date:'April 2, 2024', color:'#EEF1FF', thumb:'💻' }]
const selected = computed(() => activeCertificate.value === null ? null : certificates[activeCertificate.value])
</script>
