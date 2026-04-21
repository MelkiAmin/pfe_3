<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { authApi } from '@/services/api'

definePage({
  meta: {
    roles: ['admin'],
  },
})

interface PendingUser {
  id: number
  email: string
  first_name: string
  last_name: string
  phone: string
  role: string
  created_at: string
}

const pendingUsers = ref<PendingUser[]>([])
const loading = ref(false)
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')
const approveDialog = ref(false)
const rejectDialog = ref(false)
const selectedId = ref<number | null>(null)
const rejectNote = ref('')

const roleLabels: Record<string, string> = {
  attendee: 'Participant',
  organizer: 'Organisateur',
  admin: 'Administrateur',
}

const headers = [
  { title: 'Nom', key: 'name', sortable: false },
  { title: 'Email', key: 'email', sortable: false },
  { title: 'Telephone', key: 'phone', sortable: false },
  { title: 'Role', key: 'role', sortable: false },
  { title: 'Date inscription', key: 'created_at', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' as const },
]

const fetchPending = async () => {
  loading.value = true
  try {
    pendingUsers.value = await authApi.listPendingUsers()
  }
  catch (error: any) {
    snackbarText.value = error?.message || 'Erreur lors du chargement'
    snackbarColor.value = 'error'
    snackbar.value = true
  }
  finally {
    loading.value = false
  }
}

const openApprove = (id: number) => {
  selectedId.value = id
  approveDialog.value = true
}

const openReject = (id: number) => {
  selectedId.value = id
  rejectNote.value = ''
  rejectDialog.value = true
}

const handleApprove = async () => {
  if (!selectedId.value) return
  try {
    const response = await authApi.approveUser(selectedId.value)
    console.log('Approve response:', response)
    snackbarText.value = response.detail || 'Utilisateur approuve'
    snackbarColor.value = 'success'
    snackbar.value = true
    approveDialog.value = false
    selectedId.value = null
    fetchPending()
  }
  catch (error: any) {
    console.error('Approve error:', error)
    snackbarText.value = error?.message || 'Erreur'
    snackbarColor.value = 'error'
    snackbar.value = true
  }
}

const handleReject = async () => {
  if (!selectedId.value) return
  try {
    const response = await authApi.rejectUser(selectedId.value, rejectNote.value)
    console.log('Reject response:', response)
    snackbarText.value = response.detail || 'Utilisateur rejete'
    snackbarColor.value = 'success'
    snackbar.value = true
    rejectDialog.value = false
    selectedId.value = null
    fetchPending()
  }
  catch (error: any) {
    console.error('Reject error:', error)
    snackbarText.value = error?.message || 'Erreur'
    snackbarColor.value = 'error'
    snackbar.value = true
  }
}

onMounted(fetchPending)
</script>

<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Approbations</h1>
      </v-col>
    </v-row>

    <v-card class="section-card">
      <v-data-table
        :headers="headers"
        :items="pendingUsers"
        :loading="loading"
        :no-data-text="pendingUsers.length === 0 ? 'Aucun utilisateur en attente' : undefined"
        class="elevation-0"
      >
        <template #item.name="{ item }">
          {{ item.first_name }} {{ item.last_name }}
        </template>
        <template #item.role="{ item }">
          {{ roleLabels[item.role] || item.role }}
        </template>
        <template #item.created_at="{ item }">
          {{ new Date(item.created_at).toLocaleDateString('fr-FR') }}
        </template>
        <template #item.actions="{ item }">
          <v-btn
            color="success"
            size="small"
            variant="tonal"
            class="mr-2"
            @click="openApprove(item.id)"
          >
            <v-icon start>tabler-check</v-icon>
            Approuver
          </v-btn>
          <v-btn
            color="error"
            size="small"
            variant="tonal"
            @click="openReject(item.id)"
          >
            <v-icon start>tabler-x</v-icon>
            Rejeter
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="approveDialog" max-width="400">
      <v-card>
        <v-card-title>Confirmer l'approbation</v-card-title>
        <v-card-text>
          Etes-vous sur de vouloir approuver cet utilisateur ?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="approveDialog = false">Annuler</v-btn>
          <v-btn color="success" variant="tonal" @click="handleApprove">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="rejectDialog" max-width="400">
      <v-card>
        <v-card-title>Rejeter l'utilisateur</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectNote"
            label="Motif du rejet (optionnel)"
            rows="3"
            hide-details
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="rejectDialog = false">Annuler</v-btn>
          <v-btn color="error" variant="tonal" @click="handleReject">Rejeter</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>