import api from './axios'

export interface NotificationItem {
  id: number
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  is_read: boolean
  created_at: string | null
}

export interface NotificationsResponse {
  notifications: NotificationItem[]
  unread_count: number
  pagination: {
    page: number
    per_page: number
    total_pages: number
    total_items: number
  }
}

export async function getNotifications(params?: { page?: number; per_page?: number }): Promise<NotificationsResponse> {
  const { data } = await api.get('/user/notifications', { params })
  return data
}

export async function getUnreadCount(): Promise<{ unread_count: number }> {
  const { data } = await api.get('/user/notifications/unread-count')
  return data
}

export async function markNotificationsRead(ids?: number[]): Promise<{ message: string }> {
  const { data } = await api.post('/user/notifications/mark-read', ids ? { ids } : {})
  return data
}

export async function clearAllNotifications(): Promise<{ message: string }> {
  const { data } = await api.delete('/user/notifications/clear')
  return data
}
