<script setup lang="ts">
import { adminPanelApi, eventsApi, paymentsApi, ticketsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

definePage({
  meta: {
    layout: 'default',
  },
})

const authStore = useAuthStore()
const loading = ref(true)
const items = ref<any[]>([])

const title = computed(() => {
  if (authStore.role === 'admin')
    return 'Historique des validations'
  if (authStore.role === 'organizer')
    return 'Historique des événements créés'
  return 'Historique des achats'
})

const description = computed(() => {
  if (authStore.role === 'admin')
    return 'Consultez les événements approuvés et rejetés dans le workflow de modération.'
  if (authStore.role === 'organizer')
    return 'Suivez tous les événements que vous avez soumis et leur statut actuel.'
  return 'Trouvez vos paiements, billets réservés et totaux de réservation en un seul endroit.'
})

const load = async () => {
  loading.value = true
  try {
    if (authStore.role === 'admin') {
      const events = await adminPanelApi.listEvents()
      items.value = events.filter(event => ['approved', 'rejected'].includes(event.status))
    }
    else if (authStore.role === 'organizer') {
      items.value = await eventsApi.list()
    }
    else {
      try {
        const payments = await paymentsApi.listHistory()
        const tickets = await ticketsApi.listTickets()
        items.value = payments.map(payment => ({
          ...payment,
          ticket_count: tickets.filter(ticket => ticket.event === payment.event).length,
        }))
      }
      catch {
        items.value = []
      }
    }
  }
  catch {
    items.value = []
  }
  finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page-shell">
    <section class="page-hero">
      <p class="page-kicker">
        History
      </p>
      <h1 class="text-h3 mb-2">
        {{ title }}
      </h1>
      <p class="text-medium-emphasis mb-0">
        {{ description }}
      </p>
    </section>

    <VCard class="section-card">
      <VCardText class="pa-6 pa-md-8">
        <VSkeletonLoader
          v-if="loading"
          type="table"
        />

        <VTable v-else>
          <thead v-if="authStore.role === 'admin' || authStore.role === 'organizer'">
            <tr>
              <th>Event</th>
              <th v-if="authStore.role === 'admin'">
                Organizer
              </th>
              <th>Status</th>
              <th>Start date</th>
            </tr>
          </thead>

          <thead v-else>
            <tr>
              <th>Payment ID</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Tickets</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="!items.length">
              <td colspan="4" class="text-center py-8 text-medium-emphasis">
                No history available yet.
              </td>
            </tr>

            <template v-if="authStore.role === 'admin' || authStore.role === 'organizer'">
              <tr
                v-for="item in items"
                :key="item.id"
              >
                <td class="font-weight-bold">
                  {{ item.title }}
                </td>
                <td v-if="authStore.role === 'admin'">
                  {{ item.organizer_name }}
                </td>
                <td>
                  <VChip
                    size="small"
                    :color="{ pending: 'warning', approved: 'success', rejected: 'error' }[item.status] || 'default'"
                    variant="tonal"
                  >
                    {{ item.status }}
                  </VChip>
                </td>
                <td>{{ new Date(item.start_date).toLocaleString() }}</td>
              </tr>
            </template>

            <template v-else>
              <tr
                v-for="item in items"
                :key="item.id"
              >
                <td>#{{ item.id }}</td>
                <td>{{ item.amount }} {{ item.currency }}</td>
                <td>
                  <VChip
                    size="small"
                    :color="{ completed: 'success', pending: 'warning', failed: 'error', refunded: 'info' }[item.status] || 'default'"
                    variant="tonal"
                  >
                    {{ item.status }}
                  </VChip>
                </td>
                <td>{{ item.ticket_count }}</td>
              </tr>
            </template>
          </tbody>
        </VTable>
      </VCardText>
    </VCard>
  </div>
</template>
