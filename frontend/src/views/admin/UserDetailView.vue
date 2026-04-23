<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/admin/users" class="text-sm text-gray-500 hover:text-gray-700">← Orqaga</RouterLink>
      <h1 class="text-2xl font-bold text-gray-900">Foydalanuvchi</h1>
    </div>

    <div v-if="loading" class="text-sm text-gray-400">Yuklanmoqda...</div>

    <div v-else class="space-y-5">
      <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
        <div class="flex items-center gap-4 mb-5">
          <img :src="user.avatar" class="w-14 h-14 rounded-full object-cover border border-gray-200" />
          <div>
            <p class="font-medium text-gray-900">{{ user.first_name || user.username }}</p>
            <p class="text-sm text-gray-500">{{ user.email }}</p>
          </div>
        </div>

        <form @submit.prevent="save" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Rol</label>
              <select v-model="form.role" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="guest">Guest</option>
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="superadmin">Superadmin</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Faol</label>
              <select v-model="form.is_active" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option :value="true">Ha</option>
                <option :value="false">Yo'q</option>
              </select>
            </div>
          </div>
          <p v-if="msg" class="text-sm" :class="msg.type === 'ok' ? 'text-green-600' : 'text-red-600'">{{ msg.text }}</p>
          <div class="flex gap-3 pt-2">
            <button type="submit" :disabled="saving" class="py-2 px-4 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
              {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
            </button>
            <button type="button" @click="confirmDelete" class="py-2 px-4 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors">
              O'chirish
            </button>
          </div>
        </form>
      </div>

      <!-- Info -->
      <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm grid grid-cols-2 gap-3 text-sm">
        <div><p class="text-xs text-gray-500">Telegram ID</p><p class="font-medium">{{ user.telegram_id || '—' }}</p></div>
        <div><p class="text-xs text-gray-500">Telefon</p><p class="font-medium">{{ user.phone_number || '—' }}</p></div>
        <div><p class="text-xs text-gray-500">Ro'yxat sanasi</p><p class="font-medium">{{ formatDate(user.date_joined) }}</p></div>
        <div><p class="text-xs text-gray-500">Yangilangan</p><p class="font-medium">{{ formatDate(user.updated_at) }}</p></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usersApi } from '@/api/users'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const user = ref({})
const form = ref({ role: '', is_active: true })
const loading = ref(true)
const saving = ref(false)
const msg = ref(null)

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('uz-UZ')
}

function extractError(e) {
  const d = e.response?.data
  return d?.error || d?.detail || Object.values(d || {})?.[0]?.[0] || 'Xatolik.'
}

onMounted(async () => {
  try {
    const { data } = await usersApi.getById(id)
    user.value = data
    form.value = { role: data.role, is_active: data.is_active }
  } finally {
    loading.value = false
  }
})

async function save() {
  saving.value = true
  msg.value = null
  try {
    const { data } = await usersApi.updateById(id, form.value)
    user.value = data
    msg.value = { type: 'ok', text: 'Saqlandi!' }
  } catch (e) {
    msg.value = { type: 'err', text: extractError(e) }
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  if (!confirm(`${user.value.email} ni o'chirishni tasdiqlaysizmi?`)) return
  try {
    await usersApi.deleteById(id)
    router.push('/admin/users')
  } catch (e) {
    msg.value = { type: 'err', text: extractError(e) }
  }
}
</script>
