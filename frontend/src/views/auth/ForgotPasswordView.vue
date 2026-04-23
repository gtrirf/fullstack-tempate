<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">

      <div v-if="!codeSent">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">Parolni tiklash</h1>
        <p class="text-sm text-gray-500 mb-6">Emailingizga tasdiqlash kodi yuboramiz</p>
        <form @submit.prevent="sendCode" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="email" type="email" required placeholder="email@example.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
          <button type="submit" :disabled="loading"
            class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ loading ? 'Yuborilmoqda...' : 'Kod yuborish' }}
          </button>
        </form>
      </div>

      <div v-else>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">Yangi parol</h1>
        <p class="text-sm text-gray-500 mb-6">
          <span class="font-medium">{{ email }}</span> ga kod yuborildi
        </p>
        <form @submit.prevent="resetPassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tasdiqlash kodi</label>
            <input v-model="code" type="text" maxlength="6" required placeholder="123456"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 tracking-widest text-center text-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Yangi parol</label>
            <input v-model="newPassword" type="password" required placeholder="••••••••"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Parolni tasdiqlash</label>
            <input v-model="confirmPassword" type="password" required placeholder="••••••••"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
          <p v-if="success" class="text-sm text-green-600">{{ success }}</p>
          <button type="submit" :disabled="loading"
            class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ loading ? 'Saqlanmoqda...' : 'Parolni tiklash' }}
          </button>
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-gray-500">
        <RouterLink to="/login" class="text-blue-600 hover:underline">Kirishga qaytish</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()
const email = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const codeSent = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref('')

function extractError(e) {
  const data = e.response?.data
  return data?.error || data?.detail || data?.non_field_errors?.[0] || Object.values(data || {})?.[0]?.[0] || 'Xatolik.'
}

async function sendCode() {
  loading.value = true
  error.value = ''
  try {
    await authApi.forgotPassword(email.value)
    codeSent.value = true
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}

async function resetPassword() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await authApi.forgotPasswordVerify(email.value, code.value, newPassword.value, confirmPassword.value)
    success.value = 'Parol muvaffaqiyatli tiklandi!'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}
</script>
