<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Foydalanuvchilar</h1>

    <div v-if="loading" class="text-sm text-gray-400">Yuklanmoqda...</div>

    <div v-else class="bg-white border border-gray-100 rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Email</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Username</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Rol</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Holat</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Telegram</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 text-gray-900">{{ u.email }}</td>
            <td class="px-4 py-3 text-gray-500">{{ u.username || '—' }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                :class="roleBadge(u.role)">
                {{ u.role }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                :class="u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ u.is_active ? 'Faol' : 'Faol emas' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ u.telegram_id || '—' }}</td>
            <td class="px-4 py-3">
              <RouterLink :to="`/admin/users/${u.id}`" class="text-blue-600 hover:underline text-xs">
                Ko'rish →
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usersApi } from '@/api/users'

const users = ref([])
const loading = ref(true)

function roleBadge(role) {
  return {
    guest: 'bg-gray-100 text-gray-600',
    user: 'bg-blue-100 text-blue-700',
    admin: 'bg-purple-100 text-purple-700',
    superadmin: 'bg-red-100 text-red-700',
  }[role] || 'bg-gray-100 text-gray-600'
}

onMounted(async () => {
  try {
    const { data } = await usersApi.getAll()
    users.value = data
  } finally {
    loading.value = false
  }
})
</script>
