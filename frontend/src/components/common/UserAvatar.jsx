import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

function initialsOf(name) {
  if (!name) return '?'
  return name
    .replace(/^Dr\.\s*/i, '')
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

/**
 * Initials avatar for reps and doctors alike — the app never stores
 * profile photos, so this is the only avatar affordance needed.
 */
export default function UserAvatar({ name, size = 'default', className }) {
  return (
    <Avatar size={size} className={cn(className)}>
      <AvatarFallback className="bg-accent font-semibold text-accent-foreground">
        {initialsOf(name)}
      </AvatarFallback>
    </Avatar>
  )
}
