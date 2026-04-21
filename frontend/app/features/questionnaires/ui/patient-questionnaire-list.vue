<script setup lang="ts">
import type { PendingQuestionnaireItem } from '@features/questionnaires/model/questionnaire-store';

const props = defineProps<{
  items: PendingQuestionnaireItem[];
  isLoading: boolean;
}>();
const { t, locale } = useI18n();
const dateTimeLocale = computed(() => (locale.value === 'ru' ? 'ru-RU' : 'en-US'));

function formatAssignedDate(value: string): string {
  return new Date(value).toLocaleString(dateTimeLocale.value);
}
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('patientQuestionnaireList.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('patientQuestionnaireList.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('patientQuestionnaireList.subtitle') }}
      </p>
    </div>

    <div
      class="overflow-hidden rounded-3xl border border-slate-200 bg-white/90 shadow-sm"
      data-testid="patient-questionnaire-list"
    >
      <div v-if="props.isLoading" class="p-6 text-sm text-slate-500">
        {{ t('patientQuestionnaireList.loading') }}
      </div>
      <div
        v-else-if="props.items.length === 0"
        class="p-6 text-sm text-slate-500"
        data-testid="patient-questionnaire-empty"
      >
        {{ t('patientQuestionnaireList.empty') }}
      </div>
      <ul v-else class="divide-y divide-slate-200">
        <li
          v-for="item in props.items"
          :key="item.id"
          class="flex flex-col gap-3 p-5 md:flex-row md:items-center md:justify-between"
          :data-testid="`pending-questionnaire-${item.id}`"
        >
          <div class="space-y-1">
            <p class="text-sm font-semibold text-slate-900">{{ item.questionnaire_code }}</p>
            <p class="text-xs uppercase tracking-[0.12em] text-slate-500">
              {{ t('patientQuestionnaireList.assignedAt') }}
              {{ formatAssignedDate(item.assigned_at) }}
            </p>
          </div>
          <NuxtLink
            :to="`/questionnaires/${item.id}`"
            class="inline-flex items-center justify-center rounded-xl bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
            data-testid="open-questionnaire-link"
          >
            {{ t('patientQuestionnaireList.start') }}
          </NuxtLink>
        </li>
      </ul>
    </div>
  </section>
</template>
