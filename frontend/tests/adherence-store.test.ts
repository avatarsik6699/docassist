import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useAdherenceStore } from '../app/features/adherence/model/adherence-store';

const { apiMock } = vi.hoisted(() => ({
  apiMock: vi.fn(),
}));

vi.mock('#imports', () => ({
  useNuxtApp: () => ({
    $api: apiMock,
  }),
}));

describe('useAdherenceStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiMock.mockReset();
  });

  it('loads doctor-visible adherence history', async () => {
    apiMock.mockResolvedValueOnce({
      items: [
        {
          id: '00000000-0000-0000-0000-000000000111',
          medication_id: '00000000-0000-0000-0000-000000000222',
          status: 'taken',
          deviation_note: null,
          logged_at: '2026-04-21T10:00:00Z',
        },
      ],
    });

    const store = useAdherenceStore();
    const items = await store.loadHistory('00000000-0000-0000-0000-000000000333');

    expect(items).toHaveLength(1);
    expect(store.history[0]?.status).toBe('taken');
    expect(apiMock).toHaveBeenCalledWith(
      '/api/v1/patients/00000000-0000-0000-0000-000000000333/adherence'
    );
  });

  it('submits a patient adherence log and prepends it to history', async () => {
    apiMock.mockResolvedValueOnce({
      id: '00000000-0000-0000-0000-000000000444',
      medication_id: '00000000-0000-0000-0000-000000000222',
      status: 'modified',
      deviation_note: 'Took half dose',
      logged_at: '2026-04-21T11:00:00Z',
    });

    const store = useAdherenceStore();
    const created = await store.submitLog({
      medicationId: '00000000-0000-0000-0000-000000000222',
      status: 'modified',
      deviationNote: '  Took half dose  ',
    });

    expect(created.deviation_note).toBe('Took half dose');
    expect(store.history[0]?.id).toBe('00000000-0000-0000-0000-000000000444');
    expect(store.successMessage).toBe('Adherence saved.');
    expect(apiMock).toHaveBeenCalledWith(
      '/api/v1/medications/00000000-0000-0000-0000-000000000222/adherence',
      {
        method: 'POST',
        body: {
          status: 'modified',
          deviation_note: 'Took half dose',
        },
      }
    );
  });
});
