import apiClient from '@/services/apiClient'

/**
 * Every call here hits the LangGraph-orchestrated /ai/* surface. All of
 * them return the same shape: { session_id, intent, success, message,
 * data, error } — see AiChatPanel/useAi* for how that's consumed.
 */

export async function aiChat(payload) {
  const { data } = await apiClient.post('/ai/chat', payload)
  return data
}

export async function aiLog(payload) {
  const { data } = await apiClient.post('/ai/log', payload)
  return data
}

export async function aiEdit(payload) {
  const { data } = await apiClient.post('/ai/edit', payload)
  return data
}

export async function aiSearch(payload) {
  const { data } = await apiClient.post('/ai/search', payload)
  return data
}

export async function getAiDoctorProfile(doctorId, userId) {
  const { data } = await apiClient.get(`/ai/doctor/${doctorId}`, { params: { user_id: userId } })
  return data
}

export async function getAiSummary(interactionId, userId) {
  const { data } = await apiClient.get(`/ai/summary/${interactionId}`, { params: { user_id: userId } })
  return data
}
