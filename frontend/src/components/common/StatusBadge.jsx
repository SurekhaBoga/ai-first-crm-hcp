import { cn } from '@/lib/utils'

// Semantic status tones, reserved for state — never reused as decoration.
// Distinct from the brand accent (teal) used for primary actions/links.
const TONE_STYLES = {
  neutral: 'bg-muted text-muted-foreground',
  positive: 'bg-success/10 text-success',
  negative: 'bg-destructive/10 text-destructive',
  warning: 'bg-warning/15 text-warning-foreground',
  info: 'bg-info/10 text-info',
  accent: 'bg-primary text-primary-foreground',
}

/**
 * Pill badge for enum/status values (sentiment, follow-up status, tier,
 * source). Shares shadcn Badge's shape so it sits visually consistent
 * next to it, but carries our own semantic tone palette.
 */
export default function StatusBadge({ tone = 'neutral', className, children }) {
  return (
    <span
      className={cn(
        'inline-flex h-5 w-fit shrink-0 items-center justify-center gap-1 rounded-full border border-transparent px-2 py-0.5 text-xs font-medium whitespace-nowrap',
        TONE_STYLES[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}
