<script setup lang="ts">
import type { CreatePatientResult } from '@features/patient-roster/model/patient-roster-store';

const props = defineProps<{
  isSubmitting: boolean;
  error: string | null;
  latestCreatedPatient: CreatePatientResult | null;
}>();

const emit = defineEmits<{
  submit: [email: string];
  dismissCredentials: [];
}>();
const { t } = useI18n();

const email = ref('');

function handleSubmit() {
  const normalizedEmail = email.value.trim().toLowerCase();
  if (!normalizedEmail) {
    return;
  }

  emit('submit', normalizedEmail);
  email.value = '';
}
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('patientOnboarding.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('patientOnboarding.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('patientOnboarding.subtitle') }}
      </p>
    </div>

    <form
      class="grid gap-3 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm"
      @submit.prevent="handleSubmit"
    >
      <label for="patient-email" class="text-sm font-medium text-slate-700">
        {{ t('patientOnboarding.patientEmail') }}
      </label>
      <input
        id="patient-email"
        v-model="email"
        type="email"
        class="field-input"
        placeholder="patient@example.com"
        autocomplete="email"
        data-testid="patient-email-input"
        :disabled="props.isSubmitting"
        required
      />

      <p v-if="props.error" class="text-sm text-rose-600" data-testid="patient-form-error">
        {{ props.error }}
      </p>

      <div class="flex items-center justify-between gap-3">
        <p class="text-xs text-slate-500">{{ t('patientOnboarding.temporaryPasswordHint') }}</p>
        <button
          type="submit"
          class="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          :disabled="props.isSubmitting"
          data-testid="create-patient-submit"
        >
          {{
            props.isSubmitting
              ? t('patientOnboarding.creating')
              : t('patientOnboarding.createPatient')
          }}
        </button>
      </div>
    </form>

    <div
      v-if="props.latestCreatedPatient"
      class="space-y-3 rounded-3xl border border-amber-200 bg-amber-50/80 p-5"
      data-testid="temporary-password-card"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-semibold text-amber-950">
            {{ t('patientOnboarding.temporaryPassword') }}
          </p>
          <p class="mt-1 text-sm text-amber-900">
            {{
              t('patientOnboarding.credentialsHelp', { email: props.latestCreatedPatient.email })
            }}
          </p>
        </div>
        <button
          type="button"
          class="text-sm font-medium text-amber-900 underline underline-offset-4"
          @click="emit('dismissCredentials')"
        >
          {{ t('common.dismiss') }}
        </button>
      </div>

      <div class="grid gap-3 md:grid-cols-2">
        <div class="rounded-2xl bg-white/70 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-amber-700">{{ t('common.email') }}</p>
          <p class="mt-2 text-sm font-medium text-slate-900">
            {{ props.latestCreatedPatient.email }}
          </p>
        </div>
        <div class="rounded-2xl bg-white/70 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-amber-700">
            {{ t('common.password') }}
          </p>
          <p class="mt-2 font-mono text-sm text-slate-900" data-testid="temporary-password-value">
            {{ props.latestCreatedPatient.temporary_password }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
