import apiClient from '@/services/apiClient'

export async function listUsers({ page = 1, pageSize = 20 } = {}) {
  const { data } = await apiClient.get('/users', { params: { page, page_size: pageSize } })
  return data
}

export async function getUser(userId) {
  const { data } = await apiClient.get(`/users/${userId}`)
  return data
}

export async function createUser(payload) {
  const { data } = await apiClient.post('/users', payload)
  return data
}

export async function updateUser(userId, payload) {
  const { data } = await apiClient.put(`/users/${userId}`, payload)
  return data
}

export async function deleteUser(userId) {
  await apiClient.delete(`/users/${userId}`)
}
