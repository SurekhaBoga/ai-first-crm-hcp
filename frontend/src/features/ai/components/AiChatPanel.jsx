import { useEffect, useRef, useState } from 'react'
import { Bot, Loader2, Send, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import UserAvatar from '@/components/common/UserAvatar'
import AiResultCard from './AiResultCard'
import { useAiChat } from '@/hooks/queries/useAi'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { getApiErrorMessage } from '@/api/errors'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { draftUpdated } from '@/store/slices/interactionDraftSlice'
import { cn } from '@/lib/utils'

let messageIdCounter = 0
const nextMessageId = () => `msg-${++messageIdCounter}`

const AI_SECTION_FIELDS = ['ai_summary', 'ai_suggestions', 'missing_information', 'confidence_score']

/**
 * The one chat UI in the app: general-purpose on the AI Assistant page,
 * and the AI-first workspace's primary input on Log Interaction. Always
 * classifies through the general /ai/chat endpoint (never a forced-intent
 * one) so every intent — log, edit, summary, search, doctor profile —
 * stays reachable from the same conversation; forcing a single intent
 * would also short-circuit classify_intent's continuation rule (see
 * backend/app/ai/nodes/classify_intent.py) from ever seeing anything else.
 *
 * `syncToDraft` is what turns this from "a chat that happens to log
 * interactions" into the AI-first workspace's primary input: when set,
 * every message threads the current draft's interaction_id from Redux
 * (see store/slices/interactionDraftSlice.js) so the backend continues
 * refining the SAME interaction instead of creating a new one each turn,
 * and every response that returns an interaction is written back to
 * Redux — that's the entire mechanism behind the Interaction Panel
 * updating live as the rep talks.
 */
export default function AiChatPanel({
  doctorId,
  interactionId,
  placeholder,
  suggestions = [],
  onResult,
  syncToDraft = false,
}) {
  const { userId } = useCurrentUser()
  const dispatch = useAppDispatch()
  const draft = useAppSelector((state) => state.interactionDraft)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(undefined)
  const scrollRef = useRef(null)

  const mutation = useAiChat()

  const effectiveInteractionId = syncToDraft ? (draft.interaction?.id ?? interactionId) : interactionId
  const effectiveSessionId = syncToDraft ? (draft.sessionId ?? sessionId) : sessionId

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, mutation.isPending])

  const send = (text) => {
    const messageText = text.trim()
    if (!messageText || mutation.isPending) return

    setMessages((prev) => [...prev, { id: nextMessageId(), role: 'user', content: messageText }])
    setInput('')

    mutation.mutate(
      {
        message: messageText,
        user_id: userId,
        session_id: effectiveSessionId,
        doctor_id: doctorId,
        interaction_id: effectiveInteractionId,
      },
      {
        onSuccess: (response) => {
          setSessionId(response.session_id)
          setMessages((prev) => [
            ...prev,
            { id: nextMessageId(), role: 'assistant', content: response.message, intent: response.intent, data: response.data },
          ])
          if (syncToDraft && response.data?.interaction) {
            const changedFields =
              response.data.fields_changed ??
              (response.intent === 'interaction_summary' ? AI_SECTION_FIELDS : undefined) ??
              Object.keys(response.data.interaction).filter((key) => {
                const value = response.data.interaction[key]
                return value !== null && !(Array.isArray(value) && value.length === 0)
              })
            dispatch(
              draftUpdated({ interaction: response.data.interaction, sessionId: response.session_id, changedFields }),
            )
          }
          onResult?.(response)
        },
        onError: (error) => {
          setMessages((prev) => [
            ...prev,
            { id: nextMessageId(), role: 'assistant', content: getApiErrorMessage(error), isError: true },
          ])
        },
      },
    )
  }

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 px-4" viewportRef={scrollRef}>
        <div className="space-y-4 py-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center gap-3 py-8 text-center">
              <span className="flex h-11 w-11 items-center justify-center rounded-full bg-accent text-accent-foreground">
                <Sparkles className="h-5 w-5" />
              </span>
              <p className="max-w-xs text-sm text-muted-foreground">
                {placeholder ?? 'Describe what happened, in plain English — I’ll take it from there.'}
              </p>
              {suggestions.length > 0 && (
                <div className="flex flex-wrap justify-center gap-1.5">
                  {suggestions.map((suggestion) => (
                    <Button key={suggestion} variant="outline" size="sm" onClick={() => send(suggestion)}>
                      {suggestion}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={cn('flex gap-2.5', message.role === 'user' && 'flex-row-reverse')}>
              {message.role === 'assistant' ? (
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
                  <Bot className="h-4 w-4" />
                </span>
              ) : (
                <UserAvatar size="sm" />
              )}
              <div className={cn('max-w-[85%] space-y-2', message.role === 'user' && 'items-end')}>
                <div
                  className={cn(
                    'rounded-2xl px-3.5 py-2 text-sm',
                    message.role === 'user' && 'rounded-tr-sm bg-primary text-primary-foreground',
                    message.role === 'assistant' && !message.isError && 'rounded-tl-sm bg-muted',
                    message.isError && 'rounded-tl-sm bg-destructive/10 text-destructive',
                  )}
                >
                  {message.content}
                </div>
                {message.data && <AiResultCard intent={message.intent} data={message.data} />}
              </div>
            </div>
          ))}

          {mutation.isPending && (
            <div className="flex items-center gap-2.5">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
                <Bot className="h-4 w-4" />
              </span>
              <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-muted px-3.5 py-2.5">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Thinking…</span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <form
        onSubmit={(event) => {
          event.preventDefault()
          send(input)
        }}
        className="flex items-end gap-2 border-t p-3"
      >
        <Textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              send(input)
            }
          }}
          placeholder="Type a message…"
          rows={1}
          className="max-h-32 min-h-9 flex-1 resize-none py-2"
        />
        <Button type="submit" size="icon" disabled={!input.trim() || mutation.isPending} aria-label="Send message">
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  )
}
