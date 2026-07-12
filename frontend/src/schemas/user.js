import { z } from 'zod'

/** Mirrors backend/app/schemas/user.py (UserCreate/UserUpdate). */
export const userFormSchema = z.object({
  full_name: z.string().trim().min(1, 'Full name is required.').max(120),
  email: z.string().trim().min(1, 'Email is required.').email('Enter a valid email address.'),
  role: z.enum(['rep', 'manager', 'admin']),
  territory: z.string().trim().max(120).optional().or(z.literal('')),
})

export const userFormDefaults = {
  full_name: '',
  email: '',
  role: 'rep',
  territory: '',
}
