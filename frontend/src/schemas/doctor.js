import { z } from 'zod'

/** Mirrors backend/app/schemas/doctor.py (DoctorCreate/DoctorUpdate). */
export const doctorFormSchema = z.object({
  full_name: z.string().trim().min(1, 'Full name is required.').max(160),
  specialty: z.string().trim().min(1, 'Specialty is required.').max(120),
  institution: z.string().trim().max(200).optional().or(z.literal('')),
  tier: z.enum(['A', 'B', 'C']),
  phone: z.string().trim().max(30).optional().or(z.literal('')),
  email: z.string().trim().email('Enter a valid email address.').max(160).optional().or(z.literal('')),
  address: z.string().trim().max(255).optional().or(z.literal('')),
})

export const doctorFormDefaults = {
  full_name: '',
  specialty: '',
  institution: '',
  tier: 'B',
  phone: '',
  email: '',
  address: '',
}
