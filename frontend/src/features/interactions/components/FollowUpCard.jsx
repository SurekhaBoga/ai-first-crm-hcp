import { AlarmClock, CalendarCheck } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import StatusBadge from '@/components/common/StatusBadge'
import { FOLLOW_UP_STATUS_META, getFollowUpStatus } from '@/constants/enums'
import { formatDate } from '@/utils/date'

export default function FollowUpCard({ interaction }) {
  if (!interaction.follow_up_required) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarCheck className="h-4 w-4 text-muted-foreground" />
            Follow-up
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No follow-up needed for this interaction.</p>
        </CardContent>
      </Card>
    )
  }

  const status = getFollowUpStatus(interaction.follow_up_date, interaction.follow_up_required)
  const statusMeta = FOLLOW_UP_STATUS_META[status]

  return (
    <Card className={status === 'overdue' ? 'border-destructive/40' : undefined}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-2">
          <span className="flex items-center gap-2">
            <AlarmClock className="h-4 w-4 text-muted-foreground" />
            Follow-up
          </span>
          <StatusBadge tone={statusMeta.tone}>{statusMeta.label}</StatusBadge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm">
          <span className="text-muted-foreground">Due </span>
          <span className="font-medium">{formatDate(interaction.follow_up_date)}</span>
        </p>
        {interaction.follow_up_actions && <p className="text-sm text-muted-foreground">{interaction.follow_up_actions}</p>}
      </CardContent>
    </Card>
  )
}
