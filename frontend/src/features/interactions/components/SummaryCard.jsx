import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import DefinitionList from '@/components/common/DefinitionList'
import StatusBadge from '@/components/common/StatusBadge'
import {
  INTERACTION_TYPE_LABELS,
  INTERACTION_SOURCE_LABELS,
  SENTIMENT_META,
  INTEREST_LEVEL_META,
} from '@/constants/enums'
import { formatDateTime } from '@/utils/date'

function FreeTextBlock({ label, value }) {
  if (!value) return null
  return (
    <div>
      <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{label}</p>
      <p className="mt-1 text-sm whitespace-pre-wrap">{value}</p>
    </div>
  )
}

export default function SummaryCard({ interaction }) {
  const sentiment = interaction.sentiment ? SENTIMENT_META[interaction.sentiment] : null
  const interest = interaction.interest_level ? INTEREST_LEVEL_META[interaction.interest_level] : null

  return (
    <Card>
      <CardHeader>
        <CardTitle>Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <DefinitionList
          columns={2}
          items={[
            { label: 'Type', value: INTERACTION_TYPE_LABELS[interaction.interaction_type] },
            { label: 'When', value: formatDateTime(interaction.interaction_date) },
            { label: 'Duration', value: interaction.duration_minutes ? `${interaction.duration_minutes} min` : null },
            { label: 'Location', value: interaction.location },
            { label: 'Attendees', value: interaction.attendees },
            { label: 'Purpose', value: interaction.purpose, span: 2 },
            {
              label: 'Products discussed',
              value: interaction.products_discussed.length > 0 ? interaction.products_discussed.join(', ') : null,
              span: 2,
            },
            { label: 'Samples distributed', value: interaction.samples_distributed ? 'Yes' : 'No' },
            { label: 'Brochures shared', value: interaction.brochures_shared },
            { label: 'Promotional material', value: interaction.promotional_materials, span: 2 },
            {
              label: 'Sentiment',
              value: sentiment ? <StatusBadge tone={sentiment.tone}>{sentiment.label}</StatusBadge> : null,
            },
            {
              label: 'Interest level',
              value: interest ? <StatusBadge tone={interest.tone}>{interest.label}</StatusBadge> : null,
            },
            { label: 'Next best action', value: interaction.next_best_action, span: 2 },
            { label: 'Logged via', value: INTERACTION_SOURCE_LABELS[interaction.source] },
          ]}
        />
        <FreeTextBlock label="Discussion notes" value={interaction.discussion_points} />
        <FreeTextBlock label="Topics discussed" value={interaction.topics_discussed} />
        <FreeTextBlock label="Clinical evidence" value={interaction.clinical_evidence} />
        <FreeTextBlock label="Questions raised" value={interaction.questions_raised} />
        <FreeTextBlock label="Objections" value={interaction.objections} />
        <FreeTextBlock label="Competitor discussion" value={interaction.competitor_discussion} />
      </CardContent>
    </Card>
  )
}
