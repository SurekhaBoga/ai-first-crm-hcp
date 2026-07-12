import apiClient from '@/services/apiClient'

export async function listDoctors({ page = 1, pageSize = 20, specialty, tier, isActive } = {}) {
  const { data } = await apiClient.get('/doctors', {
    params: { page, page_size: pageSize, specialty, tier, is_active: isActive },
  })
  return data
}

export async function searchDoctors({ q, page = 1, pageSize = 20 }) {
  const { data } = await apiClient.get('/doctors/search', { params: { q, page, page_size: pageSize } })
  return data
}

export async function getDoctor(doctorId) {
  const { data } = await apiClient.get(`/doctors/${doctorId}`)
  return data
}

export async function createDoctor(payload) {
  const { data } = await apiClient.post('/doctors', payload)
  return data
}

export async function updateDoctor(doctorId, payload) {
  const { data } = await apiClient.put(`/doctors/${doctorId}`, payload)
  return data
}

export async function deleteDoctor(doctorId) {
  await apiClient.delete(`/doctors/${doctorId}`)
}
