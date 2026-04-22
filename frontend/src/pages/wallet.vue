<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiClient } from '@/services/http/axios'

definePage({
  meta: {
    layout: 'default',
  },
})

const loading = ref(false)
const withdrawLoading = ref(false)
const wallet = ref({ balance: 0 })
const transactions = ref<any[]>([])
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

onMounted(loadWallet)
</script>

<template>
  <div class="page-shell">
    <section class="page-hero">
      <p class="page-kicker">
        Wallet
      </p>
      <h1 class="text-h3 mb-2">
        Manage your balance and transaction history
      </h1>
      <p class="text-medium-emphasis mb-0">
        A cleaner wallet view with stronger hierarchy, clearer totals and smoother withdrawal flow.
      </p>
    </section>

    <VRow>
      <VCol cols="12" lg="4">
        <VCard class="section-card">
          <VCardText class="pa-6">
            <VAvatar
              color="primary"
              rounded="xl"
              size="56"
              class="mb-4"
            >
              <VIcon icon="tabler-wallet" />
            </VAvatar>
            <div class="text-medium-emphasis mb-1">
              Solde disponible
            </div>
            <div class="text-h3 mb-5">
              {{ loading ? '...' : Number(wallet.balance).toFixed(2) }} DT
            </div>

            <VAlert v-if="successMsg" type="success" variant="tonal" class="mb-3">
              {{ successMsg }}
            </VAlert>
            <VAlert v-if="errorMsg" type="error" variant="tonal" class="mb-3">
              {{ errorMsg }}
            </VAlert>

            <VBtn
              block
              size="large"
              color="primary"
              :disabled="Number(wallet.balance) <= 0"
              @click="showWithdrawDialog = true"
            >
              Demander un retrait
            </VBtn>
          </VCardText>
        </VCard>
      </VCol>

      <VCol cols="12" lg="8">
        <VCard class="section-card">
          <VCardText class="pa-6 pa-md-8">
            <div class="d-flex justify-space-between align-center flex-wrap gap-3 mb-6">
              <div>
                <p class="page-kicker mb-2">
                  Transactions
                </p>
                <h2 class="text-h4 mb-0">
                  Historique financier
                </h2>
              </div>
            </div>

            <VTable>
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
                  <td colspan="5" class="text-center py-8 text-medium-emphasis">
                    Aucune transaction pour l'instant.
                  </td>
                </tr>
                <tr v-for="tx in transactions" :key="tx.id">
                  <td>{{ new Date(tx.created_at).toLocaleDateString('fr-FR') }}</td>
                  <td>
                    <VChip :color="trxTypeColor(tx.trx_type)" size="small" variant="tonal">
                      {{ tx.trx_type === 'credit' ? 'Crédit' : 'Débit' }}
                    </VChip>
                  </td>
                  <td>{{ tx.details || '-' }}</td>
                  <td class="text-right font-weight-bold">
                    {{ tx.trx_type === 'credit' ? '+' : '-' }}{{ Number(tx.amount).toFixed(2) }} DT
                  </td>
                  <td class="text-right">{{ Number(tx.post_balance).toFixed(2) }} DT</td>
                </tr>
              </tbody>
            </VTable>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VDialog v-model="showWithdrawDialog" max-width="480">
      <VCard class="section-card" title="Demande de retrait">
        <VCardText>
          <p class="text-medium-emphasis mb-4">
            Solde disponible : <strong>{{ Number(wallet.balance).toFixed(2) }} DT</strong>
          </p>
          <VTextField
            v-model="withdrawForm.amount"
            label="Montant à retirer"
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
  </div>
</template>
