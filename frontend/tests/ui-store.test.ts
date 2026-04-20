import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useAuthStore } from '../app/features/auth/model/auth-store';

const { apiMock, navigateToMock, cookieStore } = vi.hoisted(() => ({
  apiMock: vi.fn(),
  navigateToMock: vi.fn(),
  cookieStore: new Map<string, unknown>(),
}));

vi.mock('#imports', () => ({
  navigateTo: navigateToMock,
  useNuxtApp: () => ({
    $api: apiMock,
  }),
  useCookie: (key: string) => ({
    get value() {
      return cookieStore.get(key) ?? null;
    },
    set value(value: unknown) {
      if (value === null || value === undefined) {
        cookieStore.delete(key);
        return;
      }
      cookieStore.set(key, value);
    },
  }),
}));

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiMock.mockReset();
    navigateToMock.mockReset();
    cookieStore.clear();
  });

  it('stores the token and current user after login', async () => {
    apiMock
      .mockResolvedValueOnce({ access_token: 'jwt-token', token_type: 'bearer' })
      .mockResolvedValueOnce({
        id: '00000000-0000-0000-0000-000000000001',
        email: 'admin@example.com',
        role: 'admin',
        is_active: true,
      });

    const store = useAuthStore();
    await store.login('admin@example.com', 'changeme123');

    expect(store.isAuthenticated).toBe(true);
    expect(store.user?.email).toBe('admin@example.com');
    expect(apiMock).toHaveBeenNthCalledWith(1, '/api/v1/auth/login', {
      method: 'POST',
      body: {
        email: 'admin@example.com',
        password: 'changeme123',
      },
    });
    expect(apiMock).toHaveBeenNthCalledWith(2, '/api/v1/auth/me', {
      headers: {
        Authorization: 'Bearer jwt-token',
      },
    });
  });

  it('hydrates the token from cookies for auth bootstrap', () => {
    cookieStore.set('docassist_token', { version: '1.0', data: 'jwt-token' });

    const store = useAuthStore();
    const token = store.loadFromStorage();

    expect(token).toBe('jwt-token');
    expect(store.isAuthenticated).toBe(true);
  });

  it('clears auth state, calls the logout endpoint, and redirects on logout', async () => {
    cookieStore.set('docassist_token', { version: '1.0', data: 'jwt-token' });
    apiMock.mockResolvedValueOnce({ message: 'logged out' });

    const store = useAuthStore();
    store.loadFromStorage();
    await store.logout();

    expect(store.user).toBeNull();
    expect(store.isAuthenticated).toBe(false);
    expect(apiMock).toHaveBeenCalledWith('/api/v1/auth/logout', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer jwt-token',
      },
    });
    expect(navigateToMock).toHaveBeenCalledWith('/login');
  });
});
