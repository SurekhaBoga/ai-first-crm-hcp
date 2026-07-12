import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Mail, MapPin, Pencil, Phone, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import DefinitionList from '@/components/common/DefinitionList'
import IconButton from '@/components/common/IconButton'
import StatusBadge from '@/components/common/StatusBadge'
import UserAvatar from '@/components/common/UserAvatar'
import ErrorState from '@/components/data/ErrorState'
import ConfirmDialog from '@/components/data/ConfirmDialog'
import DoctorFormDialog from '@/features/doctors/components/DoctorFormDialog'
import InteractionTimeline from '@/features/interactions/components/InteractionTimeline'
import { useDoctor, useDeleteDoctor } from '@/hooks/queries/useDoctors'
import { useDoctorTimeline } from '@/hooks/queries/useInteractions'
import { DOCTOR_TIER_META } from '@/constants/enums'
import { ROUTES } from '@/constants/routes'

export default function DoctorProfilePage() {
  const { doctorId } = useParams()
  const navigate = useNavigate()
  const [editOpen, setEditOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)

  const deleteDoctor = useDeleteDoctor()
  // Once the delete mutation succeeds, stop refetching this doctor and their
  // timeline — navigation away happens on the next render, but until it does
  // these would otherwise refetch a now-deleted resource and 404.
  const isDeleted = deleteDoctor.isSuccess
  const doctorQuery = useDoctor(doctorId, { enabled: !isDeleted })
  const timelineQuery = useDoctorTimeline(doctorId, { pageSize: 50 }, { enabled: !isDeleted })

  if (doctorQuery.isError) {
    return <ErrorState error={doctorQuery.error} onRetry={doctorQuery.refetch} />
  }

  if (doctorQuery.isLoading || !doctorQuery.data) {
    return (
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Skeleton className="h-64 w-full lg:col-span-1" />
        <Skeleton className="h-96 w-full lg:col-span-2" />
      </div>
    )
  }

  const doctor = doctorQuery.data
  const tier = DOCTOR_TIER_META[doctor.tier]
  const interactions = timelineQuery.data?.items ?? []

  const handleDelete = () => {
    deleteDoctor.mutate(doctor.id, {
      onSuccess: () => navigate(ROUTES.HCPS),
    })
  }

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to={ROUTES.HCPS}>
          <ArrowLeft className="h-4 w-4" />
          Doctor Directory
        </Link>
      </Button>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardContent className="space-y-4 p-5">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-3">
                <UserAvatar name={doctor.full_name} size="lg" />
                <div>
                  <p className="font-medium">{doctor.full_name}</p>
                  <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
                </div>
              </div>
              <StatusBadge tone={tier.tone}>{tier.label}</StatusBadge>
            </div>

            <DefinitionList
              items={[
                { label: 'Institution', value: doctor.institution },
                {
                  label: 'Phone',
                  value: doctor.phone && (
                    <span className="flex items-center gap-1.5">
                      <Phone className="h-3.5 w-3.5 text-muted-foreground" /> {doctor.phone}
                    </span>
                  ),
                },
                {
                  label: 'Email',
                  value: doctor.email && (
                    <span className="flex items-center gap-1.5">
                      <Mail className="h-3.5 w-3.5 text-muted-foreground" /> {doctor.email}
                    </span>
                  ),
                },
                {
                  label: 'Address',
                  value: doctor.address && (
                    <span className="flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5 text-muted-foreground" /> {doctor.address}
                    </span>
                  ),
                },
              ]}
            />

            <div className="flex gap-2 border-t pt-4">
              <Button variant="outline" size="sm" className="flex-1" onClick={() => setEditOpen(true)}>
                <Pencil className="h-4 w-4" />
                Edit
              </Button>
              <IconButton
                label="Delete doctor"
                icon={Trash2}
                variant="outline"
                className="text-destructive hover:text-destructive"
                onClick={() => setDeleteOpen(true)}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between gap-2">
              <div>
                <CardTitle>Interaction history</CardTitle>
                <CardDescription>{interactions.length} logged interaction{interactions.length === 1 ? '' : 's'}</CardDescription>
              </div>
              <Button asChild size="sm">
                <Link to={{ pathname: ROUTES.DASHBOARD, search: `?doctorId=${doctor.id}` }}>
                  <Plus className="h-4 w-4" />
                  Log Interaction
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {timelineQuery.isLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, index) => (
                  <Skeleton key={index} className="h-20 w-full" />
                ))}
              </div>
            ) : (
              <InteractionTimeline interactions={interactions} />
            )}
          </CardContent>
        </Card>
      </div>

      <DoctorFormDialog open={editOpen} onOpenChange={setEditOpen} doctor={doctor} />
      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete this doctor?"
        description={`This removes ${doctor.full_name} from the directory and deletes their logged interactions. This can't be undone.`}
        confirmLabel="Delete doctor"
        isLoading={deleteDoctor.isPending}
        onConfirm={handleDelete}
      />
    </div>
  )
}
