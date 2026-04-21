<script setup lang="ts">
import PatientOnboardingForm from '@features/patient-roster/ui/patient-onboarding-form.vue';
import PatientRosterTable from '@features/patient-roster/ui/patient-roster-table.vue';
import { usePatientRosterStore } from '@features/patient-roster/model/patient-roster-store';

definePageMeta({ layout: 'default' });

const authStore = useAuthStore();
const rosterStore = usePatientRosterStore();

const isDoctor = computed(() => authStore.user?.role === 'doctor');
const pageError = ref<string | null>(null);

async function loadRoster() {
  if (!isDoctor.value) {
    return;
  }

  try {
    await rosterStore.loadPatients();
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to load patients.';
  }
}

async function handleCreatePatient(email: string) {
  pageError.value = null;
  try {
    await rosterStore.createPatient(email);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to create patient.';
  }
}

async function handleActivatePatient(patientId: string) {
  pageError.value = null;
  try {
    await rosterStore.activatePatient(patientId);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to activate patient.';
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe();
  }

  if (!isDoctor.value) {
    await navigateTo('/dashboard');
    return;
  }

  await loadRoster();
});
</script>

<template>
  <div class="space-y-8">
    <div class="space-y-2">
      <p class="eyebrow">Phase 02</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Patient roster</h1>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        Create new patient accounts, reveal a one-time temporary password, and reactivate inactive
        patients assigned to the current doctor.
      </p>
    </div>

    <p v-if="pageError" class="text-sm text-rose-600" data-testid="patients-page-error">
      {{ pageError }}
    </p>

    <PatientOnboardingForm
      :is-submitting="rosterStore.isSubmitting"
      :error="rosterStore.error"
      :latest-created-patient="rosterStore.latestCreatedPatient"
      @submit="handleCreatePatient"
      @dismiss-credentials="rosterStore.clearLatestCreatedPatient()"
    />

    <PatientRosterTable
      :items="rosterStore.items"
      :is-loading="rosterStore.isLoading"
      :active-patient-id="rosterStore.activePatientId"
      @activate="handleActivatePatient"
    />
  </div>
</template>
