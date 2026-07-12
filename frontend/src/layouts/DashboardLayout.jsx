import { Outlet } from 'react-router-dom'
import Navbar from './components/Navbar'

/**
 * Root shell for every screen. Deliberately just a top bar over a
 * full-height content area — no sidebar, no breadcrumbs: the app is the
 * AI-first Log Interaction workspace plus the Doctor Directory it needs
 * HCPs to exist in, not a multi-section admin console.
 */
export default function DashboardLayout() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-muted/30">
      <Navbar />
      <main className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto h-full max-w-7xl p-4 lg:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
