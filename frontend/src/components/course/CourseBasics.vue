<template>
  <div class="panel">
    <h3 class="section-title">📘 Course information</h3>

    <div class="field">
      <label class="label">Title <span class="req">*</span></label>

      <input v-model="form.title" class="input" :class="{ error: errors.title }" maxlength="80"
        placeholder="e.g. Full-Stack Web Development with React" />

      <div class="field-footer">
        <span v-if="errors.title" class="err-msg">
          {{ errors.title }}
        </span>

        <span v-else />

        <span class="char-count">
          {{ form.title.length }} / 80
        </span>
      </div>
    </div>

    <div class="field">
      <label class="label">Short description <span class="req">*</span></label>

      <textarea v-model="form.description" class="input" :class="{ error: errors.description }" maxlength="300" rows="3"
        placeholder="What will students learn?" />

      <div class="field-footer">
        <span v-if="errors.description" class="err-msg">
          {{ errors.description }}
        </span>

        <span v-else />

        <span class="char-count">
          {{ form.description.length }} / 300
        </span>
      </div>
    </div>

    <div class="grid-2">
      <div class="field">
        <label class="label">Category <span class="req">*</span></label>

        <select v-model="form.category" class="input" :class="{ error: errors.category }">
          <option value="">Select category</option>

          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>

        <span v-if="errors.category" class="err-msg">
          {{ errors.category }}
        </span>
      </div>

      <div class="field">
        <label class="label">Level</label>

        <select v-model="form.level" class="input">
          <option v-for="level in levels" :key="level" :value="level">
            {{ level }}
          </option>
        </select>
      </div>
    </div>

    <div class="grid-3">
      <div class="field">
        <label class="label">Language</label>

        <select v-model="form.language" class="input">
          <option v-for="language in languages" :key="language" :value="language">
            {{ language }}
          </option>
        </select>
      </div>

      <div class="field">
        <label class="label">Duration hours</label>

        <input v-model.number="form.duration" class="input" type="number" min="1" max="500" placeholder="e.g. 40" />
      </div>

      <div class="field">
        <label class="label">Certificate</label>

        <select v-model="form.certificate" class="input">
          <option value="yes">Yes — on completion</option>
          <option value="no">No certificate</option>
        </select>
      </div>
    </div>

    <div class="field">
      <label class="label">Thumbnail</label>

      <div class="thumb-upload-box">
        <input id="thumbnailUpload" type="file" accept="image/*" class="hidden-file" @change="onThumbnailChange" />

        <label for="thumbnailUpload" class="upload-btn">
          Upload image
        </label>

        <button v-if="thumbnailPreview" type="button" class="remove-thumb-btn" @click="$emit('remove-thumbnail')">
          Remove
        </button>
      </div>

      <img v-if="thumbnailPreview" :src="thumbnailPreview" class="thumbnail-preview" alt="Course thumbnail preview" />

      <p class="hint">Or pick an icon:</p>

      <div class="thumb-row">
        <div v-for="option in thumbnailOptions" :key="option.icon" class="thumb-opt"
          :class="{ sel: form.thumbnail === option.icon }" :style="{ background: option.bg }"
          @click="selectIcon(option.icon)">
          {{ option.icon }}
        </div>
      </div>
    </div>

    <div class="field">
      <label class="label">Tags</label>

      <div class="tag-row">
        <span v-for="tag in availableTags" :key="tag" class="tag" :class="{ sel: form.tags.includes(tag) }"
          @click="$emit('toggle-tag', tag)">
          {{ form.tags.includes(tag) ? '✓' : '' }}
          {{ tag }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  form: Object,
  errors: Object,
  categories: Array,
  levels: Array,
  languages: Array,
  thumbnailOptions: Array,
  availableTags: Array,
  thumbnailPreview: String,
})

const emit = defineEmits([
  'toggle-tag',
  'thumbnail-upload',
  'remove-thumbnail',
])

function onThumbnailChange(event) {
  const file = event.target.files[0]

  if (!file) return

  emit('thumbnail-upload', file)
}

function selectIcon(icon) {
  emit('remove-thumbnail')
  props.form.thumbnail = icon
}
</script>

<style scoped>
.thumb-upload-box {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.hidden-file {
  display: none;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 12px;
  background: #6d28d9;
  color: white;
  font-weight: 700;
  cursor: pointer;
  border: none;
}

.remove-thumb-btn {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  font-weight: 600;
}

.thumbnail-preview {
  width: 240px;
  height: 140px;
  object-fit: cover;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  margin-bottom: 12px;
}
</style>