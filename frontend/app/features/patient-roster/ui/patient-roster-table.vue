<script setup lang="ts">
import type { PatientRosterItem } from '@features/patient-roster/model/patient-roster-store';

const props = defineProps<{
  items: PatientRosterItem[];
  isLoading: boolean;
  activePatientId: string | null;
}>();

const emit = defineEmits<{
  activate: [patientId: string];
}>();
const { t } = useI18n();
</script>

<template>
  <section class="space-y-4">
    <div class="space-y-2">
      <p class="eyebrow">{{ t('patientRosterTable.eyebrow') }}</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">
        {{ t('patientRosterTable.title') }}
      </h2>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        {{ t('patientRosterTable.subtitle') }}
      </p>
    </div>

    <div class="overflow-x-auto rounded-3xl border border-slate-200 bg-white/90 shadow-sm">
      <div v-if="props.isLoading" class="p-6 text-sm text-slate-500" data-testid="patients-loading">
        {{ t('patientRosterTable.loading') }}
      </div>

      <div
        v-else-if="props.items.length === 0"
        class="p-6 text-sm text-slate-500"
        data-testid="patients-empty"
      >
        {{ t('patientRosterTable.empty') }}
      </div>

      <table v-else class="min-w-full divide-y divide-slate-200" data-testid="patients-table">
        <thead class="bg-slate-50">
          <tr>
            <th
              class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
            >
              {{ t('common.email') }}
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
            >
              {{ t('common.status') }}
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
            >
              {{ t('patientRosterTable.onboarding') }}
            </th>
            <th
              class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
            >
              {{ t('common.action') }}
            </th>
          </tr>
        </thead>

        <tbody class="divide-y divide-slate-200">
          <tr
            v-for="item in props.items"
            :key="item.id"
            class="align-top"
            :data-testid="`patient-row-${item.id}`"
          >
            <td class="px-4 py-4 text-sm font-medium text-slate-900">{{ item.email }}</td>
            <td class="px-4 py-4 text-sm">
              <span
                class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
                :class="
                  item.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'
                "
              >
                {{ item.is_active ? t('common.active') : t('common.inactive') }}
              </span>
            </td>
            <td class="px-4 py-4 text-sm text-slate-600 capitalize">
              {{ item.onboarding_status }}
            </td>
            <td class="px-4 py-4 text-right">
              <button
                v-if="!item.is_active"
                type="button"
                class="rounded-2xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:opacity-50"
                :disabled="props.activePatientId === item.id"
                :data-testid="`activate-patient-${item.id}`"
                @click="emit('activate', item.id)"
              >
                {{
                  props.activePatientId === item.id
                    ? t('patientRosterTable.activating')
                    : t('patientRosterTable.activate')
                }}
              </button>
              <span v-else class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
                {{ t('patientRosterTable.live') }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
