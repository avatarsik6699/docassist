import { computed, ref } from 'vue';
import { navigateTo, useNuxtApp } from '#imports';
import { defineStore } from 'pinia';
import { safeCookie } from '@shared/lib/safe-cookie';

export const AUTH_COOKIE_CONFIG = {
  key: 'docassist_token',
  version: '1.0',
};

export interface AuthUser {
  id: string;
  email: string;
  role: 'admin' | 'doctor' | 'patient';
  is_active: boolean;
}

const readTokenFromCookie = () =>
  safeCookie.getItem<string>({
    keyWithVersion: AUTH_COOKIE_CONFIG,
  });

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null);
  const token = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!token.value);

  function loadFromStorage(): string | undefined {
    token.value = readTokenFromCookie() ?? null;
    return token.value ?? undefined;
  }

  async function login(email: string, password: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const { $api } = useNuxtApp();
      const data = await $api<{ access_token: string; token_type: string }>('/api/v1/auth/login', {
        method: 'POST',
        body: {
          email,
          password,
        },
      });

      safeCookie.setItem({
        keyWithVersion: AUTH_COOKIE_CONFIG,
        value: data.access_token,
        options: {
          maxAge: 60 * 60,
          path: '/',
          sameSite: 'lax',
        },
      });

      token.value = data.access_token;
      await fetchMe(data.access_token);
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchMe(accessToken = token.value): Promise<AuthUser | null> {
    if (!accessToken) {
      user.value = null;
      return null;
    }

    try {
      const { $api } = useNuxtApp();
      const data = await $api<AuthUser>('/api/v1/auth/me', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      user.value = data;
      return data;
    } catch {
      await logout(false);
      return null;
    }
  }

  async function logout(redirect = true): Promise<void> {
    const currentToken = token.value;

    if (currentToken) {
      try {
        const { $api } = useNuxtApp();
        await $api('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${currentToken}`,
          },
        });
      } catch {
        // Logout is best-effort because the current implementation is stateless.
      }
    }

    token.value = null;
    user.value = null;
    error.value = null;
    safeCookie.removeItem({ keyWithVersion: AUTH_COOKIE_CONFIG });

    if (redirect) {
      await navigateTo('/login');
    }
  }

  return {
    user,
    isLoading,
    error,
    token,
    isAuthenticated,
    loadFromStorage,
    login,
    fetchMe,
    logout,
  };
});
