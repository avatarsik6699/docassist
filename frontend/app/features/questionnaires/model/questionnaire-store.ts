import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useNuxtApp } from '#imports';

export type QuestionnaireCode = 'PHQ-9' | 'GAD-7';
export type QuestionnaireStatus = 'assigned' | 'completed';

export type QuestionnaireAssignmentItem = {
  id: string;
  questionnaire_code: QuestionnaireCode;
  status: QuestionnaireStatus;
  assigned_at: string;
  completed_at: string | null;
  total_score?: number | null;
  has_safety_signal?: boolean | null;
};

export type PendingQuestionnaireItem = {
  id: string;
  questionnaire_code: QuestionnaireCode;
  status: 'assigned';
  assigned_at: string;
};

export type QuestionnaireSubmissionResult = {
  id: string;
  assignment_id: string;
  questionnaire_code: QuestionnaireCode;
  total_score: number;
  has_safety_signal: boolean;
  submitted_at: string;
};

export const useQuestionnaireStore = defineStore('questionnaires', () => {
  const doctorItems = ref<QuestionnaireAssignmentItem[]>([]);
  const pendingItems = ref<PendingQuestionnaireItem[]>([]);
  const isLoadingDoctorItems = ref(false);
  const isLoadingPendingItems = ref(false);
  const isAssigning = ref(false);
  const isSubmitting = ref(false);
  const error = ref<string | null>(null);
  const submissionResult = ref<QuestionnaireSubmissionResult | null>(null);

  async function loadDoctorAssignments(patientId: string): Promise<QuestionnaireAssignmentItem[]> {
    isLoadingDoctorItems.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: QuestionnaireAssignmentItem[] }>(
        `/api/v1/patients/${patientId}/questionnaires`
      );
      doctorItems.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load questionnaires.';
      throw err;
    } finally {
      isLoadingDoctorItems.value = false;
    }
  }

  async function assignQuestionnaire(
    patientId: string,
    questionnaireCode: QuestionnaireCode
  ): Promise<QuestionnaireAssignmentItem> {
    isAssigning.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const created = await $api<QuestionnaireAssignmentItem>(
        `/api/v1/patients/${patientId}/questionnaires`,
        {
          method: 'POST',
          body: {
            questionnaire_code: questionnaireCode,
          },
        }
      );
      await loadDoctorAssignments(patientId);
      return created;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to assign questionnaire.';
      throw err;
    } finally {
      isAssigning.value = false;
    }
  }

  async function loadPendingQuestionnaires(): Promise<PendingQuestionnaireItem[]> {
    isLoadingPendingItems.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ items: PendingQuestionnaireItem[] }>(
        '/api/v1/questionnaires/pending'
      );
      pendingItems.value = data.items;
      return data.items;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to load pending questionnaires.';
      throw err;
    } finally {
      isLoadingPendingItems.value = false;
    }
  }

  async function submitQuestionnaire(
    assignmentId: string,
    answers: Record<string, number>
  ): Promise<QuestionnaireSubmissionResult> {
    isSubmitting.value = true;
    error.value = null;
    submissionResult.value = null;
    try {
      const { $api } = useNuxtApp();
      const result = await $api<QuestionnaireSubmissionResult>(
        `/api/v1/questionnaires/${assignmentId}/submit`,
        {
          method: 'POST',
          body: { answers },
        }
      );
      submissionResult.value = result;
      pendingItems.value = pendingItems.value.filter((item) => item.id !== assignmentId);
      return result;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unable to submit questionnaire.';
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  }

  function clearFeedback(): void {
    error.value = null;
    submissionResult.value = null;
  }

  return {
    doctorItems,
    pendingItems,
    isLoadingDoctorItems,
    isLoadingPendingItems,
    isAssigning,
    isSubmitting,
    error,
    submissionResult,
    loadDoctorAssignments,
    assignQuestionnaire,
    loadPendingQuestionnaires,
    submitQuestionnaire,
    clearFeedback,
  };
});
