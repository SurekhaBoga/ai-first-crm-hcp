import apiClient from '@/services/apiClient'

export async function listInteractions({ page = 1, pageSize = 20, doctorId, userId } = {}) {
  const { data } = await apiClient.get('/interactions', {
    params: { page, page_size: pageSize, doctor_id: doctorId, user_id: userId },
  })
  return data
}

export async function getDoctorTimeline(doctorId, { page = 1, pageSize = 20 } = {}) {
  const { data } = await apiClient.get(`/interactions/doctor/${doctorId}/timeline`, {
    params: { page, page_size: pageSize },
  })
  return data
}

export async function getInteraction(interactionId) {
  const { data } = await apiClient.get(`/interactions/${interactionId}`)
  return data
}

export async function createInteraction(payload) {
  const { data } = await apiClient.post('/interactions', payload)
  return data
}

export async function updateInteraction(interactionId, payload) {
  const { data } = await apiClient.put(`/interactions/${interactionId}`, payload)
  return data
}

export async function deleteInteraction(interactionId) {
  await apiClient.delete(`/interactions/${interactionId}`)
}
