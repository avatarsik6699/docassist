<script setup lang="ts">
import type {
  PatientSummary,
  PatientSafetyFlag,
} from '@features/patient-summary/model/patient-summary-store';
import type { SideEffectReportItem } from '@features/side-effects/model/side-effects-store';

const props = defineProps<{
  summary: PatientSummary | null;
  sideEffectsHistory: SideEffectReportItem[];
  isLoading: boolean;
}>();

function flagLabel(flag: PatientSafetyFlag): string {
  if (flag.code === 'questionnaire_safety_signal') {
    return 'Questionnaire safety signal';
  }
  if (flag.code === 'severe_side_effect_reported') {
    return 'Severe side effect reported';
  }
  return flag.code;
}
</script>

<template>
  <section
    class="space-y-5 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm"
    data-testid="patient-summary-panel"
  >
    <div class="space-y-2">
      <p class="eyebrow">Phase 05</p>
      <h2 class="text-2xl font-semibold tracking-tight text-slate-950">Recent patient summary</h2>
      <p class="max-w-3xl text-sm leading-6 text-slate-600">
        One review surface for recent questionnaires, adherence, and side effects with explicit
        safety highlighting.
      </p>
    </div>

    <div v-if="props.isLoading" class="text-sm text-slate-500">Loading patient summary…</div>

    <template v-else-if="props.summary">
      <div class="space-y-3" data-testid="patient-summary-safety-flags">
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Safety flags</p>
        <div
          v-if="props.summary.safety_flags.length === 0"
          class="rounded-2xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700"
        >
          No active safety flags from recent history.
        </div>
        <div v-else class="grid gap-2 sm:grid-cols-2">
          <div
            v-for="flag in props.summary.safety_flags"
            :key="`${flag.source}-${flag.code}`"
            class="rounded-2xl border px-3 py-2 text-sm"
            :class="
              flag.level === 'critical'
                ? 'border-rose-300 bg-rose-50 text-rose-700'
                : 'border-amber-300 bg-amber-50 text-amber-700'
            "
          >
            <p class="font-semibold uppercase tracking-wide">{{ flag.level }}</p>
            <p>{{ flagLabel(flag) }}</p>
          </div>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-3">
        <article class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Questionnaires
          </p>
          <p v-if="props.summary.questionnaires.length === 0" class="mt-2 text-sm text-slate-500">
            No submissions yet.
          </p>
          <ul v-else class="mt-2 space-y-2 text-sm text-slate-700">
            <li
              v-for="item in props.summary.questionnaires"
              :key="item.assignment_id"
              class="rounded-xl bg-white px-3 py-2"
            >
              <p class="font-medium text-slate-900">
                {{ item.questionnaire_code }} · score {{ item.total_score }}
              </p>
              <p v-if="item.has_safety_signal" class="text-rose-600">Safety signal</p>
            </li>
          </ul>
        </article>

        <article class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Adherence</p>
          <p v-if="props.summary.adherence.length === 0" class="mt-2 text-sm text-slate-500">
            No adherence logs yet.
          </p>
          <ul v-else class="mt-2 space-y-2 text-sm text-slate-700">
            <li
              v-for="item in props.summary.adherence"
              :key="item.id"
              class="rounded-xl bg-white px-3 py-2"
            >
              <p class="font-medium capitalize text-slate-900">{{ item.status }}</p>
              <p class="text-xs text-slate-500">Medication: {{ item.medication_id }}</p>
            </li>
          </ul>
        </article>

        <article class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Side effects
          </p>
          <p v-if="props.sideEffectsHistory.length === 0" class="mt-2 text-sm text-slate-500">
            No side effects reported.
          </p>
          <ul v-else class="mt-2 space-y-2 text-sm text-slate-700">
            <li
              v-for="item in props.sideEffectsHistory"
              :key="item.id"
              class="rounded-xl bg-white px-3 py-2"
            >
              <p class="font-medium text-slate-900">{{ item.symptom }}</p>
              <p
                class="capitalize"
                :class="item.severity === 'severe' ? 'text-rose-600' : 'text-slate-600'"
              >
                {{ item.severity }}
              </p>
              <p v-if="item.note" class="text-xs text-slate-500">{{ item.note }}</p>
            </li>
          </ul>
        </article>
      </div>
    </template>
  </section>
</template>
