<script setup lang="ts">
import type { MedicationItem } from '@features/medications/model/medication-store';
import type { SideEffectSeverity } from '@features/side-effects/model/side-effects-store';

const props = defineProps<{
  medications: MedicationItem[];
  isSubmitting: boolean;
  error: string | null;
  successMessage: string | null;
}>();

const emit = defineEmits<{
  submit: [
    payload: {
      medicationId: string | null;
      severity: SideEffectSeverity;
      symptom: string;
      note: string | null;
    },
  ];
}>();
const { t } = useI18n();

const medicationId = ref<string>('');
const severity = ref<SideEffectSeverity>('mild');
const symptom = ref('');
const note = ref('');

watch(
  () => props.medications,
  (medications) => {
    if (!medications.length) {
      medicationId.value = '';
      return;
    }

    if (medicationId.value && medications.some((item) => item.id === medicationId.value)) {
      return;
    }

    medicationId.value = '';
  },
  { immediate: true }
);

function handleSubmit() {
  if (!symptom.value.trim()) {
    return;
  }

  emit('submit', {
    medicationId: medicationId.value || null,
    severity: severity.value,
    symptom: symptom.value,
    note: note.value || null,
  });

  symptom.value = '';
  note.value = '';
  severity.value = 'mild';
  medicationId.value = '';
}
</script>

<template>
  <section class="space-y-4 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('sideEffectsForm.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('sideEffectsForm.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('sideEffectsForm.subtitle') }}
      </p>
    </div>

    <form class="grid gap-3" @submit.prevent="handleSubmit">
      <label for="side-effect-medication" class="text-sm font-medium text-slate-700">
        {{ t('sideEffectsForm.relatedMedication') }}
      </label>
      <select
        id="side-effect-medication"
        v-model="medicationId"
        class="field-input"
        data-testid="side-effect-medication-select"
        :disabled="props.isSubmitting"
      >
        <option value="">{{ t('sideEffectsForm.notSureNone') }}</option>
        <option v-for="item in props.medications" :key="item.id" :value="item.id">
          {{ item.name }}
        </option>
      </select>

      <label for="side-effect-severity" class="text-sm font-medium text-slate-700">
        {{ t('common.severity') }}
      </label>
      <select
        id="side-effect-severity"
        v-model="severity"
        class="field-input"
        data-testid="side-effect-severity-select"
        :disabled="props.isSubmitting"
      >
        <option value="mild">{{ t('statuses.severity.mild') }}</option>
        <option value="moderate">{{ t('statuses.severity.moderate') }}</option>
        <option value="severe">{{ t('statuses.severity.severe') }}</option>
      </select>

      <label for="side-effect-symptom" class="text-sm font-medium text-slate-700">
        {{ t('common.symptom') }}
      </label>
      <input
        id="side-effect-symptom"
        v-model="symptom"
        class="field-input"
        type="text"
        :placeholder="t('sideEffectsForm.symptomPlaceholder')"
        data-testid="side-effect-symptom-input"
        :disabled="props.isSubmitting"
      />

      <label for="side-effect-note" class="text-sm font-medium text-slate-700">
        {{ t('sideEffectsForm.clinicalNote') }}
      </label>
      <textarea
        id="side-effect-note"
        v-model="note"
        class="field-input min-h-24"
        :placeholder="t('sideEffectsForm.notePlaceholder')"
        data-testid="side-effect-note-input"
        :disabled="props.isSubmitting"
      />

      <p v-if="props.error" class="text-sm text-rose-600" data-testid="side-effect-form-error">
        {{ props.error }}
      </p>
      <p
        v-else-if="props.successMessage"
        class="text-sm text-emerald-700"
        data-testid="side-effect-form-success"
      >
        {{ props.successMessage }}
      </p>

      <div class="flex justify-end">
        <button
          type="submit"
          class="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          data-testid="side-effect-submit"
          :disabled="props.isSubmitting || !symptom.trim()"
        >
          {{ props.isSubmitting ? t('common.saving') : t('sideEffectsForm.reportSideEffect') }}
        </button>
      </div>
    </form>
  </section>
</template>
