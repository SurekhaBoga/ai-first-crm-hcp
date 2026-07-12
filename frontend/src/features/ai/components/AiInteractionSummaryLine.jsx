import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import StatusBadge from '@/components/common/StatusBadge'
import { useDoctor } from '@/hooks/queries/useDoctors'
import { INTERACTION_TYPE_LABELS, SENTIMENT_META } from '@/constants/enums'
import { buildInteractionDetailPath } from '@/constants/routes'
import { formatDate } from '@/utils/date'

/**
 * One-line interaction summary used inside AI result cards. Resolves the
 * doctor's name via the cached useDoctor query — AI responses only carry
 * doctor_id, same as every other InteractionRead in the app.
 */
export default function AiInteractionSummaryLine({ interaction }) {
  const { data: doctor } = useDoctor(interaction.doctor_id)
  const sentiment = interaction.sentiment ? SENTIMENT_META[interaction.sentiment] : null

  return (
    <Link
      to={buildInteractionDetailPath(interaction.id)}
      className="flex items-center gap-3 rounded-lg border p-3 text-sm transition-colors hover:bg-accent/50"
    >
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{doctor?.full_name ?? 'Loading…'}</p>
        <p className="truncate text-xs text-muted-foreground">
          {INTERACTION_TYPE_LABELS[interaction.interaction_type]} · {formatDate(interaction.interaction_date)}
        </p>
      </div>
      {sentiment && <StatusBadge tone={sentiment.tone}>{sentiment.label}</StatusBadge>}
      <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
    </Link>
  )
}
