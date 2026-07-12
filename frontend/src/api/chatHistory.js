import apiClient from '@/services/apiClient'

export async function saveChatMessage(payload) {
  const { data } = await apiClient.post('/chat-history', payload)
  return data
}

export async function getSessionHistory(sessionId) {
  const { data } = await apiClient.get(`/chat-history/session/${sessionId}`)
  return data
}

export async function deleteSessionHistory(sessionId) {
  await apiClient.delete(`/chat-history/session/${sessionId}`)
}

export async function deleteChatMessage(chatHistoryId) {
  await apiClient.delete(`/chat-history/${chatHistoryId}`)
}
