<script setup lang="ts">
import type { QuestionnaireCode } from '@features/questionnaires/model/questionnaire-store';

const props = defineProps<{
  patientEmail: string | null;
  isSubmitting: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  submit: [payload: { questionnaireCode: QuestionnaireCode }];
}>();

const questionnaireCode = ref<QuestionnaireCode>('PHQ-9');

function handleSubmit() {
  emit('submit', { questionnaireCode: questionnaireCode.value });
}
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">Questionnaire assignment</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">Assign PHQ-9 or GAD-7</h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        Create a pending questionnaire for the selected patient so they can complete it from their
        dashboard.
      </p>
    </div>

    <form
      class="grid gap-3 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm"
      @submit.prevent="handleSubmit"
    >
      <p v-if="props.patientEmail" class="text-sm text-slate-600">
        Assigning for: <span class="font-medium text-slate-900">{{ props.patientEmail }}</span>
      </p>
      <p v-else class="text-sm text-slate-500">Select a patient first.</p>

      <label for="questionnaire-code" class="text-sm font-medium text-slate-700"
        >Questionnaire</label
      >
      <select
        id="questionnaire-code"
        v-model="questionnaireCode"
        class="field-input max-w-md"
        data-testid="doctor-questionnaire-code-select"
        :disabled="props.isSubmitting || !props.patientEmail"
      >
        <option value="PHQ-9">PHQ-9</option>
        <option value="GAD-7">GAD-7</option>
      </select>

      <p v-if="props.error" class="text-sm text-rose-600" data-testid="doctor-questionnaire-error">
        {{ props.error }}
      </p>

      <div class="flex justify-end">
        <button
          type="submit"
          class="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          data-testid="assign-questionnaire-submit"
          :disabled="props.isSubmitting || !props.patientEmail"
        >
          {{ props.isSubmitting ? 'Assigning…' : 'Assign questionnaire' }}
        </button>
      </div>
    </form>
  </section>
</template>
