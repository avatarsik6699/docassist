import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useSideEffectsStore } from '../app/features/side-effects/model/side-effects-store';

const { apiMock } = vi.hoisted(() => ({
  apiMock: vi.fn(),
}));

vi.mock('#imports', () => ({
  useNuxtApp: () => ({
    $api: apiMock,
  }),
}));

describe('useSideEffectsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiMock.mockReset();
  });

  it('loads doctor-visible side-effect history', async () => {
    apiMock.mockResolvedValueOnce({
      items: [
        {
          id: '00000000-0000-0000-0000-000000000111',
          severity: 'moderate',
          symptom: 'Nausea',
          note: 'After dinner dose',
          reported_at: '2026-04-21T10:00:00Z',
        },
      ],
    });

    const store = useSideEffectsStore();
    const items = await store.loadHistory('00000000-0000-0000-0000-000000000333');

    expect(items).toHaveLength(1);
    expect(store.history[0]?.severity).toBe('moderate');
    expect(apiMock).toHaveBeenCalledWith(
      '/api/v1/patients/00000000-0000-0000-0000-000000000333/side-effects'
    );
  });

  it('submits a patient side-effect report and prepends history', async () => {
    apiMock.mockResolvedValueOnce({
      id: '00000000-0000-0000-0000-000000000444',
      severity: 'severe',
      symptom: 'Persistent dizziness',
      note: 'Started yesterday',
      reported_at: '2026-04-21T11:00:00Z',
    });

    const store = useSideEffectsStore();
    const created = await store.submitReport({
      medicationId: '00000000-0000-0000-0000-000000000222',
      severity: 'severe',
      symptom: '  Persistent dizziness  ',
      note: '  Started yesterday  ',
    });

    expect(created.symptom).toBe('Persistent dizziness');
    expect(store.history[0]?.id).toBe('00000000-0000-0000-0000-000000000444');
    expect(store.successMessage).toBe('Side effect reported.');
    expect(apiMock).toHaveBeenCalledWith('/api/v1/side-effects', {
      method: 'POST',
      body: {
        severity: 'severe',
        symptom: 'Persistent dizziness',
        note: 'Started yesterday',
        medication_id: '00000000-0000-0000-0000-000000000222',
      },
    });
  });
});
