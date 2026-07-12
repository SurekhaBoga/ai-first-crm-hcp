import { Link } from 'react-router-dom'
import { Phone, Video, Mail, Users as UsersIcon, Presentation } from 'lucide-react'
import StatusBadge from '@/components/common/StatusBadge'
import EmptyState from '@/components/data/EmptyState'
import { ClipboardList } from 'lucide-react'
import { INTERACTION_TYPE_LABELS, SENTIMENT_META } from '@/constants/enums'
import { buildInteractionDetailPath } from '@/constants/routes'
import { formatDate } from '@/utils/date'
import { cn } from '@/lib/utils'

const TYPE_ICONS = {
  visit: UsersIcon,
  call: Phone,
  video: Video,
  email: Mail,
  conference: Presentation,
}

/**
 * Chronological (newest-first, matches the API's ordering) record of
 * interactions with one doctor — used on the Doctor Profile page and,
 * scoped to a single doctor, alongside Interaction Details.
 */
export default function InteractionTimeline({ interactions, highlightId }) {
  if (interactions.length === 0) {
    return (
      <EmptyState icon={ClipboardList} title="No interactions yet" description="Logged visits will appear here." />
    )
  }

  return (
    <ol className="space-y-0">
      {interactions.map((interaction, index) => {
        const Icon = TYPE_ICONS[interaction.interaction_type] ?? ClipboardList
        const sentiment = interaction.sentiment ? SENTIMENT_META[interaction.sentiment] : null
        const isLast = index === interactions.length - 1

        return (
          <li key={interaction.id} className="relative flex gap-4 pb-6">
            {!isLast && <span className="absolute top-9 left-4 h-[calc(100%-2rem)] w-px bg-border" />}
            <span
              className={cn(
                'z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border bg-background',
                interaction.id === highlightId && 'border-primary text-primary',
              )}
            >
              <Icon className="h-4 w-4" />
            </span>
            <Link
              to={buildInteractionDetailPath(interaction.id)}
              className={cn(
                'flex-1 rounded-lg border p-3 text-sm transition-colors hover:bg-accent/50',
                interaction.id === highlightId && 'border-primary/50 bg-accent/30',
              )}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-medium">{INTERACTION_TYPE_LABELS[interaction.interaction_type]}</p>
                <span className="text-xs text-muted-foreground">{formatDate(interaction.interaction_date)}</span>
              </div>
              {interaction.purpose && <p className="mt-1 text-muted-foreground">{interaction.purpose}</p>}
              <div className="mt-2 flex flex-wrap gap-1.5">
                {sentiment && <StatusBadge tone={sentiment.tone}>{sentiment.label}</StatusBadge>}
                {interaction.follow_up_required && <StatusBadge tone="info">Follow-up needed</StatusBadge>}
              </div>
            </Link>
          </li>
        )
      })}
    </ol>
  )
}
