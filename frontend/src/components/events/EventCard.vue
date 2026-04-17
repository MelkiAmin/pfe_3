<script setup lang="ts">
import LazyImage from '@/components/common/LazyImage.vue'
import type { EventListItem } from '@/services/api'

const props = defineProps<{
  event: EventListItem
}>()

const eventDetailPath = computed(() => {
  const safeSlug = typeof props.event.slug === 'string' ? props.event.slug.trim() : ''
  if (safeSlug)
    return `/events/${safeSlug}`

  return `/events/id-${props.event.id}`
})
</script>

<template>
  <VCard
    class="h-100"
    variant="outlined"
  >
    <LazyImage
      :src="event.cover_image"
      :height="180"
      alt="event cover"
    />

    <VCardText>
      <div class="d-flex justify-space-between align-center gap-2 mb-2">
        <VChip
          v-if="event.is_free"
          color="success"
          size="small"
        >
          {{ $t('event.free') }}
        </VChip>
        <VChip
          v-else
          size="small"
          color="primary"
          variant="tonal"
        >
          {{ Number(event.tickets_sold) > 0 ? `${event.tickets_sold} vendus` : 'Payant' }}
        </VChip>
        <VChip
          v-if="event.is_sold_out"
          color="error"
          size="small"
        >
          Complet
        </VChip>
      </div>

      <h4 class="text-h6 mb-2">
        {{ event.title }}
      </h4>
      <p class="text-body-2 mb-1">
        <VIcon
          icon="tabler-calendar-time"
          size="16"
          class="me-1"
        />
        {{ new Date(event.start_date).toLocaleString() }}
      </p>
      <p class="text-body-2 mb-4">
        <VIcon
          icon="tabler-map-pin"
          size="16"
          class="me-1"
        />
        {{ event.city || 'En ligne' }}
      </p>

      <VBtn
        block
        :to="eventDetailPath"
      >
        {{ $t('event.view_details') }}
      </VBtn>
    </VCardText>
  </VCard>
</template>
