import { listUsers, createUser } from '@/api/users'

const DEFAULT_REP = {
  full_name: 'Local Rep',
  // EmailStr rejects the reserved `.local` domain, so use a syntactically
  // valid non-sensitive development identity.
  email: 'local.rep@hcpcrm.dev',
  role: 'rep',
}

let pendingIdentity = null

/**
 * Resolves a userId to act as without ever showing a picker: reuses the
 * first existing User if one exists, otherwise silently creates a default
 * local rep. See components/AppShell.jsx — this is what lets the
 * app launch straight into the AI-first workspace with no sign-in gate,
 * while every write (log an interaction, AI chat) still has a real
 * user_id to attribute to — the backend has no auth layer, so *some*
 * User row is still required as the actor.
 */
export function resolveDefaultUserId() {
  if (!pendingIdentity) {
    pendingIdentity = resolveIdentity().catch((error) => {
      // Allow a later Retry action to make a fresh request.
      pendingIdentity = null
      throw error
    })
  }
  return pendingIdentity
}

async function resolveIdentity() {
  const page = await listUsers({ page: 1, pageSize: 1 })
  if (page.items.length > 0) return page.items[0].id

  const user = await createUser(DEFAULT_REP)
  return user.id
}
