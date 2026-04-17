<script setup lang="ts">
interface Props {
  confirmationQuestion: string
  isDialogVisible: boolean
  confirmTitle: string
  confirmMsg: string
  cancelTitle: string
  cancelMsg: string
}

interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
  (e: 'confirm', value: boolean): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()

const unsubscribed = ref(false)
const cancelled = ref(false)

const updateModelValue = (val: boolean) => {
  emit('update:isDialogVisible', val)
}

const onConfirmation = () => {
  emit('confirm', true)
  updateModelValue(false)
  unsubscribed.value = true
}

const onCancel = () => {
  emit('confirm', false)
  emit('update:isDialogVisible', false)
  cancelled.value = true
}
</script>

<template>

