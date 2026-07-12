import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

/**
 * Icon-only action button with a tooltip. `label` doubles as the
 * accessible name (aria-label, for screen readers) and the tooltip text
 * (for sighted mouse users) — an icon-only control needs both.
 */
export default function IconButton({ label, icon: Icon, variant = 'ghost', size = 'icon', className, ...props }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant={variant} size={size} aria-label={label} className={className} {...props}>
          <Icon className="h-4 w-4" />
        </Button>
      </TooltipTrigger>
      <TooltipContent>{label}</TooltipContent>
    </Tooltip>
  )
}
