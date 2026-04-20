<script setup lang="ts">
import type { Ticket } from '@/services/api'
import { apiClient } from '@/services/http/axios'

const tickets = ref<Ticket[]>([])
const loading = ref(true)
const feedback = ref('')

const fetchTickets = async () => {
  loading.value = true
  feedback.value = ''
  try {
    const { data } = await apiClient.get('/tickets/')
    tickets.value = Array.isArray(data) ? data : data.results || []
  }
  catch {
    tickets.value = []
    feedback.value = 'Impossible de charger vos billets pour le moment.'
  }
  finally {
    loading.value = false
  }
}

const qrUrl = (code: string) =>
  `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(code)}`

const downloadPdf = (ticket: Ticket) => {
  const content = `Billet #${ticket.ticket_number}\nEvenement: ${ticket.event_title}\nStatut: ${ticket.status}`
  const blob = new Blob([content], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ticket-${ticket.ticket_number}.pdf`
  a.click()
  URL.revokeObjectURL(url)
}

const sendByEmail = (ticket: Ticket) => {
  feedback.value = `L'email de confirmation pour ${ticket.event_title} est envoyee automatiquement apres paiement.`
}

onMounted(fetchTickets)
</script>

<template>
  <VCard>
    <VCardItem title="Mes billets" />
    <VDivider />
    <VCardText>
      <VAlert
        v-if="feedback"
        type="info"
        variant="tonal"
        class="mb-4"
        closable
        @click:close="feedback = ''"
      >
        {{ feedback }}
      </VAlert>
      <VSkeletonLoader
        v-if="loading"
        type="list-item-two-line@4"
      />
      <VRow v-else>
        <VCol
          v-for="ticket in tickets"
          :key="ticket.id"
          cols="12"
          md="6"
          lg="4"
        >
            <VCard variant="outlined">
              <VCardItem :title="ticket.event_title" />
            <VCardText>
              <img
                :src="ticket.qr_code || qrUrl(ticket.ticket_number)"
                alt="qr"
                width="140"
                height="140"
              >
              <p class="text-body-2 mt-3 mb-1">
                Code: {{ ticket.ticket_number }}
              </p>
              <p class="text-body-2 mb-1">
                Statut: {{ ticket.status }}
              </p>
              <div class="d-flex gap-2 mt-2">
                <VBtn
                  size="small"
                  variant="tonal"
                  @click="downloadPdf(ticket)"
                >
                  PDF
                </VBtn>
                <VBtn
                  size="small"
                  variant="text"
                  @click="sendByEmail(ticket)"
                >
                  Envoyer email
                </VBtn>
              </div>
            </VCardText>
          </VCard>
        </VCol>
      </VRow>
    </VCardText>
  </VCard>
</template>
