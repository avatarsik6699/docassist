<script setup lang="ts">
import { useAuthStore } from '@features/auth/model/auth-store';

definePageMeta({ layout: 'default' });

const authStore = useAuthStore();

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
        Phase 01 now provides working JWT auth, role-aware users, and a stable shell for later
        doctor-patient workflows.
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
  </div>
</template>
