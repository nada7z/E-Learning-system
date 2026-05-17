<template>
  <div>
    <div class="panel">
      <h3 class="section-title">💵 Pricing</h3>

      <div class="pricing-row">
        <div
          class="pricing-card"
          :class="{ sel: form.pricing === 'free' }"
          @click="form.pricing = 'free'"
        >
          <h4>Free</h4>
          <p>Open enrollment, no payment required.</p>
        </div>

        <div
          class="pricing-card"
          :class="{ sel: form.pricing === 'paid' }"
          @click="form.pricing = 'paid'"
        >
          <h4>Paid</h4>
          <p>Set a price for full access.</p>
        </div>
      </div>

      <div v-if="form.pricing === 'paid'" class="grid-2 mt-3">
        <div class="field">
          <label class="label">Price</label>

          <input
            v-model.number="form.price"
            class="input"
            type="number"
            min="1"
            placeholder="e.g. 49"
          />
        </div>

        <div class="field">
          <label class="label">Discount price</label>

          <input
            v-model.number="form.discountPrice"
            class="input"
            type="number"
            min="0"
            placeholder="Optional"
          />
        </div>
      </div>
    </div>

    <div class="panel mt-3">
      <h3 class="section-title">⚙️ Visibility & access</h3>

      <div
        v-for="toggle in toggleSettings"
        :key="toggle.key"
        class="toggle-row"
      >
        <div>
          <div class="toggle-label">
            {{ toggle.label }}
          </div>

          <div class="toggle-hint">
            {{ toggle.hint }}
          </div>
        </div>

        <div
          class="toggle"
          :class="{ on: form.settings[toggle.key] }"
          role="switch"
          tabindex="0"
          @click="form.settings[toggle.key] = !form.settings[toggle.key]"
          @keydown.enter="form.settings[toggle.key] = !form.settings[toggle.key]"
        >
          <div class="toggle-knob" />
        </div>
      </div>
    </div>

    <div class="panel mt-3">
      <h3 class="section-title">🕒 Schedule</h3>

      <div class="grid-2">
        <div class="field">
          <label class="label">Start date</label>

          <input
            v-model="form.startDate"
            class="input"
            type="date"
          />
        </div>

        <div class="field">
          <label class="label">Enrollment deadline</label>

          <input
            v-model="form.enrollDeadline"
            class="input"
            type="date"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: Object,
  toggleSettings: Array,
})
</script>