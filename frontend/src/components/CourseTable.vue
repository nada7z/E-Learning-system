<template>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Course</th>
          <th>Lessons</th>
          <th>Duration</th>
          <th>Price</th>
          <th>Status</th>
          <th v-if="role !== 'student'">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="course in courses"
          :key="course.id"
          @click="$emit('navigate', course.id)"
          style="cursor:pointer"
        >
          <td>
            <div style="display:flex;align-items:center;gap:10px">
              <div
                style="
                  width:36px;
                  height:36px;
                  border-radius:8px;
                  display:flex;
                  align-items:center;
                  justify-content:center;
                  font-size:18px;
                  flex-shrink:0;
                  background:#EEF1FF;
                "
              >
                📚
              </div>

              <div>
                <div style="font-weight:600;font-size:14px">
                  {{ course.title }}
                </div>

                <div style="font-size:12px;color:var(--text2)">
                  {{ course.teacher_name || 'Teacher' }}
                </div>
              </div>
            </div>
          </td>

          <td>
            {{ course.lessons_count || 0 }} lessons
          </td>

          <td>
            {{ course.duration_hours || 0 }}h
          </td>

          <td>
            {{ course.is_free ? 'Free' : `$${course.price}` }}
          </td>

          <td>
            <span
              class="badge"
              :class="course.is_published ? 'badge-green' : 'badge-warn'"
            >
              {{ course.is_published ? 'published' : 'draft' }}
            </span>
          </td>

          <td v-if="role !== 'student'">
            <div style="display:flex;gap:8px">
              <button
                class="btn btn-sm"
                @click.stop="$emit('edit', course.id)"
              >
                Edit
              </button>

              <button
                class="btn btn-sm btn-danger"
                @click.stop="$emit('delete', course.id)"
              >
                Delete
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  courses: {
    type: Array,
    default: () => []
  },

  role: {
    type: String,
    default: ''
  }
})

defineEmits([
  'navigate',
  'edit',
  'delete'
])

</script>