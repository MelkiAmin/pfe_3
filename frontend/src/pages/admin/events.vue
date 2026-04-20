<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import { adminPanelApi } from '@/services/api'
import type { EventListItem, EventStatus } from '@/services/api/types'

definePage({
  meta: {
    roles: ['admin'],
  },
})

const events = ref<EventListItem[]>([])
const loading = ref(false)
const totalItems = ref(0)
const page = ref(1)
const pageSize = ref(10)
const search = ref('')
const statusFilter = ref('')

const snackbar = ref({
  show: false,
  message: '',
  color: 'success',
})

const headers = [
  { title: 'Event', key: 'title', sortable: false },
  { title: 'Organizer', key: 'organizer_name', sortable: false },
  { title: 'Category', key: 'category', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Date', key: 'start_date', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' as const },
]

const statusOptions = [
  { title: 'All', value: '' },
  { title: 'Pending', value: 'pending' },
  { title: 'Approved', value: 'approved' },
  { title: 'Rejected', value: 'rejected' },
  { title: 'Cancelled', value: 'cancelled' },
  { title: 'Completed', value: 'completed' },
]

const statusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'error',
    cancelled: 'error',
    completed: 'info',
  }
  return colors[status] || 'secondary'
}

let debounceId: ReturnType<typeof setTimeout> | null = null

const fetchEvents = async (targetPage = page.value, targetPageSize = pageSize.value) => {
  loading.value = true
  try {
    const response = await adminPanelApi.listEvents({
      page: targetPage,
      page_size: targetPageSize,
      status: statusFilter.value || undefined,
    })
    events.value = response.results || response
    totalItems.value = response.count || response.length
  }
  catch (error: any) {
    snackbar.value = { show: true, message: error?.message || 'Failed to load events', color: 'error' }
  }
  finally {
    loading.value = false
  }
}

const applyFilters = () => {
  page.value = 1
  fetchEvents()
}

const onTableOptionsUpdate = (options: { page: number; itemsPerPage: number }) => {
  if (options.page !== page.value || options.itemsPerPage !== pageSize.value)
    fetchEvents(options.page, options.itemsPerPage)
}

watch(search, value => {
  if (debounceId)
    clearTimeout(debounceId)

  debounceId = setTimeout(() => {
    fetchEvents(1)
  }, 300)
})

watch(statusFilter, () => applyFilters())

onMounted(() => {
  fetchEvents()
})

onUnmounted(() => {
  if (debounceId)
    clearTimeout(debounceId)
})
</script>

<template>
  <div class="d-flex flex-column gap-6">
    <VCard>
      <VCardItem>
        <template #title>
          Gestion des evenements
        </template>
        <template #subtitle>
          Moderez et gerez tous les evenements de la plateforme.
        </template>
      </VCardItem>

      <VCardText>
        <VRow class="align-end">
          <VCol cols="12" md="4">
            <AppTextField
              v-model="search"
              label="Recherche"
              placeholder="Titre ou organisateur..."
              prepend-inner-icon="tabler-search"
            />
          </VCol>
          <VCol cols="12" sm="6" md="3">
            <AppSelect
              v-model="statusFilter"
              label="Statut"
              :items="statusOptions"
            />
          </VCol>
        </VRow>
      </VCardText>

      <VDivider />

      <VDataTableServer
        :headers="headers"
        :items="events"
        :loading="loading"
        :items-length="totalItems"
        :items-per-page="pageSize"
        :page="page"
        class="text-no-wrap"
        @update:options="onTableOptionsUpdate"
      >
        <template #item.title="{ item }">
          <div class="d-flex align-center gap-3 py-2">
            <VAvatar size="40" rounded="lg">
              <VImg v-if="item.cover_image" :src="item.cover_image" />
              <VIcon v-else icon="tabler-ticket" />
            </VAvatar>
            <div>
              <span class="font-weight-medium">{{ item.title }}</span>
              <div class="text-caption text-medium-emphasis">{{ item.city }}</div>
            </div>
          </div>
        </template>

        <template #item.category="{ item }">
          {{ item.category?.name || '-' }}
        </template>

        <template #item.organizer_name="{ item }">
          {{ item.organizer_name }}
        </template>

        <template #item.status="{ item }">
          <VChip :color="statusColor(item.status)" size="small" variant="tonal">
            {{ item.status }}
          </VChip>
        </template>

        <template #item.start_date="{ item }">
          {{ new Date(item.start_date).toLocaleDateString('fr-FR') }}
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex justify-end">
            <VMenu>
              <template #activator="{ props }">
                <IconBtn v-bind="props">
                  <VIcon icon="tabler-dots-vertical" />
                </IconBtn>
              </template>

              <VList>
                <VListItem :to="`/events/${item.slug}`">
                  <VListItemTitle>Voir</VListItemTitle>
                </VListItem>
                <VListItem v-if="item.status === 'pending'" @click="() => {}">
                  <VListItemTitle>Approuver</VListItemTitle>
                </VListItem>
              </VList>
            </VMenu>
          </div>
        </template>
      </VDataTableServer>
    </VCard>

    <VSnackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3500"
    >
      {{ snackbar.message }}
    </VSnackbar>
  </div>
</template>