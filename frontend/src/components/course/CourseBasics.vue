<template>
  <div class="panel">
    <h3 class="section-title">📘 Course information</h3>

    <div class="field">
      <label class="label">Title <span class="req">*</span></label>

      <input
        v-model="form.title"
        class="input"
        :class="{ error: errors.title }"
        maxlength="80"
        placeholder="e.g. Full-Stack Web Development with React"
      />

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

      <textarea
        v-model="form.description"
        class="input"
        :class="{ error: errors.description }"
        maxlength="300"
        rows="3"
        placeholder="What will students learn?"
      />

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

        <select
          v-model="form.category"
          class="input"
          :class="{ error: errors.category }"
        >
          <option value="">Select category</option>
          <option
            v-for="category in categories"
            :key="category"
            :value="category"
          >
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
          <option
            v-for="level in levels"
            :key="level"
            :value="level"
          >
            {{ level }}
          </option>
        </select>
      </div>
    </div>

    <div class="grid-3">
      <div class="field">
        <label class="label">Language</label>

        <select v-model="form.language" class="input">
          <option
            v-for="language in languages"
            :key="language"
            :value="language"
          >
            {{ language }}
          </option>
        </select>
      </div>

      <div class="field">
        <label class="label">Duration hours</label>

        <input
          v-model.number="form.duration"
          class="input"
          type="number"
          min="1"
          max="500"
          placeholder="e.g. 40"
        />
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

      <div class="thumb-row">
        <div
          v-for="option in thumbnailOptions"
          :key="option.icon"
          class="thumb-opt"
          :class="{ sel: form.thumbnail === option.icon }"
          :style="{ background: option.bg }"
          @click="form.thumbnail = option.icon"
        >
          {{ option.icon }}
        </div>
      </div>

      <p class="hint">Pick an icon or upload a custom image.</p>
    </div>

    <div class="field">
      <label class="label">Tags</label>

      <div class="tag-row">
        <span
          v-for="tag in availableTags"
          :key="tag"
          class="tag"
          :class="{ sel: form.tags.includes(tag) }"
          @click="$emit('toggle-tag', tag)"
        >
          {{ form.tags.includes(tag) ? '✓' : '' }}
          {{ tag }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: Object,
  errors: Object,
  categories: Array,
  levels: Array,
  languages: Array,
  thumbnailOptions: Array,
  availableTags: Array,
})

defineEmits(['toggle-tag'])
</script>