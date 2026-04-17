<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiClient } from '@/services/http/axios'

const tickets = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const showCreate = ref(false)
const newTicket = ref({ subject: '', description: '', priority: 'medium' })
const creating = ref(false)
const snackbar = ref({ show: false, message: '', color: 'success' })

const load = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/support/tickets/')
    tickets.value = data.results || data
    total.value = data.count ?? tickets.value.length
  } catch {}
  finally { loading.value = false }
}

const create = async () => {
  creating.value = true
  try {
    await apiClient.post('/support/tickets/', newTicket.value)
    snackbar.value = { show: true, message: 'Ticket créé avec succès.', color: 'success' }
    showCreate.value = false
    newTicket.value = { subject: '', description: '', priority: 'medium' }
    await load()
  } catch (e: any) {
    snackbar.value = { show: true, message: 'Erreur lors de la création.', color: 'error' }
  } finally { creating.value = false }
}

const statusColor = (s: string) => ({
  open: 'primary', in_review: 'warning', resolved: 'success', closed: 'default'
}[s] || 'default')

const priorityColor = (p: string) => ({
  low: 'default', medium: 'info', high: 'warning', urgent: 'error'
}[p] || 'default')

onMounted(load)
</script>

<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 class="text-h5">Support — Mes tickets</h2>
      <VBtn color="primary" prepend-icon="ri-add-line" @click="showCreate = true">Nouveau ticket</VBtn>
    </div>

    <VCard>
      <VCardText>
        <VSkeletonLoader v-if="loading" type="table" />
        <VTable v-else>
          <thead>
            <tr>
              <th>Référence</th>
              <th>Sujet</th>
              <th>Statut</th>
              <th>Priorité</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!tickets.length">
              <td colspan="5" class="text-center py-8 text-medium-emphasis">Aucun ticket pour l'instant.</td>
            </tr>
            <tr v-for="t in tickets" :key="t.id">
              <td class="font-weight-bold">#{{ t.ticket_ref }}</td>
              <td>{{ t.subject }}</td>
              <td><VChip :color="statusColor(t.status)" size="small" variant="tonal">{{ t.status }}</VChip></td>
              <td><VChip :color="priorityColor(t.priority)" size="small" variant="tonal">{{ t.priority }}</VChip></td>
              <td>{{ new Date(t.created_at).toLocaleDateString('fr-FR') }}</td>
            </tr>
          </tbody>
        </VTable>
      </VCardText>
    </VCard>

    <!-- Create dialog -->
    <VDialog v-model="showCreate" max-width="560">
      <VCard title="Créer un ticket de support">
        <VCardText>
          <VTextField v-model="newTicket.subject" label="Sujet" class="mb-3" />
          <VTextarea v-model="newTicket.description" label="Description" rows="4" class="mb-3" />
          <VSelect v-model="newTicket.priority" label="Priorité"
            :items="[{title:'Basse',value:'low'},{title:'Moyenne',value:'medium'},{title:'Haute',value:'high'},{title:'Urgente',value:'urgent'}]"
          />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn variant="text" @click="showCreate = false">Annuler</VBtn>
          <VBtn color="primary" :loading="creating" @click="create">Créer</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VSnackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
    </VSnackbar>
  </div>
</template>
