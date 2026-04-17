<script setup lang="ts">
import keyboard from '@images/svg/keyboard.svg'
import paper from '@images/svg/paper-send.svg'
import rocket from '@images/svg/rocket.svg'
import { themeConfig } from '@themeConfig'

interface Props {
  isDialogVisible: boolean
}

interface Emit {
  (e: 'update:isDialogVisible', val: boolean): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()

const dialogVisibleUpdate = (val: boolean) => {
  emit('update:isDialogVisible', val)
}

const referAndEarnSteps = [
  {
    icon: paper,
    title: 'Send Invitation 👍🏻',
    subtitle: 'Send your referral link to your friend',
  },
  {
    icon: keyboard,
    title: 'Registration 😎',
    subtitle: 'Let them register to our services',
  },
  {
    icon: rocket,
    title: 'Free Trial  🎉',
    subtitle: 'Your friend will get 30 days free trial',
  },
]
</script>

<template>
  <VDialog
    :model-value="props.isDialogVisible"
    :width="$vuetify.display.smAndDown ? 'auto' : 800"
    @update:model-value="dialogVisibleUpdate"
  >

