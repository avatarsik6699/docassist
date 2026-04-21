<script setup lang="ts">
import type { MedicationItem } from '@features/medications/model/medication-store';

const props = defineProps<{
  items: MedicationItem[];
  isLoading: boolean;
  emptyMessage: string;
}>();
const { t } = useI18n();
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('medicationList.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('medicationList.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('medicationList.subtitle') }}
      </p>
    </div>

    <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white/90 shadow-sm">
      <div v-if="props.isLoading" class="p-6 text-sm text-slate-500">
        {{ t('medicationList.loading') }}
      </div>

      <div
        v-else-if="props.items.length === 0"
        class="p-6 text-sm text-slate-500"
        data-testid="medications-empty"
      >
        {{ props.emptyMessage }}
      </div>

      <ul v-else class="divide-y divide-slate-200" data-testid="patient-medication-list">
        <li
          v-for="item in props.items"
          :key="item.id"
          class="grid gap-3 px-5 py-4 md:grid-cols-[minmax(0,220px)_1fr]"
        >
          <div>
            <p class="text-sm font-semibold text-slate-950">{{ item.name }}</p>
            <p class="mt-1 text-xs uppercase tracking-[0.18em] text-emerald-700">
              {{ t('common.active') }}
            </p>
          </div>
          <p class="text-sm leading-6 text-slate-600">{{ item.dosage_instructions }}</p>
        </li>
      </ul>
    </div>
  </section>
</template>
