import { useMutation, useQueryClient } from '@tanstack/react-query'
import * as aiApi from '@/api/ai'
import { queryKeys } from '@/api/queryKeys'

/**
 * All six /ai/* endpoints are modeled as mutations, not queries — every
 * one of them is triggered by an explicit user action (send a chat
 * message, click "Generate Summary") and has a side effect on the server
 * (it writes to chat_history), so re-fetching them implicitly the way a
 * query would is the wrong mental model. Callers that want the result
 * cached/reused do so themselves via onSuccess.
 */

function invalidateAfterAiWrite(queryClient, response) {
  const interaction = response?.data?.interaction
  if (!interaction) return
  queryClient.invalidateQueries({ queryKey: queryKeys.interactions.all })
  queryClient.invalidateQueries({ queryKey: ['interactions', 'timeline', interaction.doctor_id] })
  queryClient.invalidateQueries({ queryKey: queryKeys.interactions.detail(interaction.id) })
}

export function useAiChat() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: aiApi.aiChat,
    onSuccess: (response) => invalidateAfterAiWrite(queryClient, response),
  })
}

export function useAiLog() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: aiApi.aiLog,
    onSuccess: (response) => invalidateAfterAiWrite(queryClient, response),
  })
}

export function useAiEdit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: aiApi.aiEdit,
    onSuccess: (response) => invalidateAfterAiWrite(queryClient, response),
  })
}

export function useAiSearch() {
  return useMutation({ mutationFn: aiApi.aiSearch })
}

export function useAiDoctorProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ doctorId, userId }) => aiApi.getAiDoctorProfile(doctorId, userId),
    onSuccess: (response, { doctorId }) => {
      queryClient.setQueryData(queryKeys.ai.doctorProfile(doctorId), response)
    },
  })
}

export function useAiSummary() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ interactionId, userId }) => aiApi.getAiSummary(interactionId, userId),
    onSuccess: (response, { interactionId }) => {
      queryClient.setQueryData(queryKeys.ai.summary(interactionId), response)
    },
  })
}
