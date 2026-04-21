<script setup lang="ts">
import { AUTH_COOKIE_CONFIG } from '@features/auth/model/auth-store';

const authStore = useAuthStore();
const localePath = useLocalePath();

if (import.meta.client) {
  await authStore.logout(false);
  reloadNuxtApp({ path: localePath('/login'), force: true });
} else {
  const tokenCookie = useCookie<{ version: string; data: string } | null>(AUTH_COOKIE_CONFIG.key, {
    path: '/',
    sameSite: 'lax',
  });

  tokenCookie.value = null;
  refreshCookie(AUTH_COOKIE_CONFIG.key);

  await navigateTo(localePath('/login'), { replace: true });
}
</script>

<template>
  <div />
</template>
