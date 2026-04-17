<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiClient } from '@/services/http/axios'

const loading = ref(false)
const withdrawLoading = ref(false)
const wallet = ref({ balance: 0 })
const transactions = ref<any[]>([])
const totalTransactions = ref(0)
const showWithdrawDialog = ref(false)
const withdrawForm = ref({ amount: '', method: 'bank_transfer', account_details: { iban: '' } })
const errorMsg = ref('')
const successMsg = ref('')

const loadWallet = async () => {
  loading.value = true
  try {
    const [walletRes, txRes] = await Promise.all([
      apiClient.get('/payments/wallet/'),
      apiClient.get('/payments/transactions/'),
    ])
    wallet.value = walletRes.data
    transactions.value = txRes.data.results || txRes.data
    totalTransactions.value = txRes.data.count ?? transactions.value.length
  }
  catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || 'Impossible de charger le wallet.'
  }
  finally {
    loading.value = false
  }
}

const submitWithdrawal = async () => {
  withdrawLoading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await apiClient.post('/payments/withdrawals/', withdrawForm.value)
    successMsg.value = 'Demande de retrait soumise avec succès.'
    showWithdrawDialog.value = false
    withdrawForm.value = { amount: '', method: 'bank_transfer', account_details: { iban: '' } }
    await loadWallet()
  }
  catch (e: any) {
    errorMsg.value = e?.response?.data?.amount?.[0] || e?.response?.data?.detail || 'Erreur lors de la demande de retrait.'
  }
  finally {
    withdrawLoading.value = false
  }
}

const trxTypeColor = (type: string) => type === 'credit' ? 'success' : 'error'
const trxTypeIcon = (type: string) => type === 'credit' ? 'ri-arrow-down-line' : 'ri-arrow-up-line'

onMounted(loadWallet)
</script>

<template>
  <VRow>
    <!-- Wallet Balance Card -->
    <VCol cols="12" md="4">
      <VCard>
        <VCardText class="pa-6">
          <div class="d-flex align-center gap-3 mb-4">
            <VAvatar color="primary" rounded size="48">
              <VIcon icon="ri-wallet-3-line" size="26" />
            </VAvatar>
            <div>
              <p class="text-sm text-medium-emphasis mb-0">Solde du Wallet</p>
              <h2 class="text-h4 font-weight-bold">
                {{ loading ? '...' : Number(wallet.balance).toFixed(2) }} €
              </h2>
            </div>
          </div>

          <VAlert v-if="successMsg" type="success" variant="tonal" class="mb-3" closable>
            {{ successMsg }}
          </VAlert>
          <VAlert v-if="errorMsg" type="error" variant="tonal" class="mb-3" closable>
            {{ errorMsg }}
          </VAlert>

          <VBtn
            block
            color="primary"
            variant="outlined"
            prepend-icon="ri-bank-line"
            :disabled="Number(wallet.balance) <= 0"
            @click="showWithdrawDialog = true"
          >
            Demander un retrait
          </VBtn>
        </VCardText>
      </VCard>
    </VCol>

    <!-- Transactions History -->
    <VCol cols="12" md="8">
      <VCard title="Historique des transactions">
        <VCardText>
          <VSkeletonLoader v-if="loading" type="table" />
          <VTable v-else>
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Détails</th>
                <th class="text-right">Montant</th>
                <th class="text-right">Solde après</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!transactions.length">
                <td colspan="5" class="text-center py-6 text-medium-emphasis">
                  Aucune transaction pour l'instant.
                </td>
              </tr>
              <tr v-for="tx in transactions" :key="tx.id">
                <td>{{ new Date(tx.created_at).toLocaleDateString('fr-FR') }}</td>
                <td>
                  <VChip :color="trxTypeColor(tx.trx_type)" size="small" variant="tonal">
                    <VIcon start :icon="trxTypeIcon(tx.trx_type)" size="14" />
                    {{ tx.trx_type === 'credit' ? 'Crédit' : 'Débit' }}
                  </VChip>
                </td>
                <td class="text-truncate" style="max-width: 200px;">
                  {{ tx.details || '—' }}
                </td>
                <td class="text-right font-weight-bold" :class="tx.trx_type === 'credit' ? 'text-success' : 'text-error'">
                  {{ tx.trx_type === 'credit' ? '+' : '-' }}{{ Number(tx.amount).toFixed(2) }} €
                </td>
                <td class="text-right">{{ Number(tx.post_balance).toFixed(2) }} €</td>
              </tr>
            </tbody>
          </VTable>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>

  <!-- Withdrawal Dialog -->
  <VDialog v-model="showWithdrawDialog" max-width="480">
    <VCard title="Demande de retrait">
      <VCardText>
        <p class="text-medium-emphasis mb-4">
          Solde disponible : <strong>{{ Number(wallet.balance).toFixed(2) }} €</strong>
        </p>
        <VTextField
          v-model="withdrawForm.amount"
          label="Montant à retirer (€)"
          type="number"
          :max="wallet.balance"
          min="1"
          class="mb-3"
        />
        <VTextField
          v-model="withdrawForm.account_details.iban"
          label="IBAN / Détails bancaires"
          class="mb-3"
        />
        <VAlert v-if="errorMsg" type="error" variant="tonal" class="mb-2">{{ errorMsg }}</VAlert>
      </VCardText>
      <VCardActions>
        <VSpacer />
        <VBtn variant="text" @click="showWithdrawDialog = false">Annuler</VBtn>
        <VBtn color="primary" :loading="withdrawLoading" @click="submitWithdrawal">
          Confirmer
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>
