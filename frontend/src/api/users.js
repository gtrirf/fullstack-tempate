import api from './index'

export const usersApi = {
  getMe: () =>
    api.get('/users/me/'),

  updateMe: (data) =>
    api.patch('/users/me/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getAll: () =>
    api.get('/users/'),

  getById: (id) =>
    api.get(`/users/${id}/`),

  updateById: (id, data) =>
    api.patch(`/users/${id}/`, data),

  deleteById: (id) =>
    api.delete(`/users/${id}/`),

  linkTelegram: (telegram_id) =>
    api.post('/users/link-telegram/', { telegram_id }),

  unlinkTelegram: () =>
    api.delete('/users/unlink-telegram/'),
}
