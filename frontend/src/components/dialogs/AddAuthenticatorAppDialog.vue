<script setup lang="ts">
import themeselectionQr from '@images/pages/themeselection-qr.png'

interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
  (e: 'submit', value: string): void
}
interface Props {
  authCode?: string
  isDialogVisible: boolean
}
const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const authCode = ref(structuredClone(toRaw(props.authCode)))

const formSubmit = () => {
  if (authCode.value) {
    emit('submit', authCode.value)
    emit('update:isDialogVisible', false)
  }
}

const resetAuthCode = () => {
  authCode.value = structuredClone(toRaw(props.authCode))
  emit('update:isDialogVisible', false)
}
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 900"
    :model-value="props.isDialogVisible"
    @update:model-value="(val) => $emit('update:isDialogVisible', val)"
  >

