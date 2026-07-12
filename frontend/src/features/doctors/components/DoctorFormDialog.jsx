import { useEffect } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { doctorFormDefaults, doctorFormSchema } from '@/schemas/doctor'
import { DOCTOR_TIERS } from '@/constants/enums'
import { useCreateDoctor, useUpdateDoctor } from '@/hooks/queries/useDoctors'

export default function DoctorFormDialog({ open, onOpenChange, doctor, onSaved }) {
  const isEditing = Boolean(doctor)
  const createDoctor = useCreateDoctor()
  const updateDoctor = useUpdateDoctor(doctor?.id)
  const mutation = isEditing ? updateDoctor : createDoctor

  const form = useForm({
    resolver: zodResolver(doctorFormSchema),
    defaultValues: doctorFormDefaults,
  })

  useEffect(() => {
    if (!open) return
    form.reset(
      doctor
        ? {
            full_name: doctor.full_name,
            specialty: doctor.specialty,
            institution: doctor.institution ?? '',
            tier: doctor.tier,
            phone: doctor.phone ?? '',
            email: doctor.email ?? '',
            address: doctor.address ?? '',
          }
        : doctorFormDefaults,
    )
  }, [open, doctor, form])

  const onSubmit = (values) => {
    const payload = {
      ...values,
      institution: values.institution || null,
      phone: values.phone || null,
      email: values.email || null,
      address: values.address || null,
    }
    mutation.mutate(payload, {
      onSuccess: (savedDoctor) => {
        onOpenChange(false)
        onSaved?.(savedDoctor)
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit doctor' : 'Add a doctor'}</DialogTitle>
          <DialogDescription>
            {isEditing ? "Update this doctor's directory details." : 'Adds a new HCP to the directory.'}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="full_name"
                render={({ field }) => (
                  <FormItem className="sm:col-span-2">
                    <FormLabel>Full name</FormLabel>
                    <FormControl>
                      <Input placeholder="Dr. Meera Nair" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="specialty"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Specialty</FormLabel>
                    <FormControl>
                      <Input placeholder="Cardiology" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tier"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tier</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {DOCTOR_TIERS.map((tier) => (
                          <SelectItem key={tier.value} value={tier.value}>
                            {tier.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="institution"
                render={({ field }) => (
                  <FormItem className="sm:col-span-2">
                    <FormLabel>Institution</FormLabel>
                    <FormControl>
                      <Input placeholder="Fortis Heart Institute" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone</FormLabel>
                    <FormControl>
                      <Input placeholder="+91 98450 11234" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="meera.nair@fortis-health.example" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem className="sm:col-span-2">
                    <FormLabel>Address</FormLabel>
                    <FormControl>
                      <Input placeholder="Bannerghatta Road, Bengaluru" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                {isEditing ? 'Save changes' : 'Create'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
