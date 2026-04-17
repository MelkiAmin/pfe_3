<script setup lang="ts">
import { eventsApi } from '@/services/api'
import { apiClient } from '@/services/http/axios'

const props = withDefaults(defineProps<{
  modelValue?: number
  eventId?: number
  readonly?: boolean
  allowSubmit?: boolean
}>(), {
  modelValue: 0,
  readonly: false,
  allowSubmit: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
  submitted: [value: number]
}>()

const hover = ref(0)
const rating = ref(props.modelValue)
const loading = ref(false)

watch(() => props.modelValue, value => {
  rating.value = value
})

const setRating = (value: number) => {
  if (props.readonly)
    return
  rating.value = value
  emit('update:modelValue', value)
}

const submit = async () => {
  if (!props.allowSubmit || !props.eventId || props.readonly)
    return

  loading.value = true
  try {
    try {
      await apiClient.post(`/events/${props.eventId}/reviews`, { rating: rating.value })
    }
    catch {
      await eventsApi.createReview({
        event: props.eventId,
        rating: rating.value,
      })
    }
    emit('submitted', rating.value)
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="d-flex align-center gap-1">
    <button
      v-for="star in 5"
      :key="star"
      type="button"
      class="star-btn"
      :disabled="readonly"
      @mouseenter="hover = star"
      @mouseleave="hover = 0"
      @click="setRating(star)"
    >
      <VIcon
        :icon="(hover || rating) >= star ? 'tabler-star-filled' : 'tabler-star'"
        color="warning"
        size="20"
      />
    </button>

    <VBtn
      v-if="allowSubmit && !readonly"
      size="small"
      variant="text"
      :loading="loading"
      @click="submit"
    >
      Valider
    </VBtn>
  </div>
</template>

<style scoped>
.star-btn {
  border: 0;
  background: transparent;
  padding: 0;
  line-height: 1;
  cursor: pointer;
}
.star-btn:disabled {
  cursor: default;
}
</style>
