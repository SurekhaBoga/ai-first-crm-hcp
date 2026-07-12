import { ChevronLeft, ChevronRight } from 'lucide-react'
import IconButton from '@/components/common/IconButton'
import { cn } from '@/lib/utils'

/**
 * Pagination control for server-paginated lists. The caller owns `page`
 * state; this just renders controls and "Showing 1-10 of 42" range text.
 */
export default function Pagination({ page, pageSize, totalItems, onPageChange, className }) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))
  const rangeStart = totalItems === 0 ? 0 : (page - 1) * pageSize + 1
  const rangeEnd = Math.min(page * pageSize, totalItems)

  return (
    <div className={cn('flex flex-col items-center justify-between gap-3 border-t px-5 py-3 sm:flex-row', className)}>
      <p className="text-sm text-muted-foreground">
        Showing <span className="font-medium text-foreground">{rangeStart}</span>–
        <span className="font-medium text-foreground">{rangeEnd}</span> of{' '}
        <span className="font-medium text-foreground">{totalItems}</span>
      </p>
      <div className="flex items-center gap-1">
        <IconButton
          label="Previous page"
          icon={ChevronLeft}
          variant="outline"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        />
        <span className="px-2 text-sm text-muted-foreground tabular-nums">
          Page {page} of {totalPages}
        </span>
        <IconButton
          label="Next page"
          icon={ChevronRight}
          variant="outline"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        />
      </div>
    </div>
  )
}
