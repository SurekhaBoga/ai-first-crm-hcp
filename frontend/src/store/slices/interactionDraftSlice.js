import { createSlice } from '@reduxjs/toolkit'

/**
 * The AI-first "current interaction" — the single source of truth the
 * Interaction Panel renders from. Every successful log_interaction /
 * edit_interaction / interaction_summary response from the AI Assistant
 * (see features/ai/components/AiChatPanel.jsx) dispatches `draftUpdated`
 * here, which is what makes the panel update live as the conversation
 * progresses, with no page refresh and no manual form.
 *
 * `sessionId` and `interaction.id` are threaded back into every
 * subsequent /ai/chat request so the backend treats follow-up messages as
 * continuing this draft rather than starting a new interaction (see
 * backend/app/ai/nodes/classify_intent.py's `_continue_draft_if_open`).
 */
const initialState = {
  interaction: null,
  sessionId: null,
  lastChangedFields: [],
  lastUpdatedAt: null,
}

const interactionDraftSlice = createSlice({
  name: 'interactionDraft',
  initialState,
  reducers: {
    draftUpdated(state, action) {
      const { interaction, sessionId, changedFields = [] } = action.payload
      state.interaction = interaction
      if (sessionId) state.sessionId = sessionId
      state.lastChangedFields = changedFields
      state.lastUpdatedAt = Date.now()
    },
    sessionStarted(state, action) {
      state.sessionId = action.payload
    },
    draftCleared() {
      return initialState
    },
  },
})

export const { draftUpdated, sessionStarted, draftCleared } = interactionDraftSlice.actions
export default interactionDraftSlice.reducer
