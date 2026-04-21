<script setup lang="ts">
import QuestionnaireForm from '@features/questionnaires/ui/questionnaire-form.vue';
import { useQuestionnaireStore } from '@features/questionnaires/model/questionnaire-store';

definePageMeta({ layout: 'default' });

const route = useRoute();
const questionnaireStore = useQuestionnaireStore();
const authStore = useAuthStore();
const { t } = useI18n();
const localePath = useLocalePath();

const assignmentId = computed(() => String(route.params.assignmentId ?? ''));
const assignment = computed(() =>
  questionnaireStore.pendingItems.find((item) => item.id === assignmentId.value)
);
const pageError = ref<string | null>(null);

async function loadPending() {
  try {
    await questionnaireStore.loadPendingQuestionnaires();
    if (!assignment.value) {
      pageError.value = t('questionnairePage.errors.assignmentUnavailable');
    }
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : t('questionnairePage.errors.loadFailed');
  }
}

async function handleSubmit(answers: Record<string, number>) {
  pageError.value = null;
  try {
    await questionnaireStore.submitQuestionnaire(assignmentId.value, answers);
    await navigateTo(localePath('/dashboard'));
  } catch (err: unknown) {
    pageError.value =
      err instanceof Error ? err.message : t('questionnairePage.errors.submitFailed');
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
      <p class="eyebrow">{{ t('questionnairePage.eyebrow') }}</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">
        {{ t('questionnairePage.title') }}
      </h1>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('questionnairePage.subtitle') }}
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
      :to="localePath('/dashboard')"
      class="inline-flex items-center justify-center rounded-xl bg-slate-200 px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-300"
    >
      {{ t('questionnairePage.backToDashboard') }}
    </NuxtLink>
  </div>
</template>
