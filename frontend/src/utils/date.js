export function subDays(date, days) {
  const result = new Date(date)
  result.setDate(result.getDate() - days)
  return result
}

/**
 * Accepts either a bare date ("YYYY-MM-DD", e.g. follow_up_date) or a
 * full ISO datetime (e.g. interaction_date, created_at). Bare dates get
 * a local-midnight anchor so they don't shift a day backward in
 * negative-UTC-offset timezones.
 */
export function formatDate(isoDateOrDateTime) {
  if (!isoDateOrDateTime) return '—'
  const value = isoDateOrDateTime.length === 10 ? `${isoDateOrDateTime}T00:00:00` : isoDateOrDateTime
  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

/** ISO datetime -> value a native <input type="datetime-local"> accepts. */
export function toDateTimeLocalValue(isoDateTime) {
  if (!isoDateTime) return ''
  const date = new Date(isoDateTime)
  const offsetMs = date.getTimezoneOffset() * 60_000
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16)
}

/** The reverse — <input type="datetime-local"> value -> ISO string. */
export function fromDateTimeLocalValue(value) {
  if (!value) return null
  return new Date(value).toISOString()
}

export function formatDateTime(isoDateTime) {
  if (!isoDateTime) return '—'
  return new Date(isoDateTime).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
