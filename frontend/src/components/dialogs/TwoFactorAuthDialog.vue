<script setup lang="ts">
interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
}
interface Props {
  isDialogVisible: boolean
  smsCode?: string
  authAppCode?: string
}

const props = withDefaults(defineProps<Props>(), {
  isDialogVisible: false,
  smsCode: '',
  authAppCode: '',
})

const emit = defineEmits<Emit>()

const authMethods = [
  {
    icon: 'tabler-settings',
    title: 'Authenticator Apps',
    desc: 'Get code from an app like Google Authenticator or Microsoft Authenticator.',
    value: 'authApp',
  },
  {
    icon: 'tabler-message',
    title: 'SMS',
    desc: 'We will send a code via SMS if you need to use your backup login method.',
    value: 'sms',
  },
]

const selectedMethod = ref('authApp')
const isAuthAppDialogVisible = ref(false)
const isSmsDialogVisible = ref(false)

const openSelectedMethodDialog = () => {
  if (selectedMethod.value === 'authApp') {
    isAuthAppDialogVisible.value = true
    isSmsDialogVisible.value = false
    emit('update:isDialogVisible', false)
  }
  if (selectedMethod.value === 'sms') {
    isAuthAppDialogVisible.value = false
    isSmsDialogVisible.value = true
    emit('update:isDialogVisible', false)
  }
}
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 800"
    :model-value="props.isDialogVisible"
    @update:model-value="(val) => $emit('update:isDialogVisible', val)"
  >

