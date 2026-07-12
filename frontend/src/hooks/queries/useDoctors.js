import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import * as doctorsApi from '@/api/doctors'
import { queryKeys } from '@/api/queryKeys'
import { buildOptimisticDeleteHandlers, invalidateAfterSettle } from '@/lib/optimisticListDelete'

export function useDoctors(params = {}) {
  return useQuery({
    queryKey: queryKeys.doctors.list(params),
    queryFn: () => doctorsApi.listDoctors(params),
    placeholderData: keepPreviousData,
  })
}

export function useSearchDoctors(params, options = {}) {
  return useQuery({
    queryKey: queryKeys.doctors.search(params),
    queryFn: () => doctorsApi.searchDoctors(params),
    enabled: Boolean(params.q) && (options.enabled ?? true),
    placeholderData: keepPreviousData,
  })
}

export function useDoctor(doctorId, options = {}) {
  return useQuery({
    queryKey: queryKeys.doctors.detail(doctorId),
    queryFn: () => doctorsApi.getDoctor(doctorId),
    enabled: Boolean(doctorId) && (options.enabled ?? true),
  })
}

export function useCreateDoctor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: doctorsApi.createDoctor,
    onSuccess: (doctor) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.doctors.all })
      toast.success(`${doctor.full_name} added to the directory.`)
    },
  })
}

export function useUpdateDoctor(doctorId) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload) => doctorsApi.updateDoctor(doctorId, payload),
    onSuccess: (doctor) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.doctors.all })
      queryClient.setQueryData(queryKeys.doctors.detail(doctorId), doctor)
      toast.success('Doctor profile updated.')
    },
  })
}

export function useDeleteDoctor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: doctorsApi.deleteDoctor,
    ...buildOptimisticDeleteHandlers({
      queryClient,
      listKeyPrefix: queryKeys.doctors.all,
      getItemId: (doctor) => doctor.id,
    }),
    onSuccess: () => toast.success('Doctor removed from the directory.'),
    onSettled: (_data, _error, doctorId) => {
      // Exclude the deleted doctor's own detail/timeline queries — the
      // profile page may still be mid-unmount when this runs, and
      // invalidating a still-active query for a now-deleted doctor would
      // refetch it and get back a 404.
      invalidateAfterSettle(queryClient, queryKeys.doctors.all, [queryKeys.doctors.detail(doctorId)])
      queryClient.invalidateQueries({
        queryKey: queryKeys.interactions.all,
        predicate: (query) => !(query.queryKey[1] === 'timeline' && query.queryKey[2] === doctorId),
      })
    },
  })
}
