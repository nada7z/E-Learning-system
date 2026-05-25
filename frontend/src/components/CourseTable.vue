<template>
  <div class="table-wrap">
    <table class="course-table">
      <thead>
        <tr>
          <th>Course</th>
          <th>Category</th>
          <th>Level</th>
          <th>Teacher</th>
          <th>Lessons</th>
          <th>Duration</th>
          <th>Price</th>
          <th v-if="role !== 'student'">Status</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="course in courses" :key="course.id">
          <td>
            <div class="course-cell">
              <div class="thumb">
                📚
              </div>

              <div>
                <div class="title">
                  {{ course.title }}
                </div>

                <div class="desc">
                  {{ course.description }}
                </div>
              </div>
            </div>
          </td>

          <td>
            {{ course.category }}
          </td>

          <td>
            {{ course.level }}
          </td>

          <td>
            {{ course.teacher_name || 'Teacher' }}
          </td>

          <td>
            {{ course.lessons_count || 0 }}
          </td>

          <td>
            {{ course.duration_hours || 0 }}h
          </td>

          <td>
            {{ course.is_free ? 'Free' : `$${course.price}` }}
          </td>

          <td v-if="role !== 'student'">
            <span class="badge" :class="course.is_published
              ? 'badge-green'
              : 'badge-warn'
              ">
              {{ course.is_published ? 'Published' : 'Draft' }}
            </span>
          </td>

          <td>
            <div class="actions">

              <button class="btn btn-sm" @click="$emit('navigate', course.id)">
                View
              </button>

              <button v-if="role === 'teacher'" class="btn btn-sm" @click.stop="$emit('edit', course.id)">
                Edit
              </button>

              <button v-if="role === 'teacher'" class="btn btn-sm btn-danger" @click.stop="$emit('delete', course.id)">
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