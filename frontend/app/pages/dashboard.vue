<script setup lang="ts">
import { useAdherenceStore } from '@features/adherence/model/adherence-store';
import AdherenceLogForm from '@features/adherence/ui/adherence-log-form.vue';
import { useAuthStore } from '@features/auth/model/auth-store';
import { useMedicationStore } from '@features/medications/model/medication-store';
import PatientMedicationList from '@features/medications/ui/patient-medication-list.vue';
import { useQuestionnaireStore } from '@features/questionnaires/model/questionnaire-store';
import PatientQuestionnaireList from '@features/questionnaires/ui/patient-questionnaire-list.vue';
import { useSideEffectsStore } from '@features/side-effects/model/side-effects-store';
import SideEffectReportForm from '@features/side-effects/ui/side-effect-report-form.vue';

definePageMeta({ layout: 'default' });

const authStore = useAuthStore();
const medicationStore = useMedicationStore();
const adherenceStore = useAdherenceStore();
const questionnaireStore = useQuestionnaireStore();
const sideEffectsStore = useSideEffectsStore();
const isDoctor = computed(() => authStore.user?.role === 'doctor');
const isPatient = computed(() => authStore.user?.role === 'patient');
const pageError = ref<string | null>(null);

async function loadPatientData() {
  if (!isPatient.value || authStore.requiresAccountSetup) {
    return;
  }

  try {
    await Promise.all([
      medicationStore.loadCurrentMedications(),
      questionnaireStore.loadPendingQuestionnaires(),
    ]);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to load patient dashboard data.';
  }
}

async function handleSubmitAdherence(payload: {
  medicationId: string;
  status: 'taken' | 'missed' | 'modified';
  deviationNote: string | null;
}) {
  pageError.value = null;
  try {
    await adherenceStore.submitLog(payload);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to save adherence.';
  }
}

async function handleSubmitSideEffect(payload: {
  medicationId: string | null;
  severity: 'mild' | 'moderate' | 'severe';
  symptom: string;
  note: string | null;
}) {
  pageError.value = null;
  try {
    await sideEffectsStore.submitReport(payload);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to report side effect.';
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe();
  }

  await loadPatientData();
});
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-2">
      <p class="eyebrow">Phase 03</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Dashboard</h1>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        Medication tracking extends the authenticated shell with a shared record: doctors assign
        active medications, and patients log whether each medication was actually taken.
      </p>
    </div>

    <p v-if="pageError" class="text-sm text-rose-600" data-testid="dashboard-page-error">
      {{ pageError }}
    </p>

    <UCard data-testid="dashboard-shell" class="shadow-sm ring-1 ring-slate-200/80">
      <template #header>
        <div class="flex items-center justify-between gap-4">
          <div>
            <h3 class="text-lg font-semibold text-slate-950">Current session</h3>
            <p class="text-sm text-slate-500">Server-validated identity from `/auth/me`</p>
          </div>
          <div class="flex items-center gap-3">
            <UBadge color="primary" variant="subtle">
              {{ authStore.user?.role ?? 'unknown' }}
            </UBadge>
            <NuxtLink
              to="/logout"
              data-testid="logout-button"
              class="inline-flex items-center justify-center rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
            >
              Log out
            </NuxtLink>
          </div>
        </div>
      </template>

      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">Email</p>
          <p class="mt-2 text-sm font-medium text-slate-900">{{ authStore.user?.email }}</p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">Role</p>
          <p class="mt-2 text-sm font-medium capitalize text-slate-900">
            {{ authStore.user?.role }}
          </p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">Status</p>
          <p class="mt-2 text-sm font-medium text-emerald-700">
            {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
          </p>
        </div>
      </div>
    </UCard>

    <UCard
      v-if="isDoctor"
      class="shadow-sm ring-1 ring-slate-200/80"
      data-testid="doctor-dashboard-card"
    >
      <template #header>
        <div>
          <h3 class="text-lg font-semibold text-slate-950">Doctor workflow</h3>
          <p class="text-sm text-slate-500">
            Open the roster to manage patient access, assign medications, and review adherence.
          </p>
        </div>
      </template>

      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <p class="max-w-2xl text-sm leading-6 text-slate-600">
          The roster now acts as the doctor workspace for onboarding, medication assignment, and
          recent adherence review.
        </p>
        <NuxtLink
          to="/patients"
          class="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
          data-testid="open-patients-link"
        >
          Open patient roster
        </NuxtLink>
      </div>
    </UCard>

    <UCard
      v-if="isPatient"
      class="shadow-sm ring-1 ring-slate-200/80"
      data-testid="patient-dashboard-card"
    >
      <template #header>
        <div>
          <h3 class="text-lg font-semibold text-slate-950">Patient access</h3>
          <p class="text-sm text-slate-500">Your account is linked to one doctor for MVP.</p>
        </div>
      </template>

      <div class="space-y-4">
        <p class="text-sm leading-6 text-slate-600">
          {{
            authStore.requiresAccountSetup
              ? 'Your first-login setup is still pending. Finish it before accessing the rest of the app.'
              : 'Your onboarding is complete. Your current medication list is shown below, and you can log adherence directly from this dashboard.'
          }}
        </p>
        <NuxtLink
          v-if="authStore.requiresAccountSetup"
          to="/setup-account"
          class="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
        >
          Finish account setup
        </NuxtLink>
      </div>
    </UCard>

    <template v-if="isPatient && !authStore.requiresAccountSetup">
      <PatientQuestionnaireList
        :items="questionnaireStore.pendingItems"
        :is-loading="questionnaireStore.isLoadingPendingItems"
      />

      <PatientMedicationList
        :items="medicationStore.patientItems"
        :is-loading="medicationStore.isLoadingPatientItems"
        empty-message="No active medications have been assigned yet."
      />

      <AdherenceLogForm
        :medications="medicationStore.patientItems"
        :is-submitting="adherenceStore.isSubmitting"
        :error="adherenceStore.error"
        :success-message="adherenceStore.successMessage"
        @submit="handleSubmitAdherence"
      />

      <SideEffectReportForm
        :medications="medicationStore.patientItems"
        :is-submitting="sideEffectsStore.isSubmitting"
        :error="sideEffectsStore.error"
        :success-message="sideEffectsStore.successMessage"
        @submit="handleSubmitSideEffect"
      />
    </template>
  </div>
</template>
