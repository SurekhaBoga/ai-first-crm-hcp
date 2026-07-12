import { cn } from '@/lib/utils'

/**
 * Label/value pairs, the recurring layout for read-only record details
 * (doctor info, interaction summary, follow-up info). `items` is
 * `{ label, value, span? }[]`; `span: 2` lets one row take the full width
 * of a two-column grid.
 */
export default function DefinitionList({ items, columns = 1 }) {
  return (
    <dl
      className={cn(
        'grid gap-x-6 gap-y-4',
        columns === 2 ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1',
      )}
    >
      {items.map(({ label, value, span }) => (
        <div key={label} className={span === 2 && columns === 2 ? 'sm:col-span-2' : undefined}>
          <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{label}</dt>
          <dd className="mt-1 text-sm text-foreground">{value ?? '—'}</dd>
        </div>
      ))}
    </dl>
  )
}
