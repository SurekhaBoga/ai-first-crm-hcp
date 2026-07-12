import { cn } from '@/lib/utils'

/**
 * One label/value row on the AI-driven Interaction Panel. `highlighted`
 * re-plays a brief accent flash (see the .animate-field-flash keyframe
 * in index.css) — the panel's only feedback that "the AI just wrote
 * this," since there's no save button or dirty-field state to look at.
 * `updatedAt` is part of the key so the flash re-triggers on every
 * change, not just the first.
 */
export default function PanelField({ label, value, highlighted, updatedAt, className }) {
  const isEmpty = value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)

  return (
    <div
      key={highlighted ? updatedAt : undefined}
      className={cn('rounded-md px-2 py-1.5', highlighted && 'animate-field-flash', className)}
    >
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      {isEmpty ? (
        <p className="text-sm text-muted-foreground/60 italic">Waiting for AI…</p>
      ) : typeof value === 'string' || typeof value === 'number' ? (
        <p className="text-sm break-words">{value}</p>
      ) : (
        value
      )}
    </div>
  )
}
