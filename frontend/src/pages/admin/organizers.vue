<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import { useAdminOrganizersStore } from '@/stores/admin-organizers'
import type { OrganizerProfile } from '@/services/api'

definePage({
  meta: {
    roles: ['admin'],
  },
})

const store = useAdminOrganizersStore()
const { organizers, loading, saving, deleting, totalItems, page, pageSize, filters, snackbar } = storeToRefs(store)

const searchInput = ref(filters.value.search)
const editDialog = ref(false)
const confirmDialog = ref(false)
const viewDialog = ref(false)
const selectedOrganizer = ref<OrganizerProfile | null>(null)

const editForm = reactive({
  organization_name: '',
  bio: '',
  website: '',
  is_verified: false,
})

const headers = [
  { title: 'Organisation', key: 'organization_name', sortable: false },
  { title: 'Responsable', key: 'user_name', sortable: false },
  { title: 'Email', key: 'user_email', sortable: false },
  { title: 'Statut KYC', key: 'is_verified', sortable: false },
  { title: 'Evenements', key: 'total_events', sortable: false },
  { title: 'Inscription', key: 'created_at', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' as const },
]

const verifiedOptions = [
  { title: 'Tous', value: '' },
  { title: 'Verifie', value: true },
  { title: 'Non verifie', value: false },
]

const verifiedColor = (verified: boolean) => verified ? 'success' : 'warning'

let debounceId: ReturnType<typeof setTimeout> | null = null

const fetchOrganizers = (targetPage = page.value, targetPageSize = pageSize.value) => store.fetchOrganizers({
  page: targetPage,
  pageSize: targetPageSize,
})

const applyFilters = () => {
  store.fetchOrganizers({
    page: 1,
    search: searchInput.value,
    is_verified: filters.value.is_verified,
  })
}

const onTableOptionsUpdate = (options: { page: number; itemsPerPage: number }) => {
  if (options.page !== page.value || options.itemsPerPage !== pageSize.value)
    fetchOrganizers(options.page, options.itemsPerPage)
}

const openEditDialog = (organizer: OrganizerProfile) => {
  selectedOrganizer.value = organizer
  editForm.organization_name = organizer.organization_name
  editForm.bio = organizer.bio || ''
  editForm.website = organizer.website || ''
  editForm.is_verified = organizer.is_verified
  editDialog.value = true
}

const openViewDialog = async (organizer: OrganizerProfile) => {
  selectedOrganizer.value = organizer
  await store.fetchOrganizerDetails(organizer.id)
  viewDialog.value = true
}

const openConfirmDialog = (organizer: OrganizerProfile) => {
  selectedOrganizer.value = organizer
  confirmDialog.value = true
}

const submitEdit = async () => {
  if (!selectedOrganizer.value)
    return

  await store.updateOrganizer(selectedOrganizer.value.id, { ...editForm })
  editDialog.value = false
  await fetchOrganizers()
}

const submitDelete = async () => {
  if (!selectedOrganizer.value)
    return

  await store.deleteOrganizer(selectedOrganizer.value.id)
  confirmDialog.value = false
}

const resetFilters = () => {
  searchInput.value = ''
  store.fetchOrganizers({
    page: 1,
    pageSize: pageSize.value,
    search: '',
    is_verified: '',
  })
}

watch(searchInput, value => {
  if (debounceId)
    clearTimeout(debounceId)

  debounceId = setTimeout(() => {
    store.fetchOrganizers({
      page: 1,
      search: value,
      is_verified: filters.value.is_verified,
    })
  }, 300)
})

watch(() => filters.value.is_verified, () => applyFilters())

onMounted(() => {
  fetchOrganizers()
})

onUnmounted(() => {
  if (debounceId)
    clearTimeout(debounceId)
  store.clearSelectedOrganizer()
})
</script>

<template>
  <div class="d-flex flex-column gap-6">
    <VCard>
      <VCardItem>
        <template #title>
          Gestion des organisateurs
        </template>
        <template #subtitle>
          Gerer les comptes organisteurs, verifier leur identite et suivre leurs performances.
        </template>
      </VCardItem>

      <VCardText>
        <VRow class="align-end">
          <VCol cols="12" md="5">
            <AppTextField
              v-model="searchInput"
              label="Recherche"
              placeholder="Nom de l'organisation ou email"
              prepend-inner-icon="tabler-search"
            />
          </VCol>
          <VCol cols="12" sm="6" md="3">
            <AppSelect
              v-model="filters.is_verified"
              label="Statut KYC"
              :items="verifiedOptions"
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
        :items="organizers"
        :loading="loading"
        :items-length="totalItems"
        :items-per-page="pageSize"
        :page="page"
        class="text-no-wrap"
        @update:options="onTableOptionsUpdate"
      >
        <template #item.organization_name="{ item }">
          <div class="d-flex align-center gap-3 py-2">
            <VAvatar size="40" rounded="lg">
              <VImg v-if="item.logo" :src="item.logo" />
              <VIcon v-else icon="tabler-building" />
            </VAvatar>
            <div>
              <span class="font-weight-medium">{{ item.organization_name }}</span>
            </div>
          </div>
        </template>

        <template #item.user_name="{ item }">
          {{ item.user_name }}
        </template>

        <template #item.is_verified="{ item }">
          <VChip :color="verifiedColor(item.is_verified)" size="small" variant="tonal">
            {{ item.is_verified ? 'Verifie' : 'En attente' }}
          </VChip>
        </template>

        <template #item.total_events="{ item }">
          {{ item.total_events || 0 }}
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
                <VListItem @click="openViewDialog(item)">
                  <VListItemTitle>Voir le profil</VListItemTitle>
                </VListItem>
                <VListItem @click="openEditDialog(item)">
                  <VListItemTitle>Modifier</VListItemTitle>
                </VListItem>
                <VListItem @click="openConfirmDialog(item)">
                  <VListItemTitle class="text-error">Desactiver</VListItemTitle>
                </VListItem>
              </VList>
            </VMenu>
          </div>
        </template>
      </VDataTableServer>
    </VCard>

    <VDialog v-model="editDialog" max-width="640">
      <VCard>
        <VCardItem title="Modifier l'organisateur" />
        <VCardText>
          <VRow>
            <VCol cols="12">
              <AppTextField v-model="editForm.organization_name" label="Nom de l'organisation" />
            </VCol>
            <VCol cols="12">
              <AppTextField v-model="editForm.website" label="Site web" type="url" />
            </VCol>
            <VCol cols="12">
              <AppTextField v-model="editForm.bio" label="Bio" rows="3" multiline />
            </VCol>
            <VCol cols="12">
              <VSwitch
                v-model="editForm.is_verified"
                label="Compte verifie KYC"
                color="success"
                hide-details
              />
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

    <VDialog v-model="viewDialog" max-width="800">
      <VCard v-if="selectedOrganizer">
        <VCardItem title="Profil de l'organisateur" />
        <VCardText>
          <VRow>
            <VCol cols="12" md="4">
              <VAvatar size="100" rounded="lg" class="mb-3">
                <VImg v-if="selectedOrganizer.logo" :src="selectedOrganizer.logo" />
                <VIcon v-else icon="tabler-building" size="48" />
              </VAvatar>
            </VCol>
            <VCol cols="12" md="8">
              <h3 class="text-h5 mb-2">{{ selectedOrganizer.organization_name }}</h3>
              <p class="text-medium-emphasis mb-4">{{ selectedOrganizer.user_name }} &lt;{{ selectedOrganizer.user_email }}&gt;</p>
              <VChip :color="verifiedColor(selectedOrganizer.is_verified)" class="mb-4">
                {{ selectedOrganizer.is_verified ? 'Verifie' : 'En attente de verification' }}
              </VChip>
              <p v-if="selectedOrganizer.bio" class="text-body-1">{{ selectedOrganizer.bio }}</p>
            </VCol>
          </VRow>

          <VDivider class="my-4" />

          <VRow v-if="store.selectedOrganizerStats">
            <VCol cols="6" md="3">
              <VCard variant="tonal" color="primary" class="pa-4 text-center">
                <div class="text-h4">{{ store.selectedOrganizerStats.total_events }}</div>
                <div class="text-body-2">Total evenements</div>
              </VCard>
            </VCol>
            <VCol cols="6" md="3">
              <VCard variant="tonal" color="success" class="pa-4 text-center">
                <div class="text-h4">{{ store.selectedOrganizerStats.published_events }}</div>
                <div class="text-body-2">Publications</div>
              </VCard>
            </VCol>
            <VCol cols="6" md="3">
              <VCard variant="tonal" color="info" class="pa-4 text-center">
                <div class="text-h4">{{ store.selectedOrganizerStats.total_tickets_sold }}</div>
                <div class="text-body-2">Billets vendus</div>
              </VCard>
            </VCol>
            <VCol cols="6" md="3">
              <VCard variant="tonal" color="warning" class="pa-4 text-center">
                <div class="text-h4">{{ store.selectedOrganizerStats.total_revenue }} &euro;</div>
                <div class="text-body-2">Revenus totaux</div>
              </VCard>
            </VCol>
          </VRow>

          <VDivider v-if="store.selectedOrganizerEvents.length > 0" class="my-4" />

          <div v-if="store.selectedOrganizerEvents.length > 0">
            <h4 class="text-h6 mb-3">Evenements recents</h4>
            <VList>
              <VListItem v-for="event in store.selectedOrganizerEvents" :key="event.id" :to="`/events/${event.slug}`">
                <VListItemTitle>{{ event.title }}</VListItemTitle>
                <VListItemSubtitle>{{ event.city }} - {{ new Date(event.start_date).toLocaleDateString() }}</VListItemSubtitle>
                <template #append>
                  <VChip size="small" :color="event.status === 'approved' ? 'success' : 'warning'">
                    {{ event.status }}
                  </VChip>
                </template>
              </VListItem>
            </VList>
          </div>
        </VCardText>
        <VCardActions class="justify-end">
          <VBtn variant="text" color="secondary" @click="viewDialog = false">
            Fermer
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="confirmDialog" max-width="520">
      <VCard>
        <VCardItem title="Confirmer la desactivation" />
        <VCardText class="d-flex flex-column gap-4">
          <p v-if="selectedOrganizer" class="mb-0">
            Voulez-vous vraiment desactiver le compte de <strong>{{ selectedOrganizer.organization_name }}</strong> ?
            Cette action ne peut pas etre annulee.
          </p>
        </VCardText>
        <VCardActions class="justify-end">
          <VBtn variant="text" color="secondary" @click="confirmDialog = false">
            Annuler
          </VBtn>
          <VBtn color="error" :loading="deleting" @click="submitDelete">
            Desactiver
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