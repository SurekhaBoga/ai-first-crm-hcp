import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import StatusBadge from '@/components/common/StatusBadge'
import UserAvatar from '@/components/common/UserAvatar'
import PanelField from './PanelField'
import { useDoctor } from '@/hooks/queries/useDoctors'
import { useAppSelector } from '@/store/hooks'
import { INTERACTION_TYPE_LABELS, SENTIMENT_META } from '@/constants/enums'
import { formatDate } from '@/utils/date'

function ProductChips({ items }) {
  if (!items?.length) return null
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span key={item} className="rounded-full bg-accent px-2.5 py-0.5 text-xs font-medium text-accent-foreground">
          {item}
        </span>
      ))}
    </div>
  )
}

function formatTime(isoDateTime) {
  if (!isoDateTime) return null
  return new Date(isoDateTime).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}

/**
 * The read-only "Log HCP Interaction" panel — the assignment's exact
 * field list (HCP Name, Interaction Type, Date, Time, Topics Discussed,
 * Materials Shared, Samples, Sentiment, Follow-up, AI Summary). The
 * structure is always visible, every field showing "Waiting for AI…"
 * until the conversation on the right fills it in — never a blank/empty
 * screen. Reads exclusively from the interactionDraft Redux slice: every
 * value here was written by a LangGraph tool execution (see
 * AiChatPanel's syncToDraft prop), never typed directly by the rep.
 */
export default function InteractionPanel() {
  const draft = useAppSelector((state) => state.interactionDraft)
  const interaction = draft.interaction
  const changed = (...fields) => fields.some((f) => draft.lastChangedFields.includes(f))

  const doctorQuery = useDoctor(interaction?.doctor_id, { enabled: Boolean(interaction?.doctor_id) })
  const doctor = doctorQuery.data

  const sentiment = interaction?.sentiment ? SENTIMENT_META[interaction.sentiment] : null
  const materialsShared = interaction
    ? [interaction.brochures_shared, interaction.promotional_materials].filter(Boolean).join(' · ')
    : null
  const followUp = !interaction
    ? null
    : interaction.follow_up_required
      ? interaction.follow_up_date
        ? `Yes — by ${formatDate(interaction.follow_up_date)}`
        : 'Yes'
      : 'No'
  const samples = interaction ? (interaction.samples_distributed ? 'Yes' : 'No') : null

  return (
    <section aria-label="Interaction panel" className="space-y-3 overflow-y-auto pr-1">
      <Card className={changed('doctor_id', 'doctor_name') ? 'animate-field-flash' : undefined}>
        <CardContent className="flex items-center gap-3 p-4">
          <UserAvatar name={doctor?.full_name} size="lg" />
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-muted-foreground">HCP Name</p>
            <p className="truncate font-medium">
              {doctor?.full_name ?? (doctorQuery.isLoading ? 'Loading…' : 'Waiting for AI…')}
            </p>
          </div>
          {interaction && (
            <StatusBadge tone={interaction.status === 'draft' ? 'warning' : 'positive'}>
              {interaction.status === 'draft' ? 'Draft' : 'Saved'}
            </StatusBadge>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Log HCP Interaction</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-1 sm:grid-cols-2">
          <PanelField
            label="Interaction Type"
            value={interaction ? INTERACTION_TYPE_LABELS[interaction.interaction_type] : null}
            highlighted={changed('interaction_type')}
            updatedAt={draft.lastUpdatedAt}
          />
          <PanelField
            label="Date"
            value={interaction ? formatDate(interaction.interaction_date) : null}
            highlighted={changed('interaction_date')}
            updatedAt={draft.lastUpdatedAt}
          />
          <PanelField
            label="Time"
            value={interaction ? formatTime(interaction.interaction_date) : null}
            highlighted={changed('interaction_date')}
            updatedAt={draft.lastUpdatedAt}
          />
          <PanelField
            label="Sentiment"
            value={sentiment ? <StatusBadge tone={sentiment.tone}>{sentiment.label}</StatusBadge> : null}
            highlighted={changed('sentiment')}
            updatedAt={draft.lastUpdatedAt}
          />
          <PanelField
            label="Topics Discussed"
            value={
              interaction?.products_discussed?.length || interaction?.topics_discussed ? (
                <div className="space-y-1.5">
                  <ProductChips items={interaction.products_discussed} />
                  {interaction.topics_discussed && <p className="text-sm">{interaction.topics_discussed}</p>}
                </div>
              ) : null
            }
            highlighted={changed('products_discussed', 'topics_discussed')}
            updatedAt={draft.lastUpdatedAt}
            className="sm:col-span-2"
          />
          <PanelField
            label="Materials Shared"
            value={materialsShared || null}
            highlighted={changed('brochures_shared', 'promotional_materials')}
            updatedAt={draft.lastUpdatedAt}
          />
          <PanelField
            label="Samples"
            value={samples}
            highlighted={changed('samples_distributed')}
            updatedAt={draft.lastUpdatedAt}
          />
          <PanelField
            label="Follow-up"
            value={followUp}
            highlighted={changed('follow_up_required', 'follow_up_date')}
            updatedAt={draft.lastUpdatedAt}
            className="sm:col-span-2"
          />
          <PanelField
            label="AI Summary"
            value={interaction?.ai_summary}
            highlighted={changed('ai_summary')}
            updatedAt={draft.lastUpdatedAt}
            className="sm:col-span-2"
          />
        </CardContent>
      </Card>
    </section>
  )
}
