import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useNuxtApp } from '#imports';

export type MedicationItem = {
  id: string;
  name: string;
  dosage_instructions: string;
  is_active: boolean;
};

export type MedicationCreatePayload = {
  name: string;
  dosage_instructions: string;
  is_active?: boolean;
};

export const useMedicationStore = defineStore('medications', () => {
  const doctorItems = ref<MedicationItem[]>([]);
  const patientItems = ref<MedicationItem[]>([]);
  const isLoadingDoctorItems = ref(false);
  const isLoadingPatientItems = ref(false);
  const isSubmitting = ref(false);
  const error = ref<string | null>(null);

  async function loadDoctorMedications(patientId: string): Promise<MedicationItem[]> {
    isLoadingDoctorItems.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: MedicationItem[] }>(
        `/api/v1/patients/${patientId}/medications`
      );
      doctorItems.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load medications.';
      throw err;
    } finally {
      isLoadingDoctorItems.value = false;
    }
  }

  async function createMedication(
    patientId: string,
    payload: MedicationCreatePayload
  ): Promise<MedicationItem> {
    isSubmitting.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const created = await $api<MedicationItem>(`/api/v1/patients/${patientId}/medications`, {
        method: 'POST',
        body: payload,
      });
      await loadDoctorMedications(patientId);
      return created;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to save medication.';
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  }

  async function loadCurrentMedications(): Promise<MedicationItem[]> {
    isLoadingPatientItems.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: MedicationItem[] }>('/api/v1/medications/current');
      patientItems.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load medications.';
      throw err;
    } finally {
      isLoadingPatientItems.value = false;
    }
  }

  return {
    doctorItems,
    patientItems,
    isLoadingDoctorItems,
    isLoadingPatientItems,
    isSubmitting,
    error,
    loadDoctorMedications,
    createMedication,
    loadCurrentMedications,
  };
});
