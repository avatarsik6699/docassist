<script setup lang="ts">
definePageMeta({ layout: 'default' });

const authStore = useAuthStore();

const isHydrated = ref(false);
const newPassword = ref('');
const confirmPassword = ref('');
const errorMsg = ref<string | null>(null);
const isSaving = ref(false);

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe();
  }

  if (authStore.user?.role !== 'patient' || !authStore.requiresAccountSetup) {
    await navigateTo('/dashboard');
  }

  isHydrated.value = true;
});

async function handleSubmit() {
  if (newPassword.value.length < 8) {
    errorMsg.value = 'Use at least 8 characters.';
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Passwords must match.';
    return;
  }

  isSaving.value = true;
  errorMsg.value = null;

  try {
    await authStore.setupAccount(newPassword.value);
    await navigateTo('/dashboard', { replace: true });
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Unable to save password.';
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <div class="space-y-2">
      <p class="eyebrow">Patient Setup</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Set a permanent password</h1>
      <p class="text-sm leading-6 text-slate-600">
        This one-time step finishes onboarding for {{ authStore.user?.email ?? 'your account' }}.
      </p>
    </div>

    <section class="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-sm">
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div>
          <label for="new-password" class="mb-1 block text-sm font-medium text-slate-700">
            New password
          </label>
          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            class="field-input"
            autocomplete="new-password"
            data-testid="setup-password-input"
            :disabled="!isHydrated || isSaving"
            required
          />
        </div>

        <div>
          <label for="confirm-password" class="mb-1 block text-sm font-medium text-slate-700">
            Confirm password
          </label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            class="field-input"
            autocomplete="new-password"
            data-testid="setup-password-confirm-input"
            :disabled="!isHydrated || isSaving"
            required
          />
        </div>

        <p v-if="errorMsg" class="text-sm text-rose-600" data-testid="setup-account-error">
          {{ errorMsg }}
        </p>

        <button
          type="submit"
          class="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          :disabled="!isHydrated || isSaving"
          data-testid="setup-account-submit"
        >
          {{ isSaving ? 'Saving…' : 'Save password' }}
        </button>
      </form>
    </section>
  </div>
</template>
