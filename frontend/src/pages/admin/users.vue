<script setup lang="ts">
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import DataTable from '@/components/common/DataTable.vue'
import { apiClient } from '@/services/http/axios'

definePage({
  meta: {
    roles: ['admin'],
  },
})

type UserRow = {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'user' | 'organizer' | 'admin'
  is_active: boolean
  is_2fa_enabled?: boolean
}

const users = ref<UserRow[]>([])
const loading = ref(false)
const errorMessage = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

const columns = [
  { key: 'email', title: 'Email', sortable: true },
  { key: 'first_name', title: 'Prénom', sortable: true },
  { key: 'last_name', title: 'Nom', sortable: true },
  { key: 'role', title: 'Rôle', sortable: true },
  { key: 'is_active', title: 'Statut', sortable: true },
]

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await apiClient.get('/admin-panel/users/', {
      params: {
        role: roleFilter.value || undefined,
        is_active: statusFilter.value === '' ? undefined : statusFilter.value === 'active',
      },
    })
    users.value = Array.isArray(data) ? data : data.results || []
  }
  catch (error: any) {
    users.value = []
    errorMessage.value = error?.response?.data?.detail || 'Unable to load users right now.'
  }
  finally {
    loading.value = false
  }
}

const updateUser = async (id: number, payload: Record<string, unknown>) => {
  try {
    await apiClient.patch(`/admin-panel/users/${id}/`, payload)
    await load()
  }
  catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || 'Unable to update this user.'
  }
}

onMounted(load)
</script>

<template>
  <VCard title="Gestion des utilisateurs">
    <VCardText class="d-flex flex-wrap gap-3">
      <AppSelect
        v-model="roleFilter"
        label="Rôle"
        :items="[
          { title: 'Tous', value: '' },
          { title: 'User', value: 'user' },
          { title: 'Organizer', value: 'organizer' },
          { title: 'Admin', value: 'admin' }
        ]"
        style="max-width: 180px;"
      />
      <AppSelect
        v-model="statusFilter"
        label="Statut"
        :items="[
          { title: 'Tous', value: '' },
          { title: 'Actif', value: 'active' },
          { title: 'Banni', value: 'banned' }
        ]"
        style="max-width: 180px;"
      />
      <VBtn
        variant="tonal"
        @click="load"
      >
        Filtrer
      </VBtn>
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

      <DataTable
        :items="users"
        :columns="columns"
        :loading="loading"
      >
        <template #cell-is_active="{ item }">
          <VChip
            :color="item.is_active ? 'success' : 'error'"
            size="small"
          >
            {{ item.is_active ? 'Actif' : 'Banni' }}
          </VChip>
        </template>

        <template #row-actions="{ item }">
          <VMenu>
            <template #activator="{ props }">
              <IconBtn v-bind="props">
                <VIcon icon="tabler-dots-vertical" />
              </IconBtn>
            </template>
            <VList>
              <VListItem @click="updateUser(item.id, { role: 'admin' })">
                <VListItemTitle>Passer Admin</VListItemTitle>
              </VListItem>
              <VListItem @click="updateUser(item.id, { is_active: false })">
                <VListItemTitle>Bannir</VListItemTitle>
              </VListItem>
              <VListItem @click="updateUser(item.id, { is_active: true })">
                <VListItemTitle>Activer</VListItemTitle>
              </VListItem>
            </VList>
          </VMenu>
        </template>
      </DataTable>
    </VCardText>
  </VCard>
</template>
