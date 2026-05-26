<template>
  <div>
    <div class="panel">
      <h3 class="section-title">📚 Lessons & curriculum</h3>

      <div class="lesson-list">
        <div v-for="(lesson, index) in form.lessons" :key="lesson.id" class="lesson-item lesson-item-column">
          <div class="lesson-header-row">
            <span class="drag-handle">⋮⋮</span>

            <span class="type-badge" :class="'type-' + lesson.type">
              {{ lesson.type }}
            </span>

            <div class="lesson-summary">
              <span class="lesson-title">
                {{ lesson.title || 'Untitled lesson' }}
              </span>

              <span class="lesson-meta">
                {{ lesson.meta }}
              </span>
            </div>

            <div class="lesson-actions">
              <button class="icon-btn" type="button" @click="$emit('edit-lesson', index)">
                {{ lesson.isEditing ? '✅' : '✏️' }}
              </button>

              <button class="icon-btn" type="button" @click="$emit('remove-lesson', index)">
                🗑
              </button>
            </div>
          </div>

          <div v-if="lesson.isEditing" class="lesson-editor">
            <label class="field-label">Title</label>

            <input v-model="lesson.title" class="input" placeholder="Lesson title" />

            <!-- VIDEO -->
            <template v-if="lesson.type === 'video'">
              <label class="field-label">Video description</label>

              <textarea v-model="lesson.content" class="input lesson-textarea" rows="4"
                placeholder="Describe this video lesson..."></textarea>

              <label class="field-label">Video URL</label>

              <input v-model="lesson.video_url" class="input" placeholder="https://youtube.com/..." />

              <label class="field-label">Or upload video</label>

              <input class="input" type="file" accept="video/*" @change="handleVideoUpload($event, lesson)" />
            </template>

            <!-- READING -->
            <template v-if="lesson.type === 'reading'">
              <label class="field-label">Reading content</label>

              <textarea v-model="lesson.content" class="input lesson-textarea" rows="8"
                placeholder="Write the lesson content..."></textarea>
            </template>

            <!-- QUIZ -->
            <template v-if="lesson.type === 'quiz'">
              <label class="field-label">Quiz description</label>

              <textarea v-model="lesson.content" class="input lesson-textarea" rows="3"
                placeholder="Short quiz description..."></textarea>

              <label class="field-label">Passing score (%)</label>

              <input v-model.number="lesson.quiz.passing_score" class="input" type="number" min="0" max="100" />

              <label class="field-label">Time limit in minutes</label>

              <input v-model.number="lesson.quiz.time_limit_minutes" class="input" type="number" min="1"
                placeholder="Optional" />

              <!-- FINAL EXAM -->
              <div class="final-exam-toggle">
                <div>
                  <div class="toggle-title">
                    Final Exam
                  </div>

                  <div class="toggle-sub">
                    Students must pass this quiz to complete the course and receive the certificate.
                  </div>
                </div>

                <input v-model="lesson.quiz.is_final_exam" type="checkbox" class="final-checkbox" />
              </div>

              <div class="quiz-box">
                <div v-for="(question, qIndex) in lesson.quiz.questions" :key="qIndex" class="question-box">
                  <label class="field-label">
                    Question {{ qIndex + 1 }}
                  </label>

                  <input v-model="question.text" class="input" placeholder="Question text" />

                  <select v-model="question.question_type" class="input" @change="handleQuestionTypeChange(question)">
                    <option value="multiple_choice">
                      Multiple choice
                    </option>

                    <option value="true_false">
                      True / False
                    </option>

                    <option value="short_answer">
                      Short answer
                    </option>
                  </select>

                  <input v-model.number="question.points" class="input" type="number" min="1" placeholder="Points" />

                  <div v-for="(option, oIndex) in question.options" :key="oIndex" class="option-row">
                    <input v-model="option.text" class="input" placeholder="Answer option" />

                    <label class="correct-label">
                      <input type="checkbox" v-model="option.is_correct" />

                      Correct
                    </label>

                    <button class="icon-btn" type="button" @click="removeOption(question, oIndex)">
                      🗑
                    </button>
                  </div>

                  <button v-if="question.question_type !== 'true_false'" class="add-lesson-btn" type="button"
                    @click="addOption(question)">
                    + Add option
                  </button>

                  <button class="danger-btn" type="button" @click="removeQuestion(lesson, qIndex)">
                    Remove question
                  </button>
                </div>

                <button class="add-lesson-btn w-full" type="button" @click="addQuestion(lesson)">
                  + Add question
                </button>
              </div>
            </template>

            <!-- ASSIGNMENT -->
            <template v-if="lesson.type === 'assignment'">
              <label class="field-label">
                Assignment instructions
              </label>

              <textarea v-model="lesson.assignment.instructions" class="input lesson-textarea" rows="6"
                placeholder="Explain what the student must submit..."></textarea>

              <label class="field-label">Due date</label>

              <input v-model="lesson.assignment.due_date" class="input" type="datetime-local" />

              <label class="field-label">Max score</label>

              <input v-model.number="lesson.assignment.max_score" class="input" type="number" min="1" />
            </template>

            <button class="btn btn-primary btn-sm mt-2" type="button" @click="$emit('edit-lesson', index)">
              Done
            </button>
          </div>
        </div>
      </div>

      <div class="add-lesson-grid">
        <button v-for="type in lessonTypes" :key="type.value" class="add-lesson-btn" type="button"
          @click="$emit('add-lesson', type.value)">
          + {{ type.label }}
        </button>
      </div>
    </div>

    <div class="panel mt-3">
      <h3 class="section-title">✅ Learning objectives</h3>

      <div class="objectives">
        <div v-for="(objective, index) in form.objectives" :key="index" class="objective-row">
          <span class="obj-check">✓</span>

          <input v-model="form.objectives[index]" class="input" placeholder="Students will be able to..." />

          <button class="icon-btn" type="button" @click="$emit('remove-objective', index)">
            🗑
          </button>
        </div>
      </div>

      <button class="add-lesson-btn w-full mt-2" type="button" @click="$emit('add-objective')">
        + Add learning objective
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: Object,
  lessonTypes: Array,
})

defineEmits([
  'add-lesson',
  'edit-lesson',
  'remove-lesson',
  'add-objective',
  'remove-objective',
])

function handleVideoUpload(event, lesson) {
  lesson.video_file = event.target.files[0]
}

function addQuestion(lesson) {
  lesson.quiz.questions.push({
    text: '',
    question_type: 'multiple_choice',
    points: 1,
    order_number: lesson.quiz.questions.length + 1,
    options: [
      {
        text: '',
        is_correct: false,
      },
      {
        text: '',
        is_correct: false,
      },
    ],
  })
}

function removeQuestion(lesson, index) {
  lesson.quiz.questions.splice(index, 1)
}

function addOption(question) {
  question.options.push({
    text: '',
    is_correct: false,
  })
}

function removeOption(question, index) {
  question.options.splice(index, 1)
}

function handleQuestionTypeChange(question) {
  if (question.question_type === 'true_false') {
    question.options = [
      {
        text: 'True',
        is_correct: false,
      },
      {
        text: 'False',
        is_correct: false,
      },
    ]
  }

  if (question.question_type === 'short_answer') {
    question.options = [
      {
        text: '',
        is_correct: true,
      },
    ]
  }
}
</script>

<style scoped>
.lesson-item-column {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.lesson-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.lesson-summary {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.lesson-editor {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.lesson-textarea {
  resize: vertical;
  min-height: 120px;
}

.quiz-box,
.question-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.question-box {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: white;
}

.option-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 8px;
  align-items: center;
}

.correct-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
}

.danger-btn {
  color: #dc2626;
  font-size: 13px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
}
</style>