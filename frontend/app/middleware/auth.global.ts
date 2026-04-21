import { defineNuxtRouteMiddleware, navigateTo } from '#imports';
import { useAuthStore } from '@features/auth/model/auth-store';

export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore();
  authStore.loadFromStorage();

  if (to.path === '/login') {
    if (authStore.isAuthenticated) {
      const user = authStore.user ?? (await authStore.fetchMe());
      if (user) {
        if (authStore.requiresAccountSetup) {
          return navigateTo('/setup-account');
        }
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

  if (authStore.requiresAccountSetup && to.path !== '/setup-account') {
    return navigateTo('/setup-account');
  }

  if (to.path === '/setup-account') {
    if (authStore.user?.role !== 'patient') {
      return navigateTo('/dashboard');
    }
    if (!authStore.requiresAccountSetup) {
      return navigateTo('/dashboard');
    }
  }
});
