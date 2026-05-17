<template>
  <div class="page">
    <div class="page-header flex items-center justify-between"><div><h1 class="page-title">User Management</h1><p class="page-sub">{{ mockUsers.length }} total users</p></div><button class="btn btn-primary" @click="$emit('toast', 'Add User dialog opened', '➕')">+ Add User</button></div>
    <div style="display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap"><input style="flex:1;min-width:200px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 14px;font-size:14px;color:var(--text)" placeholder="Search users…" /><select style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 14px;font-size:14px;color:var(--text)"><option>All Roles</option><option>Student</option><option>Teacher</option><option>Admin</option></select></div>
    <div class="card" style="padding:0"><UsersTable :users="mockUsers" @toast="$emit('toast', $event)" /></div>
  </div>
</template>
<script setup>
import UsersTable from '../components/UsersTable.vue'
defineEmits(['toast'])
</script>
