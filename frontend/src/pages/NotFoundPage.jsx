import { Link } from 'react-router-dom'
import { SearchX } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ROUTES } from '@/constants/routes'

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center gap-3 py-16 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <SearchX className="h-5 w-5" />
      </span>
      <div className="space-y-1">
        <h2 className="text-lg font-semibold">Page not found</h2>
        <p className="text-sm text-muted-foreground">This page doesn&apos;t exist, or the URL is incorrect.</p>
      </div>
      <Button asChild size="sm">
        <Link to={ROUTES.DASHBOARD}>Back to Home</Link>
      </Button>
    </div>
  )
}
