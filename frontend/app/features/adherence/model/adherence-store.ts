import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useNuxtApp } from '#imports';

export type AdherenceStatus = 'taken' | 'missed' | 'modified';

export type AdherenceLogItem = {
  id: string;
  medication_id: string;
  status: AdherenceStatus;
  deviation_note: string | null;
  logged_at: string;
};

export type CreateAdherencePayload = {
  medicationId: string;
  status: AdherenceStatus;
  deviationNote?: string | null;
};

export const useAdherenceStore = defineStore('adherence', () => {
  const history = ref<AdherenceLogItem[]>([]);
  const isLoadingHistory = ref(false);
  const isSubmitting = ref(false);
  const error = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadHistory(patientId: string): Promise<AdherenceLogItem[]> {
    isLoadingHistory.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: AdherenceLogItem[] }>(
        `/api/v1/patients/${patientId}/adherence`
      );
      history.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load adherence history.';
      throw err;
    } finally {
      isLoadingHistory.value = false;
    }
  }

  async function submitLog(payload: CreateAdherencePayload): Promise<AdherenceLogItem> {
    isSubmitting.value = true;
    error.value = null;
    successMessage.value = null;
    try {
      const { $api } = useNuxtApp();
      const created = await $api<AdherenceLogItem>(
        `/api/v1/medications/${payload.medicationId}/adherence`,
        {
          method: 'POST',
          body: {
            status: payload.status,
            deviation_note: payload.deviationNote?.trim() || null,
          },
        }
      );
      history.value = [created, ...history.value];
      successMessage.value = 'Adherence saved.';
      return created;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to save adherence.';
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  }

  function clearFeedback(): void {
    error.value = null;
    successMessage.value = null;
  }

  return {
    history,
    isLoadingHistory,
    isSubmitting,
    error,
    successMessage,
    loadHistory,
    submitLog,
    clearFeedback,
  };
});
