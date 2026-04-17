<script setup lang="ts">
import { Bar, Doughnut } from 'vue-chartjs'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { apiClient } from '@/services/http/axios'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const loading = ref(true)
const errorMessage = ref('')
const stats = ref({
  total_events: 0,
  published_events: 0,
  draft_events: 0,
  cancelled_events: 0,
  total_tickets_sold: 0,
  total_revenue: '0.00',
  avg_fill_rate: 0,
  recent_events: [] as any[],
  top_events: [] as any[],
})

const revenueChartData = computed(() => ({
  labels: stats.value.top_events.map(e => e.title?.substring(0, 20) + '…' || ''),
  datasets: [{
    label: 'Revenus (€)',
    backgroundColor: 'rgba(25,118,210,0.75)',
    borderRadius: 6,
    data: stats.value.top_events.map(e => Number(e.revenue)),
  }],
}))

const ticketChartData = computed(() => ({
  labels: stats.value.top_events.map(e => e.title?.substring(0, 15) + '…' || ''),
  datasets: [{
    label: 'Billets vendus',
    backgroundColor: [
      '#1976d2', '#42a5f5', '#90caf9', '#bbdefb', '#e3f2fd',
    ],
    data: stats.value.top_events.map(e => e.sold),
  }],
}))

const chartOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true } },
}

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await apiClient.get('/organizer/dashboard/')
    stats.value = data
  }
  catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || 'Impossible de charger le dashboard.'
  }
  finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <VAlert v-if="errorMessage" type="error" variant="tonal" class="mb-4">{{ errorMessage }}</VAlert>

    <!-- KPI Cards -->
    <VRow class="mb-4">
      <VCol v-for="kpi in [
        { label: 'Événements totaux', value: stats.total_events, icon: 'ri-calendar-event-line', color: 'primary' },
        { label: 'Publiés', value: stats.published_events, icon: 'ri-checkbox-circle-line', color: 'success' },
        { label: 'Billets vendus', value: stats.total_tickets_sold, icon: 'ri-ticket-2-line', color: 'warning' },
        { label: 'Revenus totaux', value: Number(stats.total_revenue).toFixed(2) + ' €', icon: 'ri-money-euro-circle-line', color: 'info' },
      ]" :key="kpi.label" cols="12" sm="6" lg="3">
        <VCard :loading="loading">
          <VCardText class="d-flex align-center gap-4">
            <VAvatar :color="kpi.color" rounded size="48">
              <VIcon :icon="kpi.icon" size="26" />
            </VAvatar>
            <div>
              <p class="text-sm text-medium-emphasis mb-0">{{ kpi.label }}</p>
              <h3 class="text-h5 font-weight-bold">
                {{ loading ? '…' : kpi.value }}
              </h3>
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <!-- Fill rate + Charts -->
    <VRow class="mb-4">
      <VCol cols="12" md="4">
        <VCard title="Taux de remplissage moyen">
          <VCardText class="text-center">
            <VSkeletonLoader v-if="loading" type="paragraph" />
            <template v-else>
              <h1 class="text-h2 font-weight-black text-primary">{{ stats.avg_fill_rate }}%</h1>
              <VProgressLinear :model-value="stats.avg_fill_rate" color="primary" rounded height="8" class="mt-3" />
              <p class="text-medium-emphasis text-sm mt-2">Moyenne sur les événements avec capacité définie</p>
            </template>
          </VCardText>
        </VCard>
      </VCol>

      <VCol cols="12" md="8">
        <VCard title="Revenus par événement (Top 5)">
          <VCardText>
            <VSkeletonLoader v-if="loading" type="image" />
            <Bar v-else-if="stats.top_events.length" :data="revenueChartData" :options="chartOptions" style="max-height:220px" />
            <p v-else class="text-center text-medium-emphasis py-8">Pas encore de données.</p>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <!-- Recent Events Table -->
    <VCard title="Événements récents">
      <VCardText>
        <VTable>
          <thead>
            <tr>
              <th>Titre</th>
              <th>Statut</th>
              <th>Date début</th>
              <th>Créé le</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="4"><VSkeletonLoader type="table-row@3" /></td>
            </tr>
            <tr v-else-if="!stats.recent_events.length">
              <td colspan="4" class="text-center py-6 text-medium-emphasis">Aucun événement pour l'instant.</td>
            </tr>
            <tr v-for="event in stats.recent_events" :key="event.id">
              <td class="font-weight-medium">{{ event.title }}</td>
              <td>
                <VChip
                  :color="{ published: 'success', draft: 'warning', cancelled: 'error', completed: 'info' }[event.status] || 'default'"
                  size="small" variant="tonal"
                >{{ event.status }}</VChip>
              </td>
              <td>{{ event.start_date ? new Date(event.start_date).toLocaleDateString('fr-FR') : '—' }}</td>
              <td>{{ event.created_at ? new Date(event.created_at).toLocaleDateString('fr-FR') : '—' }}</td>
            </tr>
          </tbody>
        </VTable>
      </VCardText>
    </VCard>
  </div>
</template>
