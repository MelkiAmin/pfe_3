<script setup lang="ts">
import { apiClient } from '@/services/http/axios'

type TicketRecord = {
  id: number
  order_id: number
  event_title: string
  ticket_code: string
  status: string
  attendee_email: string
}

const tickets = ref<TicketRecord[]>([])
const loading = ref(true)

const fetchTickets = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/orders', { params: { status: 'paid' } })
    tickets.value = Array.isArray(data) ? data : data.results || []
  }
  catch {
    tickets.value = []
  }
  finally {
    loading.value = false
  }
}

const qrUrl = (code: string) =>
  `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(code)}`

const downloadPdf = (ticket: TicketRecord) => {
  const content = `Billet #${ticket.ticket_code}\nEvenement: ${ticket.event_title}\nCommande: ${ticket.order_id}`
  const blob = new Blob([content], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ticket-${ticket.ticket_code}.pdf`
  a.click()
  URL.revokeObjectURL(url)
}

const sendByEmail = async (ticket: TicketRecord) => {
  await apiClient.post(`/orders/${ticket.order_id}/send-ticket`, { ticket_id: ticket.id })
}

onMounted(fetchTickets)
</script>

<template>
  <VCard>
    <VCardItem title="Mes billets" />
    <VDivider />
    <VCardText>
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
                :src="qrUrl(ticket.ticket_code)"
                alt="qr"
                width="140"
                height="140"
              >
              <p class="text-body-2 mt-3 mb-1">
                Code: {{ ticket.ticket_code }}
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
