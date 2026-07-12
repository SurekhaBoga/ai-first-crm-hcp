import { NavLink } from 'react-router-dom'
import { Stethoscope, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ROUTES } from '@/constants/routes'

/**
 * Minimal top bar — brand mark plus the one secondary destination the
 * workflow actually needs (Doctor Directory, since HCPs have to exist
 * somewhere for the AI to resolve a name against). No search, no theme
 * toggle, no user menu: the assignment's UI is the split-screen
 * workspace, not an admin console.
 */
export default function Navbar() {
  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b bg-background px-4 lg:px-6">
      <NavLink to={ROUTES.DASHBOARD} end className="flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Stethoscope className="h-4 w-4" />
        </span>
        <span className="font-semibold tracking-tight">HCP CRM</span>
      </NavLink>

      <nav className="ml-auto">
        <NavLink
          to={ROUTES.HCPS}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
              isActive && 'bg-accent text-accent-foreground',
            )
          }
        >
          <Users className="h-4 w-4" />
          Doctors
        </NavLink>
      </nav>
    </header>
  )
}
