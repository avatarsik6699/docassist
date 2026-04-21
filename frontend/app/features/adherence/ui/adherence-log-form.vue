<script setup lang="ts">
import type { AdherenceStatus } from '@features/adherence/model/adherence-store';
import type { MedicationItem } from '@features/medications/model/medication-store';

const props = defineProps<{
  medications: MedicationItem[];
  isSubmitting: boolean;
  error: string | null;
  successMessage: string | null;
}>();

const emit = defineEmits<{
  submit: [
    payload: { medicationId: string; status: AdherenceStatus; deviationNote: string | null },
  ];
}>();
const { t } = useI18n();

const medicationId = ref('');
const status = ref<AdherenceStatus>('taken');
const deviationNote = ref('');

watch(
  () => props.medications,
  (medications) => {
    if (!medications.length) {
      medicationId.value = '';
      return;
    }

    const stillExists = medications.some((item) => item.id === medicationId.value);
    if (!stillExists) {
      medicationId.value = medications[0]!.id;
    }
  },
  { immediate: true }
);

function handleSubmit() {
  if (!medicationId.value) {
    return;
  }

  emit('submit', {
    medicationId: medicationId.value,
    status: status.value,
    deviationNote: deviationNote.value || null,
  });
  deviationNote.value = '';
  status.value = 'taken';
}
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('adherenceForm.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('adherenceForm.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('adherenceForm.subtitle') }}
      </p>
    </div>

    <form
      class="grid gap-3 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm"
      @submit.prevent="handleSubmit"
    >
      <label for="adherence-medication" class="text-sm font-medium text-slate-700">{{
        t('common.medication')
      }}</label>
      <select
        id="adherence-medication"
        v-model="medicationId"
        class="field-input"
        data-testid="adherence-medication-select"
        :disabled="props.isSubmitting || props.medications.length === 0"
      >
        <option disabled value="">{{ t('adherenceForm.selectMedication') }}</option>
        <option v-for="item in props.medications" :key="item.id" :value="item.id">
          {{ item.name }}
        </option>
      </select>

      <label for="adherence-status" class="text-sm font-medium text-slate-700">
        {{ t('common.status') }}
      </label>
      <select
        id="adherence-status"
        v-model="status"
        class="field-input"
        data-testid="adherence-status-select"
        :disabled="props.isSubmitting || props.medications.length === 0"
      >
        <option value="taken">{{ t('statuses.adherence.taken') }}</option>
        <option value="missed">{{ t('statuses.adherence.missed') }}</option>
        <option value="modified">{{ t('statuses.adherence.modified') }}</option>
      </select>

      <label for="adherence-note" class="text-sm font-medium text-slate-700">
        {{ t('adherenceForm.deviationNote') }}
      </label>
      <textarea
        id="adherence-note"
        v-model="deviationNote"
        class="field-input min-h-24"
        :placeholder="t('adherenceForm.notePlaceholder')"
        data-testid="adherence-note-input"
        :disabled="props.isSubmitting || props.medications.length === 0"
      />

      <p v-if="props.error" class="text-sm text-rose-600" data-testid="adherence-form-error">
        {{ props.error }}
      </p>
      <p
        v-else-if="props.successMessage"
        class="text-sm text-emerald-700"
        data-testid="adherence-form-success"
      >
        {{ props.successMessage }}
      </p>

      <div class="flex justify-end">
        <button
          type="submit"
          class="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          data-testid="adherence-submit"
          :disabled="props.isSubmitting || props.medications.length === 0 || !medicationId"
        >
          {{ props.isSubmitting ? t('common.saving') : t('adherenceForm.saveAdherence') }}
        </button>
      </div>
    </form>
  </section>
</template>
