import { useEffect, useRef, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { signIn } from '@/store/slices/authSlice'
import { resolveDefaultUserId } from '@/services/autoIdentity'

/**
 * Wraps every route. There's no real session to validate (the backend has
 * no auth layer) and no sign-in screen — this just guarantees a userId
 * exists before rendering pages that assume one, resolving one silently
 * (reuse the first User, or create a default local rep) so the AI-first
 * workspace is the very first thing a rep sees.
 *
 * `startedRef` (not a cleanup-based cancel flag) guards the one-shot
 * resolution call: dispatching `signIn` changes `userId`, which is this
 * effect's own dependency, so it re-runs as soon as the id lands — a
 * cleanup-based "cancelled" flag would race that re-run's cleanup against
 * the in-flight promise's `.then()`, sometimes losing `setResolving(false)`
 * for good. The ref sidesteps that: once started, later re-runs are
 * no-ops regardless of render timing.
 */
export default function AppShell() {
  const dispatch = useAppDispatch()
  const userId = useAppSelector((state) => state.auth.userId)
  const [resolving, setResolving] = useState(!userId)
  const startedRef = useRef(false)

  useEffect(() => {
    if (userId || startedRef.current) return
    startedRef.current = true

    resolveDefaultUserId().then((id) => {
      dispatch(signIn(id))
      setResolving(false)
    })
  }, [userId, dispatch])

  if (resolving) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-primary" />
      </div>
    )
  }

  return <Outlet />
}
