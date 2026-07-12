/**
 * Central query-key factory. Every useQuery/useMutation invalidation in
 * the app goes through these instead of hand-typed arrays, so a key
 * typo can't silently break cache invalidation.
 */
export const queryKeys = {
  users: {
    all: ['users'],
    list: (params) => ['users', 'list', params],
    detail: (userId) => ['users', 'detail', userId],
  },
  doctors: {
    all: ['doctors'],
    list: (params) => ['doctors', 'list', params],
    search: (params) => ['doctors', 'search', params],
    detail: (doctorId) => ['doctors', 'detail', doctorId],
  },
  interactions: {
    all: ['interactions'],
    list: (params) => ['interactions', 'list', params],
    detail: (interactionId) => ['interactions', 'detail', interactionId],
    timeline: (doctorId, params) => ['interactions', 'timeline', doctorId, params],
  },
  chatHistory: {
    session: (sessionId) => ['chatHistory', 'session', sessionId],
  },
  ai: {
    doctorProfile: (doctorId) => ['ai', 'doctorProfile', doctorId],
    summary: (interactionId) => ['ai', 'summary', interactionId],
  },
}
