<script setup lang="ts">
interface Details {
  number: string | number
  name: string
  expiry: string
  cvv: string
  isPrimary: boolean
  type: string
}
interface Emit {
  (e: 'submit', value: Details): void
  (e: 'update:isDialogVisible', value: boolean): void
}

interface Props {
  cardDetails?: Details
  isDialogVisible: boolean
}

const props = withDefaults(defineProps<Props>(), {
  cardDetails: () => ({
    number: '',
    name: '',
    expiry: '',
    cvv: '',
    isPrimary: false,
    type: '',
  }),
})

const emit = defineEmits<Emit>()

const cardDetails = ref<Details>(structuredClone(toRaw(props.cardDetails)))

watch(() => props, () => {
  cardDetails.value = structuredClone(toRaw(props.cardDetails))
})

const formSubmit = () => {
  emit('submit', cardDetails.value)
}

const dialogModelValueUpdate = (val: boolean) => {
  emit('update:isDialogVisible', val)
}
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 600"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogModelValueUpdate"
  >

