<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  title?: string
  width?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const dialog = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value),
})
</script>

<template>
  <VDialog
    v-model="dialog"
    :max-width="width || 640"
    persistent
    role="dialog"
    aria-modal="true"
  >
    <VCard>
      <VCardItem v-if="title">
        <VCardTitle>{{ title }}</VCardTitle>
        <template #append>
          <IconBtn @click="dialog = false">
            <VIcon icon="tabler-x" />
          </IconBtn>
        </template>
      </VCardItem>

      <VCardText>
        <slot name="body">
          <slot />
        </slot>
      </VCardText>

      <VCardActions>
        <slot name="footer">
          <VSpacer />
          <VBtn
            variant="text"
            @click="dialog = false"
          >
            Fermer
          </VBtn>
        </slot>
      </VCardActions>
    </VCard>
  </VDialog>
</template>
