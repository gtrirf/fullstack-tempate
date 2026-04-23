<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Profil</h1>

    <div v-if="loading" class="text-sm text-gray-400">Yuklanmoqda...</div>

    <div v-else class="space-y-6">
      <!-- Avatar -->
      <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm flex items-center gap-4">
        <img
          :src="user.avatar || '/default.png'"
          class="w-16 h-16 rounded-full object-cover border border-gray-200"
        />
        <div>
          <p class="font-medium text-gray-900">{{ user.first_name || user.username }}</p>
          <p class="text-sm text-gray-500">{{ user.email }}</p>
        </div>
      </div>

      <!-- Edit form -->
      <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
        <h2 class="text-sm font-semibold text-gray-700 mb-4">Ma'lumotlarni tahrirlash</h2>
        <form @submit.prevent="saveProfile" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Ism</label>
              <input v-model="form.first_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Familiya</label>
              <input v-model="form.last_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Username</label>
            <input v-model="form.username" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Telefon</label>
            <input v-model="form.phone_number" type="tel" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Avatar</label>
            <input type="file" accept="image/*" @change="onAvatarChange" class="text-sm text-gray-600" />
          </div>
          <p v-if="profileMsg" class="text-sm" :class="profileMsg.type === 'ok' ? 'text-green-600' : 'text-red-600'">
            {{ profileMsg.text }}
          </p>
          <button type="submit" :disabled="saving" class="py-2 px-4 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </form>
      </div>

      <!-- Telegram -->
      <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">Telegram</h2>
        <div v-if="user.telegram_id" class="flex items-center justify-between">
          <p class="text-sm text-gray-600">ID: <span class="font-medium">{{ user.telegram_id }}</span></p>
          <button @click="unlinkTelegram" class="text-sm text-red-500 hover:text-red-700">Uzish</button>
        </div>
        <div v-else class="space-y-2">
          <p class="text-sm text-gray-500">Telegram akkauntingizni ulang</p>
          <div class="flex gap-2">
            <input v-model="telegramId" type="text" placeholder="Telegram ID" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <button @click="linkTelegram" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
              Ulash
            </button>
          </div>
        </div>
        <p v-if="telegramMsg" class="mt-2 text-sm" :class="telegramMsg.type === 'ok' ? 'text-green-600' : 'text-red-600'">
          {{ telegramMsg.text }}
        </p>
      </div>

      <!-- Change password -->
      <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
        <h2 class="text-sm font-semibold text-gray-700 mb-4">Parol o'zgartirish</h2>
        <form @submit.prevent="changePassword" class="space-y-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1">Joriy parol</label>
            <input v-model="pwForm.old_password" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Yangi parol</label>
            <input v-model="pwForm.new_password" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Parolni tasdiqlash</label>
            <input v-model="pwForm.new_password_confirm" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <p v-if="pwMsg" class="text-sm" :class="pwMsg.type === 'ok' ? 'text-green-600' : 'text-red-600'">{{ pwMsg.text }}</p>
          <button type="submit" :disabled="changingPw" class="py-2 px-4 bg-gray-800 text-white rounded-lg text-sm font-medium hover:bg-gray-900 disabled:opacity-50 transition-colors">
            {{ changingPw ? 'Saqlanmoqda...' : 'Parolni o\'zgartirish' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usersApi } from '@/api/users'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const saving = ref(false)
const changingPw = ref(false)

const user = ref({})
const form = ref({})
const avatarFile = ref(null)
const profileMsg = ref(null)

const telegramId = ref('')
const telegramMsg = ref(null)

const pwForm = ref({ old_password: '', new_password: '', new_password_confirm: '' })
const pwMsg = ref(null)

function extractError(e) {
  const d = e.response?.data
  return d?.error || d?.detail || d?.non_field_errors?.[0] || Object.values(d || {})?.[0]?.[0] || 'Xatolik.'
}

onMounted(async () => {
  try {
    const { data } = await usersApi.getMe()
    user.value = data
    form.value = {
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      username: data.username || '',
      phone_number: data.phone_number || '',
    }
  } finally {
    loading.value = false
  }
})

function onAvatarChange(e) {
  avatarFile.value = e.target.files[0] || null
}

async function saveProfile() {
  saving.value = true
  profileMsg.value = null
  try {
    const fd = new FormData()
    Object.entries(form.value).forEach(([k, v]) => { if (v) fd.append(k, v) })
    if (avatarFile.value) fd.append('avatar', avatarFile.value)
    const { data } = await usersApi.updateMe(fd)
    user.value = data
    await auth.fetchMe()
    profileMsg.value = { type: 'ok', text: 'Saqlandi!' }
  } catch (e) {
    profileMsg.value = { type: 'err', text: extractError(e) }
  } finally {
    saving.value = false
  }
}

async function linkTelegram() {
  telegramMsg.value = null
  try {
    await usersApi.linkTelegram(telegramId.value)
    await auth.fetchMe()
    const { data } = await usersApi.getMe()
    user.value = data
    telegramMsg.value = { type: 'ok', text: 'Ulandi!' }
    telegramId.value = ''
  } catch (e) {
    telegramMsg.value = { type: 'err', text: extractError(e) }
  }
}

async function unlinkTelegram() {
  telegramMsg.value = null
  try {
    await usersApi.unlinkTelegram()
    user.value.telegram_id = null
    await auth.fetchMe()
    telegramMsg.value = { type: 'ok', text: 'Uzildi.' }
  } catch (e) {
    telegramMsg.value = { type: 'err', text: extractError(e) }
  }
}

async function changePassword() {
  changingPw.value = true
  pwMsg.value = null
  try {
    await authApi.changePassword(pwForm.value.old_password, pwForm.value.new_password, pwForm.value.new_password_confirm)
    pwMsg.value = { type: 'ok', text: 'Parol o\'zgartirildi!' }
    pwForm.value = { old_password: '', new_password: '', new_password_confirm: '' }
  } catch (e) {
    pwMsg.value = { type: 'err', text: extractError(e) }
  } finally {
    changingPw.value = false
  }
}
</script>
