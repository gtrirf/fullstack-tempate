<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">

      <!-- Progress -->
      <div class="flex items-center gap-2 mb-6">
        <div
          v-for="n in 3"
          :key="n"
          class="h-1.5 flex-1 rounded-full transition-colors"
          :class="step >= n ? 'bg-blue-600' : 'bg-gray-200'"
        />
      </div>

      <!-- Step 1: Email + OTP -->
      <div v-if="step === 1">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">Ro'yxatdan o'tish</h1>
        <p class="text-sm text-gray-500 mb-6">Email manzilingizni kiriting</p>

        <form v-if="!otpSent" @submit.prevent="sendOtp" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="email@example.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
          <button type="submit" :disabled="loading" class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ loading ? 'Yuborilmoqda...' : 'Kod yuborish' }}
          </button>
        </form>

        <form v-else @submit.prevent="verifyOtp" class="space-y-4">
          <p class="text-sm text-gray-600">
            <span class="font-medium">{{ email }}</span> manziliga 6 xonali kod yuborildi.
          </p>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tasdiqlash kodi</label>
            <input
              v-model="otp"
              type="text"
              maxlength="6"
              required
              placeholder="123456"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 tracking-widest text-center text-lg"
            />
          </div>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
          <button type="submit" :disabled="loading" class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ loading ? 'Tekshirilmoqda...' : 'Tasdiqlash' }}
          </button>
          <button type="button" @click="otpSent = false" class="w-full text-sm text-gray-500 hover:text-gray-700">
            Emailni o'zgartirish
          </button>
        </form>
      </div>

      <!-- Step 2: Profile -->
      <div v-if="step === 2">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">Profil ma'lumotlari</h1>
        <p class="text-sm text-gray-500 mb-6">Ixtiyoriy — keyin ham to'ldirishingiz mumkin</p>
        <form @submit.prevent="completeProfile" class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ism</label>
              <input v-model="profile.first_name" type="text" placeholder="Ism" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Familiya</label>
              <input v-model="profile.last_name" type="text" placeholder="Familiya" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input v-model="profile.username" type="text" placeholder="username" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
            <input v-model="profile.phone_number" type="tel" placeholder="+998901234567" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
          <div class="flex gap-3">
            <button type="button" @click="step = 3" class="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
              O'tkazib yuborish
            </button>
            <button type="submit" :disabled="loading" class="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
              {{ loading ? 'Saqlanmoqda...' : 'Keyingi' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Step 3: Password -->
      <div v-if="step === 3">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">Parol o'rnatish</h1>
        <p class="text-sm text-gray-500 mb-6">Doimiy parolingizni kiriting</p>
        <form @submit.prevent="setPassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Yangi parol</label>
            <input v-model="passwords.new_password" type="password" required placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Parolni tasdiqlash</label>
            <input v-model="passwords.new_password_confirm" type="password" required placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
          <button type="submit" :disabled="loading" class="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ loading ? 'Saqlanmoqda...' : 'Yakunlash' }}
          </button>
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-gray-500">
        Akkaunt bormi?
        <RouterLink to="/login" class="text-blue-600 hover:underline">Kirish</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const step = ref(1)
const loading = ref(false)
const error = ref('')

const email = ref('')
const otp = ref('')
const otpSent = ref(false)
const profile = ref({ first_name: '', last_name: '', username: '', phone_number: '' })
const passwords = ref({ new_password: '', new_password_confirm: '' })

function extractError(e) {
  const data = e.response?.data
  if (!data) return 'Xatolik yuz berdi.'
  return (
    data.error ||
    data.detail ||
    data.non_field_errors?.[0] ||
    Object.values(data)?.[0]?.[0] ||
    'Xatolik yuz berdi.'
  )
}

async function sendOtp() {
  loading.value = true
  error.value = ''
  try {
    await authApi.sendOtp(email.value)
    otpSent.value = true
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}

async function verifyOtp() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await authApi.verifyOtp(email.value, otp.value)
    auth.setTokensFromRegister(data)
    step.value = 2
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}

async function completeProfile() {
  loading.value = true
  error.value = ''
  try {
    const fd = new FormData()
    Object.entries(profile.value).forEach(([k, v]) => { if (v) fd.append(k, v) })
    await authApi.completeProfile(fd)
    step.value = 3
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}

async function setPassword() {
  loading.value = true
  error.value = ''
  try {
    await authApi.setPassword(passwords.value.new_password, passwords.value.new_password_confirm)
    await auth.fetchMe()
    router.push('/dashboard')
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}
</script>
