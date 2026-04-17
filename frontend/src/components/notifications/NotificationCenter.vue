<script setup lang="ts">
import { notificationsApi } from '@/services/api'
import type { Notification } from '@/services/api'

const items = ref<Notification[]>([])
const unreadCount = ref(0)

const load = async () => {
  try {
    const [notifications, unread] = await Promise.all([
      notificationsApi.list(),
      notificationsApi.unreadCount(),
    ])
    items.value = notifications
    unreadCount.value = unread.unread_count
  }
  catch {
    items.value = []
    unreadCount.value = 0
  }
}

const markRead = async (notification: Notification) => {
  if (notification.is_read)
    return
  await notificationsApi.markRead(notification.id)
  notification.is_read = true
  unreadCount.value = Math.max(0, unreadCount.value - 1)
}

onMounted(load)
</script>

<template>
  <VMenu
    location="bottom end"
    width="360"
  >
    <template #activator="{ props }">
      <IconBtn v-bind="props">
        <VBadge
          :content="unreadCount"
          :model-value="unreadCount > 0"
          color="error"
        >
          <VIcon icon="tabler-bell" />
        </VBadge>
      </IconBtn>
    </template>

    <VCard>
      <VCardItem title="Notifications">
        <template #append>
          <VBtn
            size="small"
            variant="text"
            @click="notificationsApi.markAllRead().then(load)"
          >
            Tout lire
          </VBtn>
        </template>
      </VCardItem>
      <VDivider />
      <VList
        lines="two"
        max-height="380"
        class="overflow-y-auto"
      >
        <VListItem
          v-for="item in items"
          :key="item.id"
          :title="item.title"
          :subtitle="item.message"
          @click="markRead(item)"
        >
          <template #append>
            <VChip
              size="x-small"
              :color="item.is_read ? 'default' : 'primary'"
              variant="tonal"
            >
              {{ item.is_read ? 'Lu' : 'Nouveau' }}
            </VChip>
          </template>
        </VListItem>
      </VList>
    </VCard>
  </VMenu>
</template>
