<script setup lang="ts">
import AppTextarea from '@/@core/components/app-form-elements/AppTextarea.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { adminPanelApi } from '@/services/api'
import type { EventListItem } from '@/services/api'

definePage({
  meta: {
    layout: 'default',
    roles: ['admin'],
  },
})

const loading = ref(true)
const items = ref<EventListItem[]>([])
const errorMessage = ref('')
const rejectDialog = ref(false)
const selectedEventId = ref<number | null>(null)
const rejectReason = ref('')

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    items.value = await adminPanelApi.listEvents({ status: 'pending' })
  }
  catch (error: any) {
    items.value = []
    errorMessage.value = error?.data?.detail || 'Unable to load pending events.'
  }
  finally {
    loading.value = false
  }
}

const moderate = async (eventId: number, action: 'approve' | 'reject', reason = '') => {
  try {
    await adminPanelApi.moderateEvent(eventId, { action, reason })
    await load()
  }
  catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Unable to update this event.'
  }
}

const openRejectDialog = (eventId: number) => {
  selectedEventId.value = eventId
  rejectReason.value = ''
  rejectDialog.value = true
}

const confirmReject = async () => {
  if (!selectedEventId.value)
    return
  await moderate(selectedEventId.value, 'reject', rejectReason.value)
  rejectDialog.value = false
}

onMounted(load)
</script>

<template>
  <div class="page-shell">
    <section class="page-hero">
      <div class="d-flex justify-space-between align-center flex-wrap gap-3">
        <div>
          <p class="page-kicker">
            Admin validation
          </p>
          <h1 class="text-h3 mb-2">
            Pending events moderation
          </h1>
          <p class="text-medium-emphasis mb-0">
            Review each pending submission with clearer status badges and fast moderation actions.
          </p>
        </div>

        <VBtn
          color="primary"
          variant="tonal"
          rounded="pill"
          :loading="loading"
          @click="load"
        >
          Refresh
        </VBtn>
      </div>
    </section>

    <VAlert
      v-if="errorMessage"
      type="error"
      variant="tonal"
    >
      {{ errorMessage }}
    </VAlert>

    <VCard class="section-card">
      <VCardText class="pa-6">
        <VSkeletonLoader
          v-if="loading"
          type="article@3"
        />

        <div
          v-else-if="items.length"
          class="soft-grid"
        >
          <VCard
            v-for="event in items"
            :key="event.id"
            class="metric-card"
          >
            <VCardText class="pa-6">
              <div class="d-flex justify-space-between align-start gap-3 mb-4">
                <div>
                  <div class="text-h5 mb-1">
                    {{ event.title }}
                  </div>
                  <div class="text-medium-emphasis">
                    {{ event.organizer_name }} · {{ event.city || 'Online' }}
                  </div>
                </div>

                <VChip
                  size="small"
                  color="warning"
                  variant="tonal"
                >
                  {{ event.status }}
                </VChip>
              </div>

              <div class="text-body-2 text-medium-emphasis mb-4">
                {{ new Date(event.start_date).toLocaleString() }}
              </div>

              <div class="d-flex gap-3">
                <VBtn
                  color="success"
                  rounded="pill"
                  @click="moderate(event.id, 'approve')"
                >
                  Accept
                </VBtn>
                <VBtn
                  color="error"
                  variant="tonal"
                  rounded="pill"
                  @click="openRejectDialog(event.id)"
                >
                  Reject
                </VBtn>
              </div>
            </VCardText>
          </VCard>
        </div>

        <div
          v-else
          class="text-center py-10 text-medium-emphasis"
        >
          No pending events right now.
        </div>
      </VCardText>
    </VCard>

    <BaseModal
      v-model="rejectDialog"
      title="Reject event"
    >
      <template #body>
        <AppTextarea
          v-model="rejectReason"
          label="Reason"
          rows="4"
        />
      </template>
      <template #footer>
        <VSpacer />
        <VBtn variant="text" @click="rejectDialog = false">
          Cancel
        </VBtn>
        <VBtn color="error" @click="confirmReject">
          Confirm rejection
        </VBtn>
      </template>
    </BaseModal>
  </div>
</template>
