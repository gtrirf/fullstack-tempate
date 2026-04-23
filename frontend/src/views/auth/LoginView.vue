<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-1">Kirish</h1>
      <p class="text-sm text-gray-500 mb-6">Akkauntingizga kiring</p>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="email@example.com"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Parol</label>
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {{ loading ? 'Kirilmoqda...' : 'Kirish' }}
        </button>
      </form>

      <div class="mt-6 flex flex-col gap-2 text-sm text-center text-gray-500">
        <RouterLink to="/forgot-password" class="text-blue-600 hover:underline">
          Parolni unutdingizmi?
        </RouterLink>
        <span>
          Akkaunt yo'qmi?
          <RouterLink to="/register" class="text-blue-600 hover:underline">
            Ro'yxatdan o'ting
          </RouterLink>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    const data = e.response?.data
    error.value =
      data?.non_field_errors?.[0] ||
      data?.detail ||
      Object.values(data || {})?.[0]?.[0] ||
      'Kirish xatoligi. Qayta urinib ko\'ring.'
  } finally {
    loading.value = false
  }
}
</script>
