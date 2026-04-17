<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import avatar1 from '@images/avatars/avatar-1.png'

const userData = useCookie<{
  full_name?: string
  role?: string
} | null>('userData')

const router = useRouter()
const isLoggingOut = ref(false)
const authStore = useAuthStore()

const displayName = computed(() => userData.value?.full_name || 'User')
const displayRole = computed(() => userData.value?.role || 'Member')

const handleLogout = async () => {
  isLoggingOut.value = true
  await authStore.logout()
  await router.replace('/login')
  isLoggingOut.value = false
}
</script>

<template>
  <VBadge
    dot
    location="bottom right"
    offset-x="3"
    offset-y="3"
    bordered
    color="success"
  >
    <VAvatar
      class="cursor-pointer"
      color="primary"
      variant="tonal"
    >
      <VImg :src="avatar1" />

