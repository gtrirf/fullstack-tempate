import api from './index'

export const authApi = {
  sendOtp: (email) =>
    api.post('/auth/register/send-otp/', { email }),

  verifyOtp: (email, code) =>
    api.post('/auth/register/verify/', { email, code }),

  completeProfile: (data) =>
    api.post('/auth/register/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  setPassword: (new_password, new_password_confirm) =>
    api.post('/auth/register/set-password/', { new_password, new_password_confirm }),

  login: (email, password) =>
    api.post('/auth/login/', { email, password }),

  logout: (refresh) =>
    api.post('/auth/logout/', { refresh }),

  refreshToken: (refresh) =>
    api.post('/auth/token/refresh/', { refresh }),

  forgotPassword: (email) =>
    api.post('/auth/forgot-password/', { email }),

  forgotPasswordVerify: (email, code, new_password, confirm_password) =>
    api.post('/auth/forgot-password/verify/', { email, code, new_password, confirm_password }),

  changePassword: (old_password, new_password, new_password_confirm) =>
    api.post('/auth/change-password/', { old_password, new_password, new_password_confirm }),
}
