<script setup lang="ts">
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextarea from '@/@core/components/app-form-elements/AppTextarea.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { apiClient } from '@/services/http/axios'

const loading = ref(true)
const events = ref<any[]>([])
const errorMessage = ref('')
const statusFilter = ref<'pending' | 'approved' | 'rejected'>('pending')
const rejectDialog = ref(false)
const selectedEventId = ref<number | null>(null)
const rejectReason = ref('')

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await apiClient.get('/admin-panel/events/', { params: { status: statusFilter.value } })
    events.value = Array.isArray(data) ? data : data.results || []
  }
  catch (error: any) {
    events.value = []
    errorMessage.value = error?.response?.data?.detail || 'Unable to load admin events right now.'
  }
  finally {
    loading.value = false
  }
}

const verify = async (id: number, action: 'approved' | 'rejected', reason = '') => {
  try {
    await apiClient.post(`/admin-panel/events/${id}/moderate/`, {
      action: action === 'approved' ? 'approve' : 'reject',
      reason,
    })
    await load()
  }
  catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || 'Unable to update this event.'
  }
}

const openReject = (id: number) => {
  selectedEventId.value = id
  rejectReason.value = ''
  rejectDialog.value = true
}

const confirmReject = async () => {
  if (!selectedEventId.value)
    return
  await verify(selectedEventId.value, 'rejected', rejectReason.value)
  rejectDialog.value = false
}

watch(statusFilter, load)
onMounted(load)
</script>

<template>
  <VCard title="Validation des événements">
    <VCardText class="d-flex gap-3 align-center">
      <AppSelect
        v-model="statusFilter"
        label="Statut"
        :items="[
          { title: 'Pending', value: 'pending' },
          { title: 'Approved', value: 'approved' },
          { title: 'Rejected', value: 'rejected' },
        ]"
        style="max-width: 220px;"
      />
    </VCardText>

    <VCardText>
      <VAlert
        v-if="errorMessage"
        type="error"
        variant="tonal"
        class="mb-4"
      >
        {{ errorMessage }}
      </VAlert>

      <VSkeletonLoader
        v-if="loading"
        type="table"
      />

      <VTable v-else>
        <thead>
          <tr>
            <th>Titre</th>
            <th>Organisateur</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="event in events"
            :key="event.id"
          >
            <td>{{ event.title }}</td>
            <td>{{ event.organizer_name }}</td>
            <td>{{ event.status }}</td>
            <td class="d-flex gap-2">
              <VBtn
                size="small"
                color="success"
                @click="verify(event.id, 'approved')"
              >
                Approuver
              </VBtn>
              <VBtn
                size="small"
                color="error"
                variant="tonal"
                @click="openReject(event.id)"
              >
                Rejeter
              </VBtn>
            </td>
          </tr>
        </tbody>
      </VTable>
    </VCardText>
  </VCard>

  <BaseModal
    v-model="rejectDialog"
    title="Motif de rejet"
  >
    <template #body>
      <AppTextarea
        v-model="rejectReason"
        label="Motif"
        rows="4"
      />
    </template>
    <template #footer>
      <VSpacer />
      <VBtn
        variant="text"
        @click="rejectDialog = false"
      >
        Annuler
      </VBtn>
      <VBtn
        color="error"
        @click="confirmReject"
      >
        Confirmer
      </VBtn>
    </template>
  </BaseModal>
</template>
