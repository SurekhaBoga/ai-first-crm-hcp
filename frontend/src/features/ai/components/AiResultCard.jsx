import { Link } from 'react-router-dom'
import { CheckCircle2, ChevronRight, Lightbulb, ListChecks } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import StatusBadge from '@/components/common/StatusBadge'
import UserAvatar from '@/components/common/UserAvatar'
import AiInteractionSummaryLine from './AiInteractionSummaryLine'
import { DOCTOR_TIER_META } from '@/constants/enums'
import { buildDoctorDetailPath, buildInteractionDetailPath } from '@/constants/routes'

/**
 * Renders whatever a /ai/* call returned, keyed off `intent` — the same
 * five shapes every AI-driven page (Log Interaction, AI Assistant) can
 * receive, rendered consistently wherever they show up.
 */
export default function AiResultCard({ intent, data }) {
  if (!data) return null

  switch (intent) {
    case 'log_interaction':
    case 'edit_interaction':
      return (
        <Card className="border-primary/30 bg-accent/20">
          <CardContent className="p-3">
            <AiInteractionSummaryLine interaction={data.interaction} />
          </CardContent>
        </Card>
      )

    case 'search_interaction':
      return (
        <div className="space-y-2">
          {data.interactions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No matching interactions.</p>
          ) : (
            data.interactions.map((interaction) => (
              <AiInteractionSummaryLine key={interaction.id} interaction={interaction} />
            ))
          )}
        </div>
      )

    case 'doctor_profile': {
      const tier = DOCTOR_TIER_META[data.doctor.tier]
      return (
        <Card className="border-primary/30 bg-accent/20">
          <CardContent className="space-y-3 p-3">
            <Link to={buildDoctorDetailPath(data.doctor.id)} className="flex items-center gap-3">
              <UserAvatar name={data.doctor.full_name} />
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{data.doctor.full_name}</p>
                <p className="truncate text-xs text-muted-foreground">{data.doctor.specialty}</p>
              </div>
              <StatusBadge tone={tier.tone}>{tier.label}</StatusBadge>
              <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
            </Link>
            <p className="text-xs text-muted-foreground">
              {data.interaction_count} logged interaction{data.interaction_count === 1 ? '' : 's'}
            </p>
          </CardContent>
        </Card>
      )
    }

    case 'interaction_summary':
      return (
        <Card className="border-primary/30 bg-accent/20">
          <CardContent className="space-y-3 p-3 text-sm">
            <Link
              to={buildInteractionDetailPath(data.interaction.id)}
              className="flex items-center gap-1.5 font-medium text-primary hover:underline"
            >
              <CheckCircle2 className="h-4 w-4" />
              View interaction
            </Link>
            {data.key_insights?.length > 0 && (
              <div>
                <p className="mb-1 flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase">
                  <Lightbulb className="h-3.5 w-3.5" /> Key insights
                </p>
                <ul className="list-inside list-disc space-y-0.5 text-muted-foreground">
                  {data.key_insights.map((insight) => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.follow_up_recommendations?.length > 0 && (
              <div>
                <p className="mb-1 flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase">
                  <ListChecks className="h-3.5 w-3.5" /> Recommended next steps
                </p>
                <ul className="list-inside list-disc space-y-0.5 text-muted-foreground">
                  {data.follow_up_recommendations.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )

    default:
      return null
  }
}
