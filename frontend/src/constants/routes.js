/**
 * Route path constants — trimmed to exactly what the assignment needs:
 * the AI-first Log Interaction workspace (home), the Doctor Directory
 * (HCPs must exist somewhere for the AI to resolve them against), and
 * read-only Interaction Details (where "Save" lands).
 */
export const ROUTES = {
  // Home — the AI-first Log HCP Interaction workspace. The only landing
  // page; there is no sign-in gate (see components/AppShell.jsx).
  DASHBOARD: '/',
  HCPS: '/doctors',
  HCP_DETAIL: '/doctors/:doctorId',
  INTERACTION_DETAIL: '/interactions/:interactionId',
}

export function buildDoctorDetailPath(doctorId) {
  return `/doctors/${doctorId}`
}

export function buildInteractionDetailPath(interactionId) {
  return `/interactions/${interactionId}`
}
