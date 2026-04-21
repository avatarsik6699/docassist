<script setup lang="ts">
import type { QuestionnaireCode } from '@features/questionnaires/model/questionnaire-store';

const props = defineProps<{
  questionnaireCode: QuestionnaireCode;
  isSubmitting: boolean;
  error: string | null;
}>();
const { t } = useI18n();

const emit = defineEmits<{
  submit: [payload: Record<string, number>];
}>();

const definitions: Record<QuestionnaireCode, { id: string }[]> = {
  'PHQ-9': [
    { id: 'q1' },
    { id: 'q2' },
    { id: 'q3' },
    { id: 'q4' },
    { id: 'q5' },
    { id: 'q6' },
    { id: 'q7' },
    { id: 'q8' },
    { id: 'q9' },
  ],
  'GAD-7': [
    { id: 'q1' },
    { id: 'q2' },
    { id: 'q3' },
    { id: 'q4' },
    { id: 'q5' },
    { id: 'q6' },
    { id: 'q7' },
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

function questionLabel(questionId: string): string {
  return t(`questionnaireForm.questions.${props.questionnaireCode}.${questionId}`);
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
      <p class="text-sm font-medium text-slate-900">{{ questionLabel(question.id) }}</p>
      <label :for="question.id" class="text-xs uppercase tracking-[0.12em] text-slate-500">{{
        t('common.score')
      }}</label>
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
        {{ props.isSubmitting ? t('questionnaireForm.submitting') : t('questionnaireForm.submit') }}
      </button>
    </div>
  </form>
</template>
