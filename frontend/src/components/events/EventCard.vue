<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import LazyImage from '@/components/common/LazyImage.vue'
import type { EventListItem } from '@/services/api'

const props = defineProps<{
  event: EventListItem
}>()

const router = useRouter()

const handleConsultClick = () => {
  const eventId = props.event?.id
  if (!eventId) return
  router.push(`/events/${eventId}`)
}

const priceLabel = computed(() => {
  if (props.event.is_free) return 'Gratuit'
  if (props.event.min_price) return `À partir de ${props.event.min_price} DT`
  return 'Billets disponibles'
})

const isSoldOut = computed(() => {
  return props.event.tickets_available === 0 || props.event.is_sold_out
})

const ticketsLabel = computed(() => {
  const available = props.event.tickets_available
  if (!available && available !== 0) return ''
  if (available === 0 || isSoldOut.value) return 'Complet'
  return `${available} billets disponibles`
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <VCard class="event-card h-100" hover>
    <div class="event-card__media">
      <LazyImage
        :src="event.cover_image"
        :height="200"
        alt="event cover"
        class="event-card__image"
      />
      <div class="event-card__overlay" />
      <div class="event-card__badges">
        <VChip
          :color="event.is_free ? 'success' : 'primary'"
          variant="flat"
          size="small"
          class="font-weight-semibold"
        >
          {{ priceLabel }}
        </VChip>
        <VChip
          v-if="ticketsLabel && !isSoldOut"
          color="info"
          variant="flat"
          size="small"
        >
          {{ ticketsLabel }}
        </VChip>
        <VChip
          v-if="isSoldOut"
          color="error"
          variant="flat"
          size="small"
        >
          Complet
        </VChip>
        <VChip
          v-if="event.is_expired"
          color="warning"
          variant="flat"
          size="small"
        >
          Expiré
        </VChip>
      </div>
      <div v-if="event.category" class="event-card__category">
        <VChip
          size="x-small"
          variant="flat"
          color="white"
          class="text-primary font-weight-medium"
        >
          {{ event.category.name }}
        </VChip>
      </div>
    </div>

    <VCardText class="event-card__content">
      <div class="event-card__meta">
        <div class="event-card__date">
          <VIcon icon="tabler-calendar" size="14" class="mr-1" />
          {{ formatDate(event.start_date) }}
        </div>
        <div v-if="event.city" class="event-card__location">
          <VIcon icon="tabler-map-pin" size="14" class="mr-1" />
          {{ event.city }}
        </div>
      </div>

      <h3 class="event-card__title">
        {{ event.title }}
      </h3>

      <p class="event-card__description">
        {{ event.category?.description || 'Réservez vos billets pour cet événement incroyable' }}
      </p>

      <div class="event-card__footer">
        <div class="event-card__organizer">
          <VAvatar size="24" color="primary" variant="tonal">
            <span class="text-caption">{{ event.organizer_name?.charAt(0) || 'O' }}</span>
          </VAvatar>
          <span class="text-body-2">{{ event.organizer_name }}</span>
        </div>

        <VBtn
          color="primary"
          variant="flat"
          size="small"
          rounded="lg"
          class="event-card__btn"
          @click="handleConsultClick"
        >
          <VIcon icon="tabler-arrow-right" size="18" class="mr-1" />
          Consulter
        </VBtn>
      </div>
    </VCardText>
  </VCard>
</template>

<style scoped>
.event-card {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), 0.08);
  border-radius: 20px;
  background: rgb(var(--v-theme-surface));
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.03);
}

.event-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.15), 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(99, 102, 241, 0.3);
}

.event-card__media {
  position: relative;
  overflow: hidden;
}

.event-card__image {
  transition: transform 0.4s ease;
}

.event-card:hover .event-card__image {
  transform: scale(1.08);
}

.event-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(0, 0, 0, 0.5) 100%);
  pointer-events: none;
}

.event-card__badges {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  z-index: 1;
}

.event-card__category {
  position: absolute;
  bottom: 12px;
  left: 12px;
  z-index: 1;
}

.event-card__content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-card__meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.event-card__date,
.event-card__location {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-weight: 500;
}

.event-card__title {
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.3;
  color: rgb(var(--v-theme-on-surface));
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-card__description {
  font-size: 0.85rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), 0.08);
}

.event-card__organizer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-card__btn {
  font-weight: 600;
  letter-spacing: 0.02em;
}
</style>
