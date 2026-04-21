<script setup lang="ts">
import type { QuestionnaireCode } from '@features/questionnaires/model/questionnaire-store';

const props = defineProps<{
  questionnaireCode: QuestionnaireCode;
  isSubmitting: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  submit: [payload: Record<string, number>];
}>();

const definitions: Record<QuestionnaireCode, { id: string; label: string }[]> = {
  'PHQ-9': [
    { id: 'q1', label: 'Little interest or pleasure in doing things' },
    { id: 'q2', label: 'Feeling down, depressed, or hopeless' },
    { id: 'q3', label: 'Trouble falling or staying asleep, or sleeping too much' },
    { id: 'q4', label: 'Feeling tired or having little energy' },
    { id: 'q5', label: 'Poor appetite or overeating' },
    { id: 'q6', label: 'Feeling bad about yourself' },
    { id: 'q7', label: 'Trouble concentrating on things' },
    { id: 'q8', label: 'Moving or speaking slowly or being fidgety/restless' },
    { id: 'q9', label: 'Thoughts that you would be better off dead or of hurting yourself' },
  ],
  'GAD-7': [
    { id: 'q1', label: 'Feeling nervous, anxious, or on edge' },
    { id: 'q2', label: 'Not being able to stop or control worrying' },
    { id: 'q3', label: 'Worrying too much about different things' },
    { id: 'q4', label: 'Trouble relaxing' },
    { id: 'q5', label: 'Being so restless that it is hard to sit still' },
    { id: 'q6', label: 'Becoming easily annoyed or irritable' },
    { id: 'q7', label: 'Feeling afraid as if something awful might happen' },
  ],
};

const answers = ref<Record<string, number>>({});

function resetAnswers() {
  const next: Record<string, number> = {};
  for (const item of definitions[props.questionnaireCode]) {
    next[item.id] = 0;
  }
  answers.value = next;
}

watch(
  () => props.questionnaireCode,
  () => {
    resetAnswers();
  },
  { immediate: true }
);

function handleSubmit() {
  emit('submit', { ...answers.value });
}
</script>

<template>
  <form
    class="space-y-4 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm"
    data-testid="questionnaire-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-for="question in definitions[props.questionnaireCode]"
      :key="question.id"
      class="grid gap-2 rounded-2xl border border-slate-200 p-4"
    >
      <p class="text-sm font-medium text-slate-900">{{ question.label }}</p>
      <label :for="question.id" class="text-xs uppercase tracking-[0.12em] text-slate-500"
        >Score</label
      >
      <select
        :id="question.id"
        v-model.number="answers[question.id]"
        class="field-input max-w-xs"
        :data-testid="`question-answer-${question.id}`"
        :disabled="props.isSubmitting"
      >
        <option :value="0">0</option>
        <option :value="1">1</option>
        <option :value="2">2</option>
        <option :value="3">3</option>
      </select>
    </div>

    <p v-if="props.error" class="text-sm text-rose-600" data-testid="questionnaire-submit-error">
      {{ props.error }}
    </p>

    <div class="flex justify-end">
      <button
        type="submit"
        class="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
        data-testid="questionnaire-submit"
        :disabled="props.isSubmitting"
      >
        {{ props.isSubmitting ? 'Submitting…' : 'Submit questionnaire' }}
      </button>
    </div>
  </form>
</template>
