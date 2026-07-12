import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import * as interactionsApi from '@/api/interactions'
import { queryKeys } from '@/api/queryKeys'
import { buildOptimisticDeleteHandlers, invalidateAfterSettle } from '@/lib/optimisticListDelete'

export function useDoctorTimeline(doctorId, params = {}, options = {}) {
  return useQuery({
    queryKey: queryKeys.interactions.timeline(doctorId, params),
    queryFn: () => interactionsApi.getDoctorTimeline(doctorId, params),
    enabled: Boolean(doctorId) && (options.enabled ?? true),
    placeholderData: keepPreviousData,
  })
}

export function useInteraction(interactionId, options = {}) {
  return useQuery({
    queryKey: queryKeys.interactions.detail(interactionId),
    queryFn: () => interactionsApi.getInteraction(interactionId),
    enabled: Boolean(interactionId) && (options.enabled ?? true),
  })
}

function invalidateInteractionLists(queryClient, interaction) {
  queryClient.invalidateQueries({ queryKey: queryKeys.interactions.all })
  if (interaction?.doctor_id) {
    queryClient.invalidateQueries({ queryKey: ['interactions', 'timeline', interaction.doctor_id] })
  }
}

export function useUpdateInteraction(interactionId) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload) => interactionsApi.updateInteraction(interactionId, payload),
    onSuccess: (interaction) => {
      invalidateInteractionLists(queryClient, interaction)
      queryClient.setQueryData(queryKeys.interactions.detail(interactionId), interaction)
      toast.success('Interaction updated.')
    },
  })
}

export function useDeleteInteraction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: interactionsApi.deleteInteraction,
    ...buildOptimisticDeleteHandlers({
      queryClient,
      listKeyPrefix: queryKeys.interactions.all,
      getItemId: (interaction) => interaction.id,
    }),
    onSuccess: () => toast.success('Interaction deleted.'),
    onSettled: (_data, _error, interactionId) =>
      invalidateAfterSettle(queryClient, queryKeys.interactions.all, [queryKeys.interactions.detail(interactionId)]),
  })
}
