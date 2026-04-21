import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useQuestionnaireStore } from '../app/features/questionnaires/model/questionnaire-store';

const { apiMock } = vi.hoisted(() => ({
  apiMock: vi.fn(),
}));

vi.mock('#imports', () => ({
  useNuxtApp: () => ({
    $api: apiMock,
  }),
}));

describe('useQuestionnaireStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiMock.mockReset();
  });

  it('loads doctor questionnaire assignments', async () => {
    apiMock.mockResolvedValueOnce({
      items: [
        {
          id: '00000000-0000-0000-0000-000000000001',
          questionnaire_code: 'PHQ-9',
          status: 'assigned',
          assigned_at: '2026-04-21T10:00:00Z',
          completed_at: null,
        },
      ],
    });

    const store = useQuestionnaireStore();
    const items = await store.loadDoctorAssignments('00000000-0000-0000-0000-000000000099');

    expect(items).toHaveLength(1);
    expect(items[0]?.questionnaire_code).toBe('PHQ-9');
    expect(apiMock).toHaveBeenCalledWith(
      '/api/v1/patients/00000000-0000-0000-0000-000000000099/questionnaires'
    );
  });

  it('assigns questionnaire and reloads doctor list', async () => {
    apiMock
      .mockResolvedValueOnce({
        id: '00000000-0000-0000-0000-000000000010',
        questionnaire_code: 'GAD-7',
        status: 'assigned',
        assigned_at: '2026-04-21T10:05:00Z',
        completed_at: null,
      })
      .mockResolvedValueOnce({
        items: [
          {
            id: '00000000-0000-0000-0000-000000000010',
            questionnaire_code: 'GAD-7',
            status: 'assigned',
            assigned_at: '2026-04-21T10:05:00Z',
            completed_at: null,
          },
        ],
      });

    const store = useQuestionnaireStore();
    await store.assignQuestionnaire('00000000-0000-0000-0000-000000000099', 'GAD-7');

    expect(store.doctorItems).toHaveLength(1);
    expect(apiMock).toHaveBeenNthCalledWith(
      1,
      '/api/v1/patients/00000000-0000-0000-0000-000000000099/questionnaires',
      {
        method: 'POST',
        body: {
          questionnaire_code: 'GAD-7',
        },
      }
    );
  });

  it('submits questionnaire and removes it from pending list', async () => {
    apiMock.mockResolvedValueOnce({
      id: '00000000-0000-0000-0000-000000000111',
      assignment_id: '00000000-0000-0000-0000-000000000222',
      questionnaire_code: 'PHQ-9',
      total_score: 3,
      has_safety_signal: false,
      submitted_at: '2026-04-21T10:10:00Z',
    });

    const store = useQuestionnaireStore();
    store.pendingItems = [
      {
        id: '00000000-0000-0000-0000-000000000222',
        questionnaire_code: 'PHQ-9',
        status: 'assigned',
        assigned_at: '2026-04-21T10:00:00Z',
      },
    ];

    const result = await store.submitQuestionnaire('00000000-0000-0000-0000-000000000222', {
      q1: 1,
      q2: 1,
      q3: 1,
      q4: 0,
      q5: 0,
      q6: 0,
      q7: 0,
      q8: 0,
      q9: 0,
    });

    expect(result.total_score).toBe(3);
    expect(store.pendingItems).toHaveLength(0);
    expect(store.submissionResult?.assignment_id).toBe('00000000-0000-0000-0000-000000000222');
  });
});
