import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useNuxtApp } from '#imports';

export type PatientOnboardingStatus = 'pending' | 'completed';

export type PatientRosterItem = {
  id: string;
  email: string;
  is_active: boolean;
  onboarding_status: PatientOnboardingStatus;
};

export type CreatePatientResult = {
  id: string;
  email: string;
  doctor_user_id: string;
  onboarding_status: 'pending';
  temporary_password: string;
};

export const usePatientRosterStore = defineStore('patient-roster', () => {
  const items = ref<PatientRosterItem[]>([]);
  const latestCreatedPatient = ref<CreatePatientResult | null>(null);
  const isLoading = ref(false);
  const isSubmitting = ref(false);
  const activePatientId = ref<string | null>(null);
  const error = ref<string | null>(null);

  async function loadPatients(): Promise<PatientRosterItem[]> {
    isLoading.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: PatientRosterItem[] }>('/api/v1/patients');
      items.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load patients.';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createPatient(email: string): Promise<CreatePatientResult> {
    isSubmitting.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const created = await $api<CreatePatientResult>('/api/v1/patients', {
        method: 'POST',
        body: {
          email,
        },
      });
      latestCreatedPatient.value = created;
      await loadPatients();
      return created;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to create patient.';
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  }

  async function activatePatient(patientId: string): Promise<void> {
    activePatientId.value = patientId;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      await $api(`/api/v1/patients/${patientId}/activate`, {
        method: 'POST',
      });
      await loadPatients();
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to activate patient.';
      throw err;
    } finally {
      activePatientId.value = null;
    }
  }

  function clearLatestCreatedPatient(): void {
    latestCreatedPatient.value = null;
  }

  return {
    items,
    latestCreatedPatient,
    isLoading,
    isSubmitting,
    activePatientId,
    error,
    loadPatients,
    createPatient,
    activatePatient,
    clearLatestCreatedPatient,
  };
});
