<script setup lang="ts">
import { useAdherenceStore } from '@features/adherence/model/adherence-store';
import type { PatientRosterItem } from '@features/patient-roster/model/patient-roster-store';
import { useMedicationStore } from '@features/medications/model/medication-store';
import DoctorMedicationForm from '@features/medications/ui/doctor-medication-form.vue';
import PatientMedicationList from '@features/medications/ui/patient-medication-list.vue';
import PatientOnboardingForm from '@features/patient-roster/ui/patient-onboarding-form.vue';
import PatientRosterTable from '@features/patient-roster/ui/patient-roster-table.vue';
import { usePatientRosterStore } from '@features/patient-roster/model/patient-roster-store';
import {
  useQuestionnaireStore,
  type QuestionnaireCode,
} from '@features/questionnaires/model/questionnaire-store';
import DoctorQuestionnaireAssignmentForm from '@features/questionnaires/ui/doctor-questionnaire-assignment-form.vue';

definePageMeta({ layout: 'default' });

const authStore = useAuthStore();
const rosterStore = usePatientRosterStore();
const medicationStore = useMedicationStore();
const adherenceStore = useAdherenceStore();
const questionnaireStore = useQuestionnaireStore();

const isDoctor = computed(() => authStore.user?.role === 'doctor');
const pageError = ref<string | null>(null);
const selectedPatientId = ref<string | null>(null);
const selectedPatient = computed<PatientRosterItem | null>(
  () => rosterStore.items.find((item) => item.id === selectedPatientId.value) ?? null
);

async function loadRoster() {
  if (!isDoctor.value) {
    return;
  }

  try {
    const items = await rosterStore.loadPatients();
    if (!selectedPatientId.value || !items.some((item) => item.id === selectedPatientId.value)) {
      selectedPatientId.value = items[0]?.id ?? null;
    }
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to load patients.';
  }
}

async function loadSelectedPatientData() {
  if (!selectedPatientId.value) {
    medicationStore.doctorItems = [];
    adherenceStore.history = [];
    return;
  }

  try {
    await Promise.all([
      medicationStore.loadDoctorMedications(selectedPatientId.value),
      adherenceStore.loadHistory(selectedPatientId.value),
      questionnaireStore.loadDoctorAssignments(selectedPatientId.value),
    ]);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to load patient details.';
  }
}

async function handleCreatePatient(email: string) {
  pageError.value = null;
  try {
    await rosterStore.createPatient(email);
    if (rosterStore.latestCreatedPatient?.id) {
      selectedPatientId.value = rosterStore.latestCreatedPatient.id;
    }
    await loadSelectedPatientData();
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to create patient.';
  }
}

async function handleActivatePatient(patientId: string) {
  pageError.value = null;
  try {
    await rosterStore.activatePatient(patientId);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to activate patient.';
  }
}

async function handleCreateMedication(payload: { name: string; dosage_instructions: string }) {
  if (!selectedPatientId.value) {
    return;
  }

  pageError.value = null;
  try {
    await medicationStore.createMedication(selectedPatientId.value, payload);
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to save medication.';
  }
}

async function handleAssignQuestionnaire(payload: { questionnaireCode: QuestionnaireCode }) {
  if (!selectedPatientId.value) {
    return;
  }

  pageError.value = null;
  try {
    await questionnaireStore.assignQuestionnaire(
      selectedPatientId.value,
      payload.questionnaireCode
    );
  } catch (err: unknown) {
    pageError.value = err instanceof Error ? err.message : 'Unable to assign questionnaire.';
  }
}

watch(selectedPatientId, async () => {
  pageError.value = null;
  if (!isDoctor.value) {
    return;
  }
  await loadSelectedPatientData();
});

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe();
  }

  if (!isDoctor.value) {
    await navigateTo('/dashboard');
    return;
  }

  await loadRoster();
  await loadSelectedPatientData();
});
</script>

<template>
  <div class="space-y-8">
    <div class="space-y-2">
      <p class="eyebrow">Phase 03</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Patient roster</h1>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        Create new patient accounts, manage active medications for assigned patients, and review
        their recent adherence history in one place.
      </p>
    </div>

    <p v-if="pageError" class="text-sm text-rose-600" data-testid="patients-page-error">
      {{ pageError }}
    </p>

    <PatientOnboardingForm
      :is-submitting="rosterStore.isSubmitting"
      :error="rosterStore.error"
      :latest-created-patient="rosterStore.latestCreatedPatient"
      @submit="handleCreatePatient"
      @dismiss-credentials="rosterStore.clearLatestCreatedPatient()"
    />

    <PatientRosterTable
      :items="rosterStore.items"
      :is-loading="rosterStore.isLoading"
      :active-patient-id="rosterStore.activePatientId"
      @activate="handleActivatePatient"
    />

    <section class="space-y-4 rounded-3xl border border-slate-200 bg-white/70 p-5 shadow-sm">
      <div class="space-y-2">
        <p class="eyebrow">Patient context</p>
        <h2 class="text-2xl font-semibold tracking-tight text-slate-950">Selected patient</h2>
        <p class="max-w-2xl text-sm leading-6 text-slate-600">
          Medication assignment and adherence review always apply to the currently selected patient.
        </p>
      </div>

      <label for="patient-selector" class="text-sm font-medium text-slate-700">Patient</label>
      <select
        id="patient-selector"
        v-model="selectedPatientId"
        class="field-input max-w-xl"
        data-testid="doctor-medication-patient-select"
      >
        <option disabled value="">Select patient</option>
        <option v-for="item in rosterStore.items" :key="item.id" :value="item.id">
          {{ item.email }}
        </option>
      </select>
    </section>

    <DoctorMedicationForm
      :patient-email="selectedPatient?.email ?? null"
      :is-submitting="medicationStore.isSubmitting"
      :error="medicationStore.error"
      @submit="handleCreateMedication"
    />

    <DoctorQuestionnaireAssignmentForm
      :patient-email="selectedPatient?.email ?? null"
      :is-submitting="questionnaireStore.isAssigning"
      :error="questionnaireStore.error"
      @submit="handleAssignQuestionnaire"
    />

    <PatientMedicationList
      :items="medicationStore.doctorItems"
      :is-loading="medicationStore.isLoadingDoctorItems"
      empty-message="No active medications are recorded for this patient yet."
    />

    <section class="space-y-4">
      <div class="space-y-2">
        <p class="eyebrow">Questionnaire history</p>
        <h2 class="text-2xl font-semibold tracking-tight text-slate-950">Assignments</h2>
      </div>

      <div
        class="overflow-hidden rounded-3xl border border-slate-200 bg-white/90 shadow-sm"
        data-testid="doctor-questionnaire-history"
      >
        <div v-if="questionnaireStore.isLoadingDoctorItems" class="p-6 text-sm text-slate-500">
          Loading questionnaires…
        </div>
        <div
          v-else-if="questionnaireStore.doctorItems.length === 0"
          class="p-6 text-sm text-slate-500"
          data-testid="doctor-questionnaire-empty"
        >
          No questionnaires assigned yet.
        </div>
        <table v-else class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr>
              <th
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
              >
                Questionnaire
              </th>
              <th
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
              >
                Status
              </th>
              <th
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
              >
                Score
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            <tr v-for="item in questionnaireStore.doctorItems" :key="item.id">
              <td class="px-4 py-4 text-sm font-medium text-slate-900">
                {{ item.questionnaire_code }}
              </td>
              <td class="px-4 py-4 text-sm capitalize text-slate-600">{{ item.status }}</td>
              <td class="px-4 py-4 text-sm text-slate-600">
                <span v-if="item.total_score !== null && item.total_score !== undefined">
                  {{ item.total_score }}
                  <span v-if="item.has_safety_signal" class="ml-2 font-medium text-rose-600">
                    safety flag
                  </span>
                </span>
                <span v-else>Pending</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="space-y-4">
      <div class="space-y-2">
        <p class="eyebrow">Adherence history</p>
        <h2 class="text-2xl font-semibold tracking-tight text-slate-950">Recent logs</h2>
        <p class="max-w-2xl text-sm leading-6 text-slate-600">
          Review the latest patient-reported adherence records as structured entries instead of
          relying on memory during follow-up.
        </p>
      </div>

      <div
        class="overflow-hidden rounded-3xl border border-slate-200 bg-white/90 shadow-sm"
        data-testid="doctor-adherence-history"
      >
        <div v-if="adherenceStore.isLoadingHistory" class="p-6 text-sm text-slate-500">
          Loading adherence history…
        </div>
        <div
          v-else-if="adherenceStore.history.length === 0"
          class="p-6 text-sm text-slate-500"
          data-testid="doctor-adherence-empty"
        >
          No adherence records have been submitted for this patient yet.
        </div>
        <table v-else class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr>
              <th
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
              >
                Time
              </th>
              <th
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
              >
                Status
              </th>
              <th
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
              >
                Note
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            <tr
              v-for="item in adherenceStore.history"
              :key="item.id"
              :data-testid="`adherence-row-${item.id}`"
            >
              <td class="px-4 py-4 text-sm text-slate-600">
                {{ new Date(item.logged_at).toLocaleString() }}
              </td>
              <td class="px-4 py-4 text-sm font-medium capitalize text-slate-900">
                {{ item.status }}
              </td>
              <td class="px-4 py-4 text-sm text-slate-600">
                {{ item.deviation_note || 'No deviation note' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
