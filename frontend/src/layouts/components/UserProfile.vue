<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isLoggingOut = ref(false)

const userData = useCookie<{
  full_name?: string
  role?: string
} | null>('userData')

const initials = computed(() => {
  const name = userData.value?.full_name || 'User'
  return name.split(' ').map(part => part[0]).join('').slice(0, 2).toUpperCase()
})

const displayName = computed(() => userData.value?.full_name || 'User')
const displayRole = computed(() => authStore.roleLabel(userData.value?.role as any))

const handleLogout = async () => {
  isLoggingOut.value = true
  await authStore.logout()
  await router.replace('/login')
  isLoggingOut.value = false
}
</script>

<template>
  <div class="user-profile-shell">
    <VAvatar
      rounded="xl"
      color="primary"
      variant="flat"
      size="40"
    >
      {{ initials }}
    </VAvatar>

    <div class="user-copy">
      <div class="user-name">
        {{ displayName }}
      </div>
      <div class="user-role">
        {{ displayRole }}
      </div>
    </div>

    <VBtn
      size="small"
      variant="tonal"
      :loading="isLoggingOut"
      @click="handleLogout"
    >
      Logout
    </VBtn>
  </div>
</template>

<style scoped>
.user-profile-shell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.35rem 0.4rem 0.35rem 0.35rem;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 18px;
  background: rgba(var(--v-theme-surface), 0.86);
}

.user-copy {
  min-width: 0;
}

.user-name {
  font-weight: 700;
  line-height: 1.1;
}

.user-role {
  font-size: 0.84rem;
  color: rgba(var(--v-theme-on-surface), 0.62);
}
</style>
