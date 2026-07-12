import { useQuery } from '@tanstack/react-query'
import * as usersApi from '@/api/users'
import { queryKeys } from '@/api/queryKeys'

/**
 * There's no user-management UI in this build (see AppShell/autoIdentity
 * — identity is resolved silently, never picked or edited) — this is the
 * one read used to look up the current user's details.
 */
export function useUser(userId, options = {}) {
  return useQuery({
    queryKey: queryKeys.users.detail(userId),
    queryFn: () => usersApi.getUser(userId),
    enabled: Boolean(userId) && (options.enabled ?? true),
  })
}
