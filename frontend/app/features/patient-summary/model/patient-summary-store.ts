import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useNuxtApp } from '#imports';

export type PatientQuestionnaireSummary = {
  assignment_id: string;
  questionnaire_code: 'PHQ-9' | 'GAD-7';
  total_score: number;
  has_safety_signal: boolean;
  submitted_at: string;
};

export type PatientAdherenceSummary = {
  id: string;
  medication_id: string;
  status: 'taken' | 'missed' | 'modified';
  logged_at: string;
};

export type PatientSummarySideEffect = {
  id: string;
  severity: 'mild' | 'moderate' | 'severe';
  symptom: string;
  reported_at: string;
};

export type PatientSafetyFlag = {
  source: 'questionnaire' | 'side_effect';
  level: 'critical' | 'warning';
  code: string;
};

export type PatientSummary = {
  patient_id: string;
  questionnaires: PatientQuestionnaireSummary[];
  adherence: PatientAdherenceSummary[];
  side_effects: PatientSummarySideEffect[];
  safety_flags: PatientSafetyFlag[];
};

export const usePatientSummaryStore = defineStore('patient-summary', () => {
  const summary = ref<PatientSummary | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  async function loadSummary(patientId: string): Promise<PatientSummary> {
    isLoading.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<PatientSummary>(`/api/v1/patients/${patientId}/summary`);
      summary.value = data;
      return data;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load patient summary.';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearSummary(): void {
    summary.value = null;
    error.value = null;
  }

  return {
    summary,
    isLoading,
    error,
    loadSummary,
    clearSummary,
  };
});
