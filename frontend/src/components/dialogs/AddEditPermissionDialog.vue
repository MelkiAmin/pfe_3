<script setup lang="ts">
interface Props {
  isDialogVisible: boolean
  permissionName?: string
}
interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
  (e: 'update:permissionName', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  permissionName: '',
})

const emit = defineEmits<Emit>()

const currentPermissionName = ref('')

const onReset = () => {
  emit('update:isDialogVisible', false)
  currentPermissionName.value = ''
}

const onSubmit = () => {
  emit('update:isDialogVisible', false)
  emit('update:permissionName', currentPermissionName.value)
}

watch(() => props, () => {
  currentPermissionName.value = props.permissionName
})
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 600"
    :model-value="props.isDialogVisible"
    @update:model-value="onReset"
  >

