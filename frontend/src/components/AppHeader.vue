<template>
  <header class="bg-white border-b border-gray-100 sticky top-0 z-10">
    <div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
      <!-- Logo -->
      <RouterLink to="/dashboard" class="font-bold text-gray-900 text-sm tracking-tight">
        Template
      </RouterLink>

      <!-- Nav -->
      <nav class="flex items-center gap-4 text-sm">
        <RouterLink
          to="/dashboard"
          class="text-gray-500 hover:text-gray-900 transition-colors"
          active-class="text-gray-900 font-medium"
        >
          Dashboard
        </RouterLink>
        <RouterLink
          to="/profile"
          class="text-gray-500 hover:text-gray-900 transition-colors"
          active-class="text-gray-900 font-medium"
        >
          Profil
        </RouterLink>
        <RouterLink
          v-if="auth.isAdmin"
          to="/admin/users"
          class="text-gray-500 hover:text-gray-900 transition-colors"
          active-class="text-gray-900 font-medium"
        >
          Admin
        </RouterLink>

        <!-- User + Logout -->
        <div class="flex items-center gap-3 ml-4 pl-4 border-l border-gray-100">
          <span class="text-xs text-gray-400">{{ auth.user?.email }}</span>
          <button
            @click="logout"
            class="text-xs text-gray-500 hover:text-red-600 transition-colors"
          >
            Chiqish
          </button>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>
