<template>
  <div>
    <div class="progress-bar">
      <div
        class="progress-fill"
        :style="{ width: (step / totalSteps * 100) + '%' }"
      />
    </div>

    <div class="stepper">
      <div
        v-for="(label, index) in stepLabels"
        :key="label"
        class="step"
      >
        <div
          class="step-circle"
          :class="{
            done: step > index + 1,
            active: step === index + 1,
            idle: step < index + 1,
          }"
        >
          <span v-if="step > index + 1">✓</span>
          <span v-else>{{ index + 1 }}</span>
        </div>

        <span
          class="step-label"
          :class="{
            done: step > index + 1,
            active: step === index + 1,
          }"
        >
          {{ label }}
        </span>

        <div
          v-if="index < stepLabels.length - 1"
          class="step-line"
          :class="{ done: step > index + 1 }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  step: Number,
  totalSteps: Number,
  stepLabels: Array,
})
</script>