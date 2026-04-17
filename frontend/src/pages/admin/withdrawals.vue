<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiClient } from '@/services/http/axios'

const loading = ref(false)
const withdrawals = ref<any[]>([])
const actionLoading = ref<number | null>(null)
const feedback = ref('')
const snackbar = ref({ show: false, message: '', color: 'success' })

const loadWithdrawals = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/payments/admin/withdrawals/')
    withdrawals.value = data.results || data
  }
  catch (e: any) {
    snackbar.value = { show: true, message: 'Impossible de charger les retraits.', color: 'error' }
  }
  finally {
    loading.value = false
  }
}

const handleAction = async (id: number, action: 'approve' | 'reject') => {
  actionLoading.value = id
  try {
    await apiClient.post(`/payments/admin/withdrawals/${id}/action/`, {
      action,
      admin_feedback: feedback.value,
    })
    snackbar.value = {
      show: true,
      message: action === 'approve' ? 'Retrait approuvé ✓' : 'Retrait rejeté',
      color: action === 'approve' ? 'success' : 'warning',
    }
    feedback.value = ''
    await loadWithdrawals()
  }
  catch (e: any) {
    snackbar.value = {
      show: true,
      message: e?.response?.data?.detail || 'Erreur lors du traitement.',
      color: 'error',
    }
  }
  finally {
    actionLoading.value = null
  }
}

const statusColor = (s: string) => ({ pending: 'warning', approved: 'success', rejected: 'error' }[s] || 'default')

onMounted(loadWithdrawals)
</script>

<template>
  <VCard title="Demandes de retrait" subtitle="Gérer les retraits des organisateurs">
    <VCardText>
      <VSkeletonLoader v-if="loading" type="table" />
      <VTable v-else>
        <thead>
          <tr>
            <th>#</th>
            <th>Utilisateur</th>
            <th>Montant</th>
            <th>Méthode</th>
            <th>Statut</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!withdrawals.length">
            <td colspan="7" class="text-center py-8 text-medium-emphasis">
              Aucune demande de retrait en attente.
            </td>
          </tr>
          <tr v-for="wr in withdrawals" :key="wr.id">
            <td>#{{ wr.id }}</td>
            <td>{{ wr.user?.email || wr.user }}</td>
            <td class="font-weight-bold">{{ Number(wr.amount).toFixed(2) }} €</td>
            <td>{{ wr.method }}</td>
            <td>
              <VChip :color="statusColor(wr.status)" size="small" variant="tonal">
                {{ wr.status }}
              </VChip>
            </td>
            <td>{{ new Date(wr.created_at).toLocaleDateString('fr-FR') }}</td>
            <td>
              <template v-if="wr.status === 'pending'">
                <VBtn
                  icon="ri-check-line"
                  color="success"
                  variant="text"
                  size="small"
                  :loading="actionLoading === wr.id"
                  @click="handleAction(wr.id, 'approve')"
                />
                <VBtn
                  icon="ri-close-line"
                  color="error"
                  variant="text"
                  size="small"
                  :loading="actionLoading === wr.id"
                  @click="handleAction(wr.id, 'reject')"
                />
              </template>
              <span v-else class="text-medium-emphasis text-sm">—</span>
            </td>
          </tr>
        </tbody>
      </VTable>
    </VCardText>
  </VCard>

  <VSnackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
    {{ snackbar.message }}
  </VSnackbar>
</template>
