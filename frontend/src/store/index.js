import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import interactionDraftReducer from './slices/interactionDraftSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    interactionDraft: interactionDraftReducer,
  },
})
