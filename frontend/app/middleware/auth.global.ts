import { defineNuxtRouteMiddleware, navigateTo } from '#imports';
import { useAuthStore } from '@features/auth/model/auth-store';

export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore();
  authStore.loadFromStorage();

  if (to.path === '/login') {
    if (authStore.isAuthenticated) {
      const user = authStore.user ?? (await authStore.fetchMe());
      if (user) {
        return navigateTo('/dashboard');
      }
    }
    return;
  }

  if (!authStore.isAuthenticated) {
    return navigateTo('/login');
  }

  if (!authStore.user) {
    const user = await authStore.fetchMe();
    if (!user) {
      return navigateTo('/login');
    }
  }
});
