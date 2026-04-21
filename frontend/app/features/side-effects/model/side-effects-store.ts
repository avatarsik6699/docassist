import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useNuxtApp } from '#imports';

export type SideEffectSeverity = 'mild' | 'moderate' | 'severe';

export type SideEffectReportItem = {
  id: string;
  severity: SideEffectSeverity;
  symptom: string;
  note: string | null;
  reported_at: string;
};

export type SideEffectCreatePayload = {
  severity: SideEffectSeverity;
  symptom: string;
  note?: string | null;
  medicationId?: string | null;
};

export const useSideEffectsStore = defineStore('side-effects', () => {
  const history = ref<SideEffectReportItem[]>([]);
  const isLoadingHistory = ref(false);
  const isSubmitting = ref(false);
  const error = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadHistory(patientId: string): Promise<SideEffectReportItem[]> {
    isLoadingHistory.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: SideEffectReportItem[] }>(
        `/api/v1/patients/${patientId}/side-effects`
      );
      history.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load side effects.';
      throw err;
    } finally {
      isLoadingHistory.value = false;
    }
  }

  async function submitReport(payload: SideEffectCreatePayload): Promise<SideEffectReportItem> {
    isSubmitting.value = true;
    error.value = null;
    successMessage.value = null;
    try {
      const { $api } = useNuxtApp();
      const created = await $api<SideEffectReportItem>('/api/v1/side-effects', {
        method: 'POST',
        body: {
          severity: payload.severity,
          symptom: payload.symptom.trim(),
          note: payload.note?.trim() || null,
          medication_id: payload.medicationId || null,
        },
      });
      history.value = [created, ...history.value];
      successMessage.value = 'Side effect reported.';
      return created;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to report side effect.';
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
    submitReport,
    clearFeedback,
  };
});
