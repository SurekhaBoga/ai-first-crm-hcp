import { useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { PlusCircle, Save, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import AiChatPanel from '@/features/ai/components/AiChatPanel'
import InteractionPanel from '@/features/interactions/components/InteractionPanel'
import { useUpdateInteraction } from '@/hooks/queries/useInteractions'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { draftCleared } from '@/store/slices/interactionDraftSlice'
import { buildInteractionDetailPath } from '@/constants/routes'

const AI_SUGGESTIONS = [
  'I met Dr. Nair this morning for a 30 minute visit',
  'Had a call with Dr. Nair about Cardiozin dosing',
]

/**
 * The AI-first interaction workspace — the assignment's primary journey.
 * There is deliberately no manual form here: the left panel is a
 * read-only view of interactionDraft (Redux), populated exclusively by
 * LangGraph tool executions the chat on the right triggers. See
 * AiChatPanel's `syncToDraft` prop and store/slices/interactionDraftSlice
 * for the mechanism. Manual field editing still exists, but only as a
 * deliberate secondary path on the Interaction Details page after a
 * record is saved — never as how a record gets created.
 */
export default function LogInteractionPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const draft = useAppSelector((state) => state.interactionDraft)
  const [workspaceKey, setWorkspaceKey] = useState(0)

  const preselectedDoctorId = searchParams.get('doctorId') ?? ''
  const interaction = draft.interaction
  const updateInteraction = useUpdateInteraction(interaction?.id)

  const handleSave = () => {
    updateInteraction.mutate(
      { status: 'submitted' },
      {
        onSuccess: (saved) => {
          toast.success('Interaction saved.')
          dispatch(draftCleared())
          navigate(buildInteractionDetailPath(saved.id))
        },
      },
    )
  }

  const handleNewInteraction = () => {
    dispatch(draftCleared())
    setWorkspaceKey((key) => key + 1)
  }

  return (
    <div className="flex h-[calc(100vh-6.5rem)] flex-col gap-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Log Interaction</h2>
          <p className="text-sm text-muted-foreground">
            Just describe the visit — the AI builds the record on the left as you talk.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleNewInteraction} disabled={!interaction}>
            <PlusCircle className="h-4 w-4" />
            New Interaction
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            disabled={!interaction || interaction.status !== 'draft' || updateInteraction.isPending}
          >
            <Save className="h-4 w-4" />
            {updateInteraction.isPending ? 'Saving…' : 'Save'}
          </Button>
        </div>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 lg:grid-cols-2">
        <InteractionPanel />

        <Card className="flex min-h-0 flex-col">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="h-4 w-4 text-primary" />
              AI Assistant
            </CardTitle>
            <CardDescription>Describe the visit in plain English — corrections work too.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden p-0">
            <AiChatPanel
              key={workspaceKey}
              doctorId={preselectedDoctorId || undefined}
              suggestions={AI_SUGGESTIONS}
              placeholder="Tell me about the visit and I'll build the record for you."
              syncToDraft
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
