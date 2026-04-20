<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import { useAdminUsersStore } from '@/stores/admin-users'
import type { AdminUser, AdminUserStatus, UserRole } from '@/services/api'

definePage({
  meta: {
    roles: ['admin'],
  },
})

const store = useAdminUsersStore()
const { users, loading, saving, deleting, totalItems, page, pageSize, filters, snackbar } = storeToRefs(store)

const searchInput = ref(filters.value.search)
const editDialog = ref(false)
const confirmDialog = ref(false)
const currentAction = ref<'ban' | 'delete' | 'unban'>('ban')
const selectedUser = ref<AdminUser | null>(null)
const banReason = ref('')

const editForm = reactive({
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  role: 'attendee' as UserRole,
  status: 'active' as AdminUserStatus,
})

const headers = [
  { title: 'Utilisateur', key: 'full_name', sortable: false },
  { title: 'Email', key: 'email', sortable: false },
  { title: 'Role', key: 'role', sortable: false },
  { title: 'Statut', key: 'status', sortable: false },
  { title: 'Telephone', key: 'phone', sortable: false },
  { title: 'Inscription', key: 'created_at', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' as const },
]

const roleOptions = [
  { title: 'Tous les roles', value: '' },
  { title: 'Participant', value: 'attendee' },
  { title: 'Organisateur', value: 'organizer' },
  { title: 'Admin', value: 'admin' },
]

const statusOptions = [
  { title: 'Tous les statuts', value: '' },
  { title: 'Actif', value: 'active' },
  { title: 'Banni', value: 'banned' },
]

const selectedActionLabel = computed(() => {
  if (currentAction.value === 'delete')
    return 'desactiver'
  if (currentAction.value === 'unban')
    return 'reactiver'
  return 'bannir'
})

const statusColor = (status: AdminUserStatus) => status === 'active' ? 'success' : 'error'
const roleColor = (role: UserRole) => {
  if (role === 'admin')
    return 'error'
  if (role === 'organizer')
    return 'info'
  return 'secondary'
}
const roleLabel = (role: UserRole) => {
  if (role === 'admin')
    return 'Admin'
  if (role === 'organizer')
    return 'Organisateur'
  return 'Participant'
}

let debounceId: ReturnType<typeof setTimeout> | null = null

const fetchUsers = (targetPage = page.value, targetPageSize = pageSize.value) => store.fetchUsers({
  page: targetPage,
  pageSize: targetPageSize,
})

const applyFilters = () => {
  store.fetchUsers({
    page: 1,
    search: searchInput.value,
    role: filters.value.role,
    status: filters.value.status,
  })
}

const onTableOptionsUpdate = (options: { page: number; itemsPerPage: number }) => {
  if (options.page !== page.value || options.itemsPerPage !== pageSize.value)
    fetchUsers(options.page, options.itemsPerPage)
}

const openEditDialog = (user: AdminUser) => {
  selectedUser.value = user
  editForm.email = user.email
  editForm.first_name = user.first_name
  editForm.last_name = user.last_name
  editForm.phone = user.phone || ''
  editForm.role = user.role
  editForm.status = user.status
  editDialog.value = true
}

const openConfirmDialog = (action: 'ban' | 'delete' | 'unban', user: AdminUser) => {
  currentAction.value = action
  selectedUser.value = user
  banReason.value = action === 'ban' ? '' : user.ban_reason || ''
  confirmDialog.value = true
}

const closeConfirmDialog = () => {
  confirmDialog.value = false
  banReason.value = ''
}

const submitEdit = async () => {
  if (!selectedUser.value)
    return

  await store.updateUser(selectedUser.value.id, { ...editForm })
  editDialog.value = false
  await fetchUsers()
}

const submitConfirm = async () => {
  if (!selectedUser.value)
    return

  if (currentAction.value === 'ban')
    await store.banUser(selectedUser.value.id, banReason.value)
  else if (currentAction.value === 'unban')
    await store.unbanUser(selectedUser.value.id)
  else
    await store.deleteUser(selectedUser.value.id)

  closeConfirmDialog()
}

const resetFilters = () => {
  searchInput.value = ''
  store.fetchUsers({
    page: 1,
    pageSize: pageSize.value,
    search: '',
    role: '',
    status: '',
  })
}

watch(searchInput, value => {
  if (debounceId)
    clearTimeout(debounceId)

  debounceId = setTimeout(() => {
    store.fetchUsers({
      page: 1,
      search: value,
      role: filters.value.role,
      status: filters.value.status,
    })
  }, 300)
})

watch(() => filters.value.role, () => applyFilters())
watch(() => filters.value.status, () => applyFilters())

onMounted(() => {
  fetchUsers()
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
          Gestion des utilisateurs
        </template>
        <template #subtitle>
          Rechercher, modifier, bannir ou desactiver les comptes depuis l'admin panel.
        </template>
      </VCardItem>

      <VCardText>
        <VRow class="align-end">
          <VCol cols="12" md="5">
            <AppTextField
              v-model="searchInput"
              label="Recherche"
              placeholder="Email, prenom ou nom"
              prepend-inner-icon="tabler-search"
            />
          </VCol>
          <VCol cols="12" sm="6" md="3">
            <AppSelect
              v-model="filters.role"
              label="Role"
              :items="roleOptions"
            />
          </VCol>
          <VCol cols="12" sm="6" md="3">
            <AppSelect
              v-model="filters.status"
              label="Statut"
              :items="statusOptions"
            />
          </VCol>
          <VCol cols="12" md="1" class="d-flex justify-end">
            <VBtn
              variant="tonal"
              color="secondary"
              @click="resetFilters"
            >
              Reset
            </VBtn>
          </VCol>
        </VRow>
      </VCardText>

      <VDivider />

      <VDataTableServer
        :headers="headers"
        :items="users"
        :loading="loading"
        :items-length="totalItems"
        :items-per-page="pageSize"
        :page="page"
        class="text-no-wrap"
        @update:options="onTableOptionsUpdate"
      >
        <template #item.full_name="{ item }">
          <div class="d-flex flex-column py-3">
            <span class="font-weight-medium">{{ item.full_name }}</span>
            <span class="text-sm text-medium-emphasis">
              #{{ item.id }}
            </span>
          </div>
        </template>

        <template #item.role="{ item }">
          <VChip :color="roleColor(item.role)" size="small" variant="tonal">
            {{ roleLabel(item.role) }}
          </VChip>
        </template>

        <template #item.status="{ item }">
          <div class="d-flex flex-column gap-1">
            <VChip :color="statusColor(item.status)" size="small" variant="tonal">
              {{ item.status === 'active' ? 'Actif' : 'Banni' }}
            </VChip>
            <span v-if="item.ban_reason" class="text-xs text-medium-emphasis">
              {{ item.ban_reason }}
            </span>
          </div>
        </template>

        <template #item.created_at="{ item }">
          {{ new Date(item.created_at).toLocaleDateString('fr-FR') }}
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
                <VListItem @click="openEditDialog(item)">
                  <VListItemTitle>Modifier</VListItemTitle>
                </VListItem>
                <VListItem v-if="item.status === 'active'" @click="openConfirmDialog('ban', item)">
                  <VListItemTitle>Bannir</VListItemTitle>
                </VListItem>
                <VListItem v-else @click="openConfirmDialog('unban', item)">
                  <VListItemTitle>Debannir</VListItemTitle>
                </VListItem>
                <VListItem @click="openConfirmDialog('delete', item)">
                  <VListItemTitle>Desactiver</VListItemTitle>
                </VListItem>
              </VList>
            </VMenu>
          </div>
        </template>
      </VDataTableServer>
    </VCard>

    <VDialog v-model="editDialog" max-width="640">
      <VCard>
        <VCardItem title="Modifier l'utilisateur" />
        <VCardText>
          <VRow>
            <VCol cols="12" md="6">
              <AppTextField v-model="editForm.first_name" label="Prenom" />
            </VCol>
            <VCol cols="12" md="6">
              <AppTextField v-model="editForm.last_name" label="Nom" />
            </VCol>
            <VCol cols="12">
              <AppTextField v-model="editForm.email" label="Email" type="email" />
            </VCol>
            <VCol cols="12" md="6">
              <AppTextField v-model="editForm.phone" label="Telephone" />
            </VCol>
            <VCol cols="12" md="3">
              <AppSelect v-model="editForm.role" label="Role" :items="roleOptions.slice(1)" />
            </VCol>
            <VCol cols="12" md="3">
              <AppSelect v-model="editForm.status" label="Statut" :items="statusOptions.slice(1)" />
            </VCol>
          </VRow>
        </VCardText>
        <VCardActions class="justify-end">
          <VBtn variant="text" color="secondary" @click="editDialog = false">
            Annuler
          </VBtn>
          <VBtn :loading="saving" @click="submitEdit">
            Enregistrer
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="confirmDialog" max-width="520">
      <VCard>
        <VCardItem :title="`Confirmer: ${selectedActionLabel}`" />
        <VCardText class="d-flex flex-column gap-4">
          <p v-if="selectedUser" class="mb-0">
            Voulez-vous vraiment {{ selectedActionLabel }} le compte de <strong>{{ selectedUser.full_name }}</strong> ?
          </p>

          <AppTextField
            v-if="currentAction === 'ban'"
            v-model="banReason"
            label="Raison du bannissement"
            placeholder="Expliquez la raison"
          />
        </VCardText>
        <VCardActions class="justify-end">
          <VBtn variant="text" color="secondary" @click="closeConfirmDialog">
            Annuler
          </VBtn>
          <VBtn
            :color="currentAction === 'delete' ? 'error' : currentAction === 'ban' ? 'warning' : 'success'"
            :loading="saving || deleting"
            @click="submitConfirm"
          >
            Confirmer
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VSnackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3500"
    >
      {{ snackbar.message }}
    </VSnackbar>
  </div>
</template>
