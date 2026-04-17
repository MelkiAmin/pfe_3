<script setup lang="ts">
interface Emit {
  (e: 'update:isDialogVisible', val: boolean): void
}

interface Prop {
  isDialogVisible: boolean
}

const props = defineProps<Prop>()

const emit = defineEmits<Emit>()

const selectedPlan = ref('standard')

const plansList = [
  { desc: 'Standard - $99/month', title: 'Standard', value: 'standard' },
  { desc: 'Basic - $0/month', title: 'Basic', value: 'basic' },
  { desc: 'Enterprise - $499/month', title: 'Enterprise', value: 'enterprice' },
  { desc: 'Company - $999/month', title: 'Company', value: 'company' },
]

const isConfirmDialogVisible = ref(false)

const dialogModelValueUpdate = (val: boolean) => {
  emit('update:isDialogVisible', val)
}
</script>

<template>

