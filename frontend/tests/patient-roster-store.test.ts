import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { usePatientRosterStore } from '../app/features/patient-roster/model/patient-roster-store';

const { apiMock } = vi.hoisted(() => ({
  apiMock: vi.fn(),
}));

vi.mock('#imports', () => ({
  useNuxtApp: () => ({
    $api: apiMock,
  }),
}));

describe('usePatientRosterStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiMock.mockReset();
  });

  it('loads the current doctor roster', async () => {
    apiMock.mockResolvedValueOnce({
      items: [
        {
          id: '00000000-0000-0000-0000-000000000101',
          email: 'patient@example.com',
          is_active: true,
          onboarding_status: 'pending',
        },
      ],
    });

    const store = usePatientRosterStore();
    const items = await store.loadPatients();

    expect(items).toHaveLength(1);
    expect(store.items[0]?.email).toBe('patient@example.com');
    expect(apiMock).toHaveBeenCalledWith('/api/v1/patients');
  });

  it('creates a patient and refreshes the roster', async () => {
    apiMock
      .mockResolvedValueOnce({
        id: '00000000-0000-0000-0000-000000000102',
        email: 'new.patient@example.com',
        doctor_user_id: '00000000-0000-0000-0000-000000000201',
        onboarding_status: 'pending',
        temporary_password: 'TempPass123',
      })
      .mockResolvedValueOnce({
        items: [
          {
            id: '00000000-0000-0000-0000-000000000102',
            email: 'new.patient@example.com',
            is_active: true,
            onboarding_status: 'pending',
          },
        ],
      });

    const store = usePatientRosterStore();
    const created = await store.createPatient('new.patient@example.com');

    expect(created.temporary_password).toBe('TempPass123');
    expect(store.latestCreatedPatient?.email).toBe('new.patient@example.com');
    expect(store.items).toHaveLength(1);
    expect(apiMock).toHaveBeenNthCalledWith(1, '/api/v1/patients', {
      method: 'POST',
      body: {
        email: 'new.patient@example.com',
      },
    });
    expect(apiMock).toHaveBeenNthCalledWith(2, '/api/v1/patients');
  });

  it('activates an inactive patient and refreshes the roster', async () => {
    apiMock
      .mockResolvedValueOnce({
        id: '00000000-0000-0000-0000-000000000103',
        is_active: true,
        onboarding_status: 'completed',
      })
      .mockResolvedValueOnce({
        items: [
          {
            id: '00000000-0000-0000-0000-000000000103',
            email: 'inactive.patient@example.com',
            is_active: true,
            onboarding_status: 'completed',
          },
        ],
      });

    const store = usePatientRosterStore();
    await store.activatePatient('00000000-0000-0000-0000-000000000103');

    expect(apiMock).toHaveBeenNthCalledWith(
      1,
      '/api/v1/patients/00000000-0000-0000-0000-000000000103/activate',
      {
        method: 'POST',
      }
    );
    expect(store.items[0]?.is_active).toBe(true);
  });
});
