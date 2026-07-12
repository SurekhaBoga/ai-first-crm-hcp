import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { signOut } from '@/store/slices/authSlice'
import { useUser } from '@/hooks/queries/useUsers'

/**
 * The active "identity" (see authSlice) plus its live User record. If the
 * signed-in user was deleted elsewhere (another tab, another rep), the
 * 404 auto-signs-out instead of leaving the app stuck on a dead id.
 */
export function useCurrentUser() {
  const dispatch = useAppDispatch()
  const userId = useAppSelector((state) => state.auth.userId)
  const query = useUser(userId, { enabled: Boolean(userId) })

  useEffect(() => {
    if (query.isError) dispatch(signOut())
  }, [query.isError, dispatch])

  return {
    userId,
    user: query.data,
    isLoading: Boolean(userId) && query.isLoading,
  }
}
