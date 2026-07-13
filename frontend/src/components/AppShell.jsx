import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
 * Startup failures are rendered explicitly with a retry action. This is
 * important because identity resolution is the first API request the app
 * makes; a stopped API or CORS mistake must never look like a blank page.
 */
export default function AppShell() {
  const dispatch = useAppDispatch()
  const userId = useAppSelector((state) => state.auth.userId)
  const [resolving, setResolving] = useState(!userId)
  const [error, setError] = useState(null)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    if (userId) return

    let active = true

    resolveDefaultUserId()
      .then((id) => {
        if (active) dispatch(signIn(id))
      })
      .catch(() => {
        if (active) setError('Could not connect to the CRM API. Make sure the backend is running.')
      })
      .finally(() => {
        if (active) setResolving(false)
      })

    return () => {
      active = false
    }
  }, [userId, dispatch, retryCount])

  if (userId) return <Outlet />

  if (error) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background p-6">
        <div className="flex max-w-md flex-col items-center gap-4 text-center">
          <AlertTriangle className="h-9 w-9 text-destructive" />
          <div>
            <h1 className="text-lg font-semibold">Unable to start the CRM</h1>
            <p className="mt-1 text-sm text-muted-foreground">{error}</p>
          </div>
          <Button
            onClick={() => {
              setError(null)
              setResolving(true)
              setRetryCount((count) => count + 1)
            }}
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  if (resolving) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-primary" />
      </div>
    )
  }

  return null
}
