import { computed, ref } from 'vue';
import { navigateTo, refreshCookie, useNuxtApp, useCookie, useLocalePath } from '#imports';
import { defineStore } from 'pinia';

export const AUTH_COOKIE_CONFIG = {
  key: 'docassist_token',
  version: '1.0',
};

type TokenCookieValue = { version: string; data: string } | null;

export interface AuthUser {
  id: string;
  email: string;
  role: 'admin' | 'doctor' | 'patient';
  is_active: boolean;
  onboarding_status?: 'pending' | 'completed' | null;
  must_change_password?: boolean | null;
  doctor_user_id?: string | null;
}

export const useAuthStore = defineStore('auth', () => {
  const localePath = useLocalePath();
  const tokenCookie = useCookie<TokenCookieValue>(AUTH_COOKIE_CONFIG.key, {
    maxAge: 60 * 60,
    path: '/',
    sameSite: 'lax',
  });

  const user = ref<AuthUser | null>(null);
  const token = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!token.value);
  const requiresAccountSetup = computed(
    () => user.value?.role === 'patient' && Boolean(user.value.must_change_password)
  );

  function loadFromStorage(): string | undefined {
    const raw = tokenCookie.value;
    if (raw?.version === AUTH_COOKIE_CONFIG.version) {
      token.value = raw.data;
    } else if (!token.value) {
      token.value = null;
    }
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

      tokenCookie.value = { version: AUTH_COOKIE_CONFIG.version, data: data.access_token };
      refreshCookie(AUTH_COOKIE_CONFIG.key);

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
    tokenCookie.value = null;
    refreshCookie(AUTH_COOKIE_CONFIG.key);

    if (redirect) {
      await navigateTo(localePath('/login'));
    }
  }

  async function setupAccount(newPassword: string): Promise<AuthUser> {
    const { $api } = useNuxtApp();
    const updatedUser = await $api<AuthUser>('/api/v1/patients/setup-account', {
      method: 'POST',
      body: {
        new_password: newPassword,
      },
    });

    user.value = updatedUser;
    return updatedUser;
  }

  return {
    user,
    isLoading,
    error,
    token,
    isAuthenticated,
    requiresAccountSetup,
    loadFromStorage,
    login,
    fetchMe,
    logout,
    setupAccount,
  };
});
