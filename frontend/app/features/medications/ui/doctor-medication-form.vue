<script setup lang="ts">
const props = defineProps<{
  patientEmail: string | null;
  isSubmitting: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  submit: [payload: { name: string; dosage_instructions: string }];
}>();
const { t } = useI18n();

const name = ref('');
const dosageInstructions = ref('');

function handleSubmit() {
  const normalizedName = name.value.trim();
  const normalizedDosage = dosageInstructions.value.trim();

  if (!normalizedName || !normalizedDosage || !props.patientEmail) {
    return;
  }

  emit('submit', {
    name: normalizedName,
    dosage_instructions: normalizedDosage,
  });

  name.value = '';
  dosageInstructions.value = '';
}
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('doctorMedicationForm.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('doctorMedicationForm.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('doctorMedicationForm.subtitle') }}
      </p>
    </div>

    <form
      class="grid gap-3 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm"
      @submit.prevent="handleSubmit"
    >
      <div
        class="rounded-2xl bg-slate-50 p-3 text-sm text-slate-600"
        data-testid="selected-patient-banner"
      >
        <span v-if="props.patientEmail">
          {{ t('doctorMedicationForm.managingFor', { email: props.patientEmail }) }}
        </span>
        <span v-else>{{ t('doctorMedicationForm.selectPatientFirst') }}</span>
      </div>

      <label for="medication-name" class="text-sm font-medium text-slate-700">{{
        t('doctorMedicationForm.medicationName')
      }}</label>
      <input
        id="medication-name"
        v-model="name"
        type="text"
        class="field-input"
        placeholder="Sertraline"
        data-testid="medication-name-input"
        :disabled="props.isSubmitting || !props.patientEmail"
        required
      />

      <label for="medication-dosage" class="text-sm font-medium text-slate-700">
        {{ t('doctorMedicationForm.dosageInstructions') }}
      </label>
      <textarea
        id="medication-dosage"
        v-model="dosageInstructions"
        class="field-input min-h-28"
        placeholder="50 mg once daily"
        data-testid="medication-dosage-input"
        :disabled="props.isSubmitting || !props.patientEmail"
        required
      />

      <p
        v-if="props.error"
        class="text-sm text-rose-600"
        data-testid="doctor-medication-form-error"
      >
        {{ props.error }}
      </p>

      <div class="flex justify-end">
        <button
          type="submit"
          class="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          data-testid="create-medication-submit"
          :disabled="props.isSubmitting || !props.patientEmail"
        >
          {{ props.isSubmitting ? t('common.saving') : t('doctorMedicationForm.saveMedication') }}
        </button>
      </div>
    </form>
  </section>
</template>
