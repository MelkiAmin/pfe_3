<script setup lang="ts">
import LazyImage from '@/components/common/LazyImage.vue'
import type { EventListItem } from '@/services/api'

const props = defineProps<{
  event: EventListItem
}>()

const eventDetailPath = computed(() => {
  const safeSlug = typeof props.event.slug === 'string' ? props.event.slug.trim() : ''
  return safeSlug ? `/events/${safeSlug}` : `/events/id-${props.event.id}`
})

const priceLabel = computed(() => {
  if (props.event.is_free) return 'Gratuit'
  if (props.event.min_price) return `À partir de ${props.event.min_price}€`
  return 'Billets disponibles'
})
</script>

<template>
  <VCard class="event-card h-100">
    <div class="event-card__media">
      <LazyImage
        :src="event.cover_image"
        :height="250"
        alt="event cover"
      />
      <div class="event-card__overlay" />
      <div class="event-card__badges">
        <VChip
          color="primary"
          variant="flat"
          size="small"
        >
          {{ priceLabel }}
        </VChip>
        <VChip
          v-if="event.is_sold_out"
          color="error"
          size="small"
        >
          Complet
        </VChip>
      </div>
    </div>

    <VCardText class="pa-5">
      <div class="d-flex align-center justify-space-between gap-3 mb-3">
        <div class="event-card__date">
          {{ new Date(event.start_date).toLocaleDateString() }}
        </div>
        <div class="event-card__city">
          {{ event.city || 'Online' }}
        </div>
      </div>

      <h3 class="text-h5 mb-2">
        {{ event.title }}
      </h3>

      <p class="text-medium-emphasis mb-4">
        {{ event.category?.description || 'A curated event experience with seamless ticket booking and modern attendee flow.' }}
      </p>

      <div class="d-flex align-center justify-space-between gap-4">
        <div>
          <div class="text-body-2 text-medium-emphasis">
            Organisateur
          </div>
          <div class="font-weight-bold">
            {{ event.organizer_name }}
          </div>
        </div>

        <VBtn
          color="primary"
          rounded="pill"
          :to="eventDetailPath"
        >
          Consulter
        </VBtn>
      </div>
    </VCardText>
  </VCard>
</template>

<style scoped>
.event-card {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 28px;
  background: rgba(var(--v-theme-surface), 0.98);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.07);
}

.event-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.13);
}

.event-card__media {
  position: relative;
}

.event-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.28) 100%);
}

.event-card__badges {
  position: absolute;
  inset-block-start: 1rem;
  inset-inline: 1rem;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.event-card__date {
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgb(var(--v-theme-primary));
}

.event-card__city {
  font-size: 0.9rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
</style>
