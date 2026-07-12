import { Link } from 'react-router-dom'
import { Mail, MapPin, Phone } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import StatusBadge from '@/components/common/StatusBadge'
import UserAvatar from '@/components/common/UserAvatar'
import { DOCTOR_TIER_META } from '@/constants/enums'
import { buildDoctorDetailPath } from '@/constants/routes'

export default function DoctorCard({ doctor }) {
  const tier = DOCTOR_TIER_META[doctor.tier]

  return (
    <Link to={buildDoctorDetailPath(doctor.id)}>
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardContent className="flex h-full flex-col gap-3 p-5">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-3">
              <UserAvatar name={doctor.full_name} size="lg" />
              <div className="min-w-0">
                <p className="truncate font-medium">{doctor.full_name}</p>
                <p className="truncate text-sm text-muted-foreground">{doctor.specialty}</p>
              </div>
            </div>
            <StatusBadge tone={tier.tone}>{tier.label}</StatusBadge>
          </div>

          {doctor.institution && <p className="truncate text-sm text-muted-foreground">{doctor.institution}</p>}

          <div className="mt-auto space-y-1 border-t pt-3 text-xs text-muted-foreground">
            {doctor.phone && (
              <p className="flex items-center gap-1.5">
                <Phone className="h-3.5 w-3.5" /> {doctor.phone}
              </p>
            )}
            {doctor.email && (
              <p className="flex items-center gap-1.5 truncate">
                <Mail className="h-3.5 w-3.5 shrink-0" /> <span className="truncate">{doctor.email}</span>
              </p>
            )}
            {doctor.address && (
              <p className="flex items-center gap-1.5 truncate">
                <MapPin className="h-3.5 w-3.5 shrink-0" /> <span className="truncate">{doctor.address}</span>
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
