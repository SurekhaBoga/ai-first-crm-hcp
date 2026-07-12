import { Loader2 } from 'lucide-react'

/** Suspense fallback for lazy-loaded routes. */
export default function PageLoader() {
  return (
    <div className="flex h-full min-h-64 w-full items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  )
}
