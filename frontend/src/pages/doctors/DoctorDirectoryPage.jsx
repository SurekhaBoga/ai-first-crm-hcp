import { useMemo, useState } from 'react'
import { ArrowDownAZ, ArrowUpZA, Plus, Search, Stethoscope } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import EmptyState from '@/components/data/EmptyState'
import ErrorState from '@/components/data/ErrorState'
import Pagination from '@/components/common/Pagination'
import DoctorCard from '@/features/doctors/components/DoctorCard'
import DoctorFormDialog from '@/features/doctors/components/DoctorFormDialog'
import { useDoctors, useSearchDoctors } from '@/hooks/queries/useDoctors'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'
import { DOCTOR_TIERS } from '@/constants/enums'

const PAGE_SIZE = 12

export default function DoctorDirectoryPage() {
  const [query, setQuery] = useState('')
  const [tier, setTier] = useState('all')
  const [sortBy, setSortBy] = useState('name-asc')
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)

  const debouncedQuery = useDebouncedValue(query, 300)
  const isSearching = debouncedQuery.trim().length > 0

  const listQuery = useDoctors({ page, pageSize: PAGE_SIZE, tier: tier === 'all' ? undefined : tier })
  const searchQuery = useSearchDoctors(
    { q: debouncedQuery, page, pageSize: PAGE_SIZE },
    { enabled: isSearching },
  )

  const activeQuery = isSearching ? searchQuery : listQuery
  const total = activeQuery.data?.total ?? 0

  // The API always orders by name ascending and has no `sort` param, so
  // sorting is applied client-side over the current page — consistent
  // with how type/sentiment filtering on Interaction History works.
  const doctors = useMemo(() => {
    const items = [...(activeQuery.data?.items ?? [])]
    if (sortBy === 'name-desc') items.reverse()
    if (sortBy === 'tier') items.sort((a, b) => a.tier.localeCompare(b.tier))
    return items
  }, [activeQuery.data, sortBy])

  const handleQueryChange = (value) => {
    setQuery(value)
    setPage(1)
  }

  const handleTierChange = (value) => {
    setTier(value)
    setPage(1)
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Doctor Directory</h2>
          <p className="text-sm text-muted-foreground">Browse and manage the HCPs in your territory.</p>
        </div>
        <Button size="sm" onClick={() => setFormOpen(true)}>
          <Plus className="h-4 w-4" />
          Add Doctor
        </Button>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute top-1/2 left-2.5 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(event) => handleQueryChange(event.target.value)}
            placeholder="Search by name, specialty, or institution…"
            className="pl-8"
            aria-label="Search doctors"
          />
        </div>
        <Select value={tier} onValueChange={handleTierChange} disabled={isSearching}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="All tiers" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All tiers</SelectItem>
            {DOCTOR_TIERS.map((t) => (
              <SelectItem key={t.value} value={t.value}>
                {t.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-full sm:w-44">
            <SelectValue placeholder="Sort" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name-asc">
              <ArrowDownAZ className="h-4 w-4" /> Name (A–Z)
            </SelectItem>
            <SelectItem value="name-desc">
              <ArrowUpZA className="h-4 w-4" /> Name (Z–A)
            </SelectItem>
            <SelectItem value="tier">Tier</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {activeQuery.isError && <ErrorState error={activeQuery.error} onRetry={activeQuery.refetch} />}

      {!activeQuery.isError && (
        <>
          {activeQuery.isLoading ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <Skeleton key={index} className="h-44 w-full rounded-xl" />
              ))}
            </div>
          ) : doctors.length === 0 ? (
            <Card>
              <EmptyState
                icon={Stethoscope}
                title="No doctors found"
                description={
                  isSearching || tier !== 'all'
                    ? 'Try a different search term or clear the tier filter.'
                    : 'Add your first doctor to start logging interactions.'
                }
                action={
                  !isSearching && tier === 'all' ? (
                    <Button size="sm" onClick={() => setFormOpen(true)}>
                      <Plus className="h-4 w-4" />
                      Add Doctor
                    </Button>
                  ) : undefined
                }
              />
            </Card>
          ) : (
            <>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {doctors.map((doctor) => (
                  <DoctorCard key={doctor.id} doctor={doctor} />
                ))}
              </div>
              <Card>
                <CardContent className="p-0">
                  <Pagination page={page} pageSize={PAGE_SIZE} totalItems={total} onPageChange={setPage} />
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}

      <DoctorFormDialog open={formOpen} onOpenChange={setFormOpen} />
    </div>
  )
}
