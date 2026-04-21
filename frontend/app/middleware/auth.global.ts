import { defineNuxtRouteMiddleware, navigateTo, useLocalePath } from '#imports';
import { useAuthStore } from '@features/auth/model/auth-store';

export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore();
  const localePath = useLocalePath();
  const loginPath = localePath('/login');
  const dashboardPath = localePath('/dashboard');
  const setupAccountPath = localePath('/setup-account');

  authStore.loadFromStorage();

  if (to.path === loginPath) {
    if (authStore.isAuthenticated) {
      const user = authStore.user ?? (await authStore.fetchMe());
      if (user) {
        if (authStore.requiresAccountSetup) {
          return navigateTo(setupAccountPath);
        }
        return navigateTo(dashboardPath);
      }
    }
    return;
  }

  if (!authStore.isAuthenticated) {
    return navigateTo(loginPath);
  }

  if (!authStore.user) {
    const user = await authStore.fetchMe();
    if (!user) {
      return navigateTo(loginPath);
    }
  }

  if (authStore.requiresAccountSetup && to.path !== setupAccountPath) {
    return navigateTo(setupAccountPath);
  }

  if (to.path === setupAccountPath) {
    if (authStore.user?.role !== 'patient') {
      return navigateTo(dashboardPath);
    }
    if (!authStore.requiresAccountSetup) {
      return navigateTo(dashboardPath);
    }
  }
});
