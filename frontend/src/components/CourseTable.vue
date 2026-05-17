<template>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Course</th><th>Students</th><th>Completion</th><th>Rating</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-for="c in courses" :key="c.id">
          <td><div style="display:flex;align-items:center;gap:10px"><div style="width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0" :style="{ background: c.color }">{{ c.thumb }}</div><div><div style="font-weight:600;font-size:14px">{{ c.title }}</div><div style="font-size:12px;color:var(--text2)">{{ c.lessons }} lessons</div></div></div></td>
          <td><span style="font-weight:600">{{ c.enrolled }}</span></td>
          <td><div style="display:flex;align-items:center;gap:8px;min-width:120px"><div class="progress-bar" style="flex:1"><div class="progress-fill" :style="{ width: c.progress + '%', background: '#3D5AFE' }"></div></div><span style="font-size:12px;font-weight:600;color:var(--text2);min-width:32px">{{ c.progress }}%</span></div></td>
          <td><span style="font-weight:600">⭐ {{ c.rating }}</span></td>
          <td><span class="badge" :class="c.status === 'published' ? 'badge-green' : 'badge-warn'">{{ c.status }}</span></td>
          <td><button class="btn btn-ghost btn-sm" @click="$emit('navigate', 'course-detail')">Edit</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
defineProps({ courses: Array })
defineEmits(['navigate'])
</script>
