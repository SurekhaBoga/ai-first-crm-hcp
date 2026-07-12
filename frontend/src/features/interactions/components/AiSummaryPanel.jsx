import { AlertTriangle, Gauge, Lightbulb, ListChecks, Loader2, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import StatusBadge from '@/components/common/StatusBadge'
import { useAiSummary } from '@/hooks/queries/useAi'
import { useCurrentUser } from '@/hooks/useCurrentUser'

/**
 * The "AI Interaction Summary" surface — a single GET /ai/summary/{id}
 * call (no LangGraph classification step, forced intent) rendered as its
 * own card rather than a chat bubble, since there's no back-and-forth
 * here: one interaction in, one summary out.
 *
 * The record persists its own ai_summary/ai_suggestions/missing_information
 * /confidence_score (see backend/app/ai/nodes/interaction_summary.py), so
 * a summary generated earlier — even from the AI workspace before this
 * interaction was saved — shows immediately without re-generating. A
 * live mutation result (freshly generated/regenerated in this session)
 * always takes priority over the persisted one.
 */
export default function AiSummaryPanel({ interaction }) {
  const { userId } = useCurrentUser()
  const summaryMutation = useAiSummary()

  const live = summaryMutation.data
  const persisted = interaction.ai_summary
    ? {
        summary: interaction.ai_summary,
        key_insights: [],
        follow_up_recommendations: interaction.ai_suggestions,
        missing_information: interaction.missing_information,
        confidence_score: interaction.confidence_score,
      }
    : null
  const result = live?.success ? live.data : persisted

  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          AI summary
        </CardTitle>
        <CardDescription>Generated from this interaction and recent history with the same doctor.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!result && !live && (
          <Button
            size="sm"
            variant="outline"
            disabled={summaryMutation.isPending}
            onClick={() => summaryMutation.mutate({ interactionId: interaction.id, userId })}
          >
            {summaryMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Generate summary
          </Button>
        )}

        {live && !live.success && <p className="text-sm text-destructive">{live.error}</p>}

        {result && (
          <div className="space-y-4 text-sm">
            <p>{result.summary}</p>
            {result.key_insights?.length > 0 && (
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase">
                  <Lightbulb className="h-3.5 w-3.5" /> Key insights
                </p>
                <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                  {result.key_insights.map((insight) => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.follow_up_recommendations?.length > 0 && (
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase">
                  <ListChecks className="h-3.5 w-3.5" /> AI suggestions
                </p>
                <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                  {result.follow_up_recommendations.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.missing_information?.length > 0 && (
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase">
                  <AlertTriangle className="h-3.5 w-3.5" /> Missing information
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {result.missing_information.map((field) => (
                    <StatusBadge key={field} tone="warning">
                      {field.replaceAll('_', ' ')}
                    </StatusBadge>
                  ))}
                </div>
              </div>
            )}
            {result.confidence_score != null && (
              <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Gauge className="h-3.5 w-3.5" />
                Confidence: {Math.round(result.confidence_score * 100)}%
              </p>
            )}
            <Button
              size="sm"
              variant="ghost"
              disabled={summaryMutation.isPending}
              onClick={() => summaryMutation.mutate({ interactionId: interaction.id, userId })}
            >
              {summaryMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Regenerate
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
