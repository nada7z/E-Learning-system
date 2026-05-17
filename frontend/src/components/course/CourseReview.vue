<template>
  <div>
    <div class="panel">
      <h3 class="section-title">👁 Course preview</h3>

      <div class="preview-card">
        <div
          class="preview-thumb"
          :style="{ background: selectedThumbnailBg }"
        >
          {{ form.thumbnail }}
        </div>

        <div class="preview-title">
          {{ form.title || 'Untitled Course' }}
        </div>

        <div class="preview-desc">
          {{ form.description || 'No description yet.' }}
        </div>

        <div class="meta-row">
          <span v-if="form.category" class="pill">
            {{ form.category }}
          </span>

          <span class="pill">
            {{ form.level }}
          </span>

          <span v-if="form.duration" class="pill">
            {{ form.duration }} hrs
          </span>

          <span class="pill">
            {{ form.language }}
          </span>

          <span v-if="form.certificate === 'yes'" class="pill pill-acc">
            Certificate
          </span>
        </div>

        <div v-if="form.tags.length" class="tag-row mt-2">
          <span
            v-for="tag in form.tags"
            :key="tag"
            class="tag sel small"
          >
            {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <div class="panel mt-3">
      <h3 class="section-title">📋 Checklist</h3>

      <div class="checklist">
        <div
          v-for="item in checklist"
          :key="item.label"
          class="checklist-row"
        >
          <span :class="item.ok ? 'icon-ok' : 'icon-muted'">
            {{ item.ok ? '✓' : '×' }}
          </span>

          <span class="checklist-label">
            {{ item.label }}
          </span>

          <span class="checklist-val">
            {{ item.val }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: Object,
  checklist: Array,
  selectedThumbnailBg: String,
})
</script>