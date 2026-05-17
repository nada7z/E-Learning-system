<template>
  <div class="table-wrap">
    <table>
      <thead><tr><th>User</th><th>Role</th><th>Courses</th><th>Joined</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td><div style="display:flex;align-items:center;gap:12px"><div class="avatar" :style="{ background: u.color + '22', color: u.color }">{{ u.avatar }}</div><div><div style="font-weight:600;font-size:14px">{{ u.name }}</div><div style="font-size:12px;color:var(--text2)">{{ u.email }}</div></div></div></td>
          <td><span class="badge" :class="u.role === 'Admin' ? 'badge-purple' : u.role === 'Teacher' ? 'badge-green' : 'badge-blue'">{{ u.role }}</span></td>
          <td>{{ u.courses }}</td><td style="color:var(--text2);font-size:13px">{{ u.joined }}</td>
          <td><span class="badge" :class="u.status === 'active' ? 'badge-green' : 'badge-gray'">{{ u.status }}</span></td>
          <td><button class="btn btn-ghost btn-sm" @click="$emit('toast', 'Editing ' + u.name)">Edit</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
defineProps({ users: Array })
defineEmits(['toast'])
</script>
