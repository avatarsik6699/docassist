<script setup lang="ts">
import { useAuthStore } from '@features/auth/model/auth-store';

definePageMeta({ layout: 'blank' });

const authStore = useAuthStore();

const isHydrated = ref(false);
const email = ref('');
const password = ref('');
const errorMsg = ref<string | null>(null);

onMounted(() => {
  isHydrated.value = true;
});

async function handleLogin() {
  if (!email.value.trim() || !password.value) {
    errorMsg.value = 'Email and password are required.';
    return;
  }
  errorMsg.value = null;
  try {
    await authStore.login(email.value.trim(), password.value);
    await navigateTo('/dashboard', { replace: true });
  } catch {
    errorMsg.value = 'Invalid email or password. Please try again.';
  }
}
</script>

<template>
  <div class="login-shell w-full max-w-md rounded-3xl p-8 shadow-xl space-y-8">
    <div class="space-y-3 text-center">
      <p class="eyebrow">Phase 01</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Docassist</h1>
      <p class="text-sm leading-6 text-slate-600">
        Sign in with the seeded admin account to verify the Phase 01 auth foundation.
      </p>
    </div>

    <form class="space-y-4" @submit.prevent="handleLogin">
      <div>
        <label for="email" class="block text-sm font-medium text-slate-700 mb-1">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          placeholder="admin@example.com"
          :disabled="!isHydrated || authStore.isLoading"
          required
          data-testid="email-input"
          class="field-input"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-slate-700 mb-1">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="••••••••"
          :disabled="!isHydrated || authStore.isLoading"
          required
          data-testid="password-input"
          class="field-input"
        />
      </div>

      <p v-if="errorMsg" data-testid="login-error" class="text-sm text-rose-600">{{ errorMsg }}</p>

      <button
        type="submit"
        :disabled="!isHydrated || authStore.isLoading"
        data-testid="login-submit"
        class="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
      >
        {{ authStore.isLoading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>

    <p class="text-xs text-center text-slate-500">
      Default: <span class="font-mono">admin@example.com</span> /
      <span class="font-mono">changeme123</span>
    </p>
  </div>
</template>
