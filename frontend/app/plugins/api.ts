import { defineNuxtPlugin, useRuntimeConfig, navigateTo, useCookie, useLocalePath } from '#imports';
import { AUTH_COOKIE_CONFIG } from '@features/auth/model/auth-store';

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const localePath = useLocalePath();
  const rawApiBase = (import.meta.server ? config.apiBaseInternal : config.public.apiBase) as
    | string
    | undefined;
  const configuredApiBase = (rawApiBase || 'http://localhost:8000/api/v1')
    .replace(/\/$/, '')
    .replace(/\/api\/v1$/, '');

  const tokenCookie = useCookie<{ version: string; data: string } | null>(AUTH_COOKIE_CONFIG.key);

  const api = $fetch.create({
    baseURL: configuredApiBase,

    onRequest({ options }) {
      const raw = tokenCookie.value;
      const token = raw?.version === AUTH_COOKIE_CONFIG.version ? raw.data : null;

      if (token) {
        options.headers = options.headers || {};

        // Nuxt's $fetch headers can be Headers init, record, or array
        if (options.headers instanceof Headers) {
          options.headers.set('Authorization', `Bearer ${token}`);
        } else if (Array.isArray(options.headers)) {
          (options.headers as [string, string][]).push(['Authorization', `Bearer ${token}`]);
        } else {
          (options.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
        }
      }
    },

    onResponseError({ response }) {
      if (response.status === 401) {
        tokenCookie.value = null;

        if (import.meta.client) {
          navigateTo(localePath('/login'));
        }
      }
    },
  });

  return {
    provide: {
      api,
    },
  };
});
