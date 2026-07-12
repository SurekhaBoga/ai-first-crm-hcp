/**
 * Mirrors the Python enums in backend/app/models/*.py — the single
 * source of truth for every enum's options (for <Select>s), display
 * labels, and (where relevant) the StatusBadge tone it renders with.
 */
export const DOCTOR_TIERS = [
  { value: 'A', label: 'Tier A', tone: 'accent' },
  { value: 'B', label: 'Tier B', tone: 'positive' },
  { value: 'C', label: 'Tier C', tone: 'neutral' },
]

export const INTERACTION_TYPES = [
  { value: 'visit', label: 'In-Person Visit' },
  { value: 'call', label: 'Phone Call' },
  { value: 'video', label: 'Video Call' },
  { value: 'email', label: 'Email' },
  { value: 'conference', label: 'Conference' },
]

export const SENTIMENTS = [
  { value: 'positive', label: 'Positive', tone: 'positive' },
  { value: 'neutral', label: 'Neutral', tone: 'neutral' },
  { value: 'negative', label: 'Negative', tone: 'negative' },
]

export const INTEREST_LEVELS = [
  { value: 'low', label: 'Low', tone: 'neutral' },
  { value: 'medium', label: 'Medium', tone: 'info' },
  { value: 'high', label: 'High', tone: 'positive' },
]

export const INTERACTION_SOURCES = [
  { value: 'manual', label: 'Manual entry' },
  { value: 'ai_chat', label: 'AI chat' },
]

export const FOLLOW_UP_STATUSES = [
  { value: 'none', label: 'No follow-up', tone: 'neutral' },
  { value: 'upcoming', label: 'Upcoming', tone: 'info' },
  { value: 'overdue', label: 'Overdue', tone: 'negative' },
]

function toMap(list, pick = (item) => item.label) {
  return Object.fromEntries(list.map((item) => [item.value, pick(item)]))
}

export const DOCTOR_TIER_LABELS = toMap(DOCTOR_TIERS)
export const INTERACTION_TYPE_LABELS = toMap(INTERACTION_TYPES)
export const SENTIMENT_LABELS = toMap(SENTIMENTS)
export const INTERACTION_SOURCE_LABELS = toMap(INTERACTION_SOURCES)

export const DOCTOR_TIER_META = toMap(DOCTOR_TIERS, (item) => item)
export const SENTIMENT_META = toMap(SENTIMENTS, (item) => item)
export const FOLLOW_UP_STATUS_META = toMap(FOLLOW_UP_STATUSES, (item) => item)
export const INTEREST_LEVEL_META = toMap(INTEREST_LEVELS, (item) => item)

/** 'none' | 'overdue' | 'upcoming' — derived from "today", not stored. */
export function getFollowUpStatus(followUpDate, followUpRequired) {
  if (!followUpRequired || !followUpDate) return 'none'
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return new Date(`${followUpDate}T00:00:00`) < today ? 'overdue' : 'upcoming'
}
