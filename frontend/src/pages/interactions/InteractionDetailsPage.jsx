import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import IconButton from '@/components/common/IconButton'
import StatusBadge from '@/components/common/StatusBadge'
import ErrorState from '@/components/data/ErrorState'
import ConfirmDialog from '@/components/data/ConfirmDialog'
import DoctorCard from '@/features/doctors/components/DoctorCard'
import SummaryCard from '@/features/interactions/components/SummaryCard'
import FollowUpCard from '@/features/interactions/components/FollowUpCard'
import AiSummaryPanel from '@/features/interactions/components/AiSummaryPanel'
import InteractionTimeline from '@/features/interactions/components/InteractionTimeline'
import { useInteraction, useDeleteInteraction, useDoctorTimeline } from '@/hooks/queries/useInteractions'
import { useDoctor } from '@/hooks/queries/useDoctors'
import { INTERACTION_TYPE_LABELS, SENTIMENT_META } from '@/constants/enums'
import { ROUTES } from '@/constants/routes'

export default function InteractionDetailsPage() {
  const { interactionId } = useParams()
  const navigate = useNavigate()
  const [deleteOpen, setDeleteOpen] = useState(false)

  const deleteInteraction = useDeleteInteraction()
  // Once the delete mutation succeeds, stop refetching this interaction and
  // its related queries — navigation away happens on the next render, but
  // until it does these would otherwise refetch a now-deleted resource and
  // 404.
  const isDeleted = deleteInteraction.isSuccess
  const interactionQuery = useInteraction(interactionId, { enabled: !isDeleted })
  const interaction = interactionQuery.data
  const doctorQuery = useDoctor(interaction?.doctor_id, { enabled: Boolean(interaction) && !isDeleted })
  const timelineQuery = useDoctorTimeline(
    interaction?.doctor_id,
    { pageSize: 10 },
    { enabled: Boolean(interaction) && !isDeleted },
  )

  if (interactionQuery.isError) {
    return <ErrorState error={interactionQuery.error} onRetry={interactionQuery.refetch} />
  }

  if (interactionQuery.isLoading || !interaction) {
    return (
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Skeleton className="h-96 w-full lg:col-span-2" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  const sentiment = interaction.sentiment ? SENTIMENT_META[interaction.sentiment] : null

  const handleDelete = () => {
    deleteInteraction.mutate(interaction.id, { onSuccess: () => navigate(ROUTES.DASHBOARD) })
  }

  return (
    <div className="space-y-4">
      {/* No manual edit here by design — corrections go through a new AI
          Assistant conversation, same as the initial log. Delete remains
          available as a destructive action, not a field edit. */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild>
            <Link to={ROUTES.DASHBOARD} aria-label="Back to Log Interaction">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">{INTERACTION_TYPE_LABELS[interaction.interaction_type]}</h2>
              {sentiment && <StatusBadge tone={sentiment.tone}>{sentiment.label}</StatusBadge>}
            </div>
            <p className="text-sm text-muted-foreground">with {doctorQuery.data?.full_name ?? '…'}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <IconButton
            label="Delete interaction"
            icon={Trash2}
            variant="outline"
            className="text-destructive hover:text-destructive"
            onClick={() => setDeleteOpen(true)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <SummaryCard interaction={interaction} />
          <AiSummaryPanel interaction={interaction} />
          <Card>
            <CardHeader>
              <CardTitle>Timeline with this doctor</CardTitle>
              <CardDescription>Recent interactions, most recent first — this one is highlighted.</CardDescription>
            </CardHeader>
            <CardContent>
              {timelineQuery.isLoading ? (
                <Skeleton className="h-32 w-full" />
              ) : (
                <InteractionTimeline interactions={timelineQuery.data?.items ?? []} highlightId={interaction.id} />
              )}
            </CardContent>
          </Card>
        </div>
        <div className="space-y-4">
          {doctorQuery.data && <DoctorCard doctor={doctorQuery.data} />}
          <FollowUpCard interaction={interaction} />
        </div>
      </div>

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete this interaction?"
        description="This permanently removes the interaction record. This can't be undone."
        confirmLabel="Delete interaction"
        isLoading={deleteInteraction.isPending}
        onConfirm={handleDelete}
      />
    </div>
  )
}
