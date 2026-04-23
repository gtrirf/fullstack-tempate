<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        Xush kelibsiz, {{ auth.user?.first_name || auth.user?.username || 'Foydalanuvchi' }}!
      </h1>
      <p class="text-sm text-gray-500 mt-1">Bosh sahifa</p>
    </div>

    <!-- Role badge -->
    <div class="flex items-center gap-2 mb-6">
      <span class="px-2.5 py-0.5 rounded-full text-xs font-medium"
        :class="{
          'bg-gray-100 text-gray-700': auth.isGuest,
          'bg-blue-100 text-blue-700': auth.isUser,
          'bg-purple-100 text-purple-700': auth.isAdmin,
        }">
        {{ roleLabel }}
      </span>
      <span v-if="auth.isGuest" class="text-xs text-amber-600">
        Ro'yxatdan o'tishni yakunlang (parol o'rnatilmagan)
      </span>
    </div>

    <!-- Info cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
      <div class="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
        <p class="text-xs text-gray-500 mb-1">Email</p>
        <p class="font-medium text-gray-900 text-sm">{{ auth.user?.email }}</p>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
        <p class="text-xs text-gray-500 mb-1">Telegram</p>
        <p class="font-medium text-gray-900 text-sm">
          {{ auth.user?.telegram_id ? '✅ Ulangan' : '—' }}
        </p>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
        <p class="text-xs text-gray-500 mb-1">Backend holati</p>
        <p class="font-medium text-sm" :class="health === true ? 'text-green-600' : health === false ? 'text-red-600' : 'text-gray-400'">
          {{ health === true ? '✅ Ishlayapti' : health === false ? '❌ Javob bermayapti' : 'Tekshirilmoqda...' }}
        </p>
      </div>
      <div v-if="auth.isAdmin" class="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
        <p class="text-xs text-gray-500 mb-1">Admin panel</p>
        <RouterLink to="/admin/users" class="text-sm text-blue-600 hover:underline font-medium">
          Foydalanuvchilar →
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const health = ref(null)

const roleLabel = computed(() => {
  const map = { guest: 'Mehmon', user: 'Foydalanuvchi', admin: 'Admin', superadmin: 'Super Admin' }
  return map[auth.user?.role] || auth.user?.role
})

onMounted(async () => {
  try {
    const base = import.meta.env.VITE_API_URL.replace('/api', '')
    const { data } = await api.get('/health/')
    health.value = data.backend_status === 'ok'
  } catch {
    health.value = false
  }
})
</script>
