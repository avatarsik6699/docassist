<script setup lang="ts">
import { useAuthStore } from '@features/auth/model/auth-store';

definePageMeta({ layout: 'default' });

const authStore = useAuthStore();
const isDoctor = computed(() => authStore.user?.role === 'doctor');
const isPatient = computed(() => authStore.user?.role === 'patient');

async function handleLogout() {
  await authStore.logout();
}
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-2">
      <p class="eyebrow">Authenticated Area</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Dashboard</h1>
      <p class="max-w-2xl text-sm leading-6 text-slate-600">
        Phase 02 turns the shell into a real onboarding hub: doctors can manage patient access, and
        patient sessions are guided through first-login setup.
      </p>
    </div>

    <UCard data-testid="dashboard-shell" class="shadow-sm ring-1 ring-slate-200/80">
      <template #header>
        <div class="flex items-center justify-between gap-4">
          <div>
            <h3 class="text-lg font-semibold text-slate-950">Current session</h3>
            <p class="text-sm text-slate-500">Server-validated identity from `/auth/me`</p>
          </div>
          <div class="flex items-center gap-3">
            <UBadge color="primary" variant="subtle">
              {{ authStore.user?.role ?? 'unknown' }}
            </UBadge>
            <UButton
              color="neutral"
              variant="soft"
              data-testid="logout-button"
              @click="handleLogout"
            >
              Log out
            </UButton>
          </div>
        </div>
      </template>

      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">Email</p>
          <p class="mt-2 text-sm font-medium text-slate-900">{{ authStore.user?.email }}</p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">Role</p>
          <p class="mt-2 text-sm font-medium capitalize text-slate-900">
            {{ authStore.user?.role }}
          </p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">Status</p>
          <p class="mt-2 text-sm font-medium text-emerald-700">
            {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
          </p>
        </div>
      </div>
    </UCard>

    <UCard
      v-if="isDoctor"
      class="shadow-sm ring-1 ring-slate-200/80"
      data-testid="doctor-dashboard-card"
    >
      <template #header>
        <div>
          <h3 class="text-lg font-semibold text-slate-950">Doctor workflow</h3>
          <p class="text-sm text-slate-500">
            Open the roster to create or reactivate patient access.
          </p>
        </div>
      </template>

      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <p class="max-w-2xl text-sm leading-6 text-slate-600">
          The roster is now the control point for doctor-managed onboarding in MVP.
        </p>
        <NuxtLink
          to="/patients"
          class="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
          data-testid="open-patients-link"
        >
          Open patient roster
        </NuxtLink>
      </div>
    </UCard>

    <UCard
      v-if="isPatient"
      class="shadow-sm ring-1 ring-slate-200/80"
      data-testid="patient-dashboard-card"
    >
      <template #header>
        <div>
          <h3 class="text-lg font-semibold text-slate-950">Patient access</h3>
          <p class="text-sm text-slate-500">Your account is linked to one doctor for MVP.</p>
        </div>
      </template>

      <div class="space-y-4">
        <p class="text-sm leading-6 text-slate-600">
          {{
            authStore.requiresAccountSetup
              ? 'Your first-login setup is still pending. Finish it before accessing the rest of the app.'
              : 'Your onboarding is complete. Later phases will unlock medication, questionnaires, and reporting here.'
          }}
        </p>
        <NuxtLink
          v-if="authStore.requiresAccountSetup"
          to="/setup-account"
          class="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
        >
          Finish account setup
        </NuxtLink>
      </div>
    </UCard>
  </div>
</template>
