<script setup lang="ts">
import QuestionnaireForm from '@features/questionnaires/ui/questionnaire-form.vue';
import { useQuestionnaireStore } from '@features/questionnaires/model/questionnaire-store';

definePageMeta({ layout: 'default' });

const route = useRoute();
const questionnaireStore = useQuestionnaireStore();
const authStore = useAuthStore();

const assignmentId = computed(() => String(route.params.assignmentId ?? ''));
const assignment = computed(() =>
  questionnaireStore.pendingItems.find((item) => item.id === assignmentId.value)
);
const pageError = ref<string | null>(null);

async function loadPending() {
  try {
    await questionnaireStore.loadPendingQuestionnaires();
    if (!assignment.value) {
      pageError.value = 'Questionnaire assignment is not available.';
    }
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to load questionnaire.';
  }
}

async function handleSubmit(answers: Record<string, number>) {
  pageError.value = null;
  try {
    await questionnaireStore.submitQuestionnaire(assignmentId.value, answers);
    await navigateTo('/dashboard');
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to submit questionnaire.';
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe();
  }
  await loadPending();
});
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-2">
      <p class="eyebrow">Questionnaire submission</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Complete questionnaire</h1>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        Answer each item using a score from 0 to 3, then submit the form once.
      </p>
    </div>

    <p v-if="pageError" class="text-sm text-rose-600" data-testid="questionnaire-page-error">
      {{ pageError }}
    </p>

    <QuestionnaireForm
      v-if="assignment"
      :questionnaire-code="assignment.questionnaire_code"
      :is-submitting="questionnaireStore.isSubmitting"
      :error="questionnaireStore.error"
      @submit="handleSubmit"
    />

    <NuxtLink
      to="/dashboard"
      class="inline-flex items-center justify-center rounded-xl bg-slate-200 px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-300"
    >
      Back to dashboard
    </NuxtLink>
  </div>
</template>
