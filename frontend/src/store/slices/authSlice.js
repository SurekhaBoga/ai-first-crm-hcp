import { createSlice } from '@reduxjs/toolkit'

const STORAGE_KEY = 'hcp-crm.currentUserId'

const initialState = {
  userId: localStorage.getItem(STORAGE_KEY),
}

/**
 * There is no credentialed session here — the backend has no auth layer
 * at all. `userId` identifies which User record every write (log an
 * interaction, AI chat) is attributed to; it's resolved silently on
 * launch, never picked by the rep. See src/components/AppShell.jsx and
 * src/services/autoIdentity.js. `signOut` exists only as a self-healing
 * hook for useCurrentUser.js (if the resolved user is ever deleted
 * elsewhere, clearing it here lets AppShell resolve a fresh one).
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    signIn(state, action) {
      state.userId = action.payload
      localStorage.setItem(STORAGE_KEY, action.payload)
    },
    signOut(state) {
      state.userId = null
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})

export const { signIn, signOut } = authSlice.actions
export default authSlice.reducer
