<script setup lang="ts">
import { useAuthStore } from '@features/auth/model/auth-store';

definePageMeta({ layout: 'blank' });

const authStore = useAuthStore();
const { t } = useI18n();
const localePath = useLocalePath();

const isHydrated = ref(false);
const email = ref('');
const password = ref('');
const errorMsg = ref<string | null>(null);

onMounted(() => {
  isHydrated.value = true;
});

async function handleLogin() {
  if (!email.value.trim() || !password.value) {
    errorMsg.value = t('login.validation.required');
    return;
  }
  errorMsg.value = null;
  try {
    await authStore.login(email.value.trim(), password.value);
    await navigateTo(localePath('/dashboard'), { replace: true });
  } catch {
    errorMsg.value = t('login.validation.invalid');
  }
}
</script>

<template>
  <div class="login-shell w-full max-w-md rounded-3xl p-8 shadow-xl space-y-8">
    <div class="space-y-3 text-center">
      <h1 class="text-3xl font-semibold tracking-tight text-slate-950">Docassist</h1>
      <p class="text-sm leading-6 text-slate-600">
        {{ t('login.subtitle') }}
      </p>
    </div>

    <form class="space-y-4" @submit.prevent="handleLogin">
      <div>
        <label for="email" class="block text-sm font-medium text-slate-700 mb-1">
          {{ t('common.email') }}
        </label>
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
        <label for="password" class="block text-sm font-medium text-slate-700 mb-1">
          {{ t('common.password') }}
        </label>
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
        {{ authStore.isLoading ? t('login.signingIn') : t('login.signIn') }}
      </button>
    </form>
  </div>
</template>
