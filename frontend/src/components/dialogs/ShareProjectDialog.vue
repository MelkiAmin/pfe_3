<script setup lang="ts">
import avatar1 from '@images/avatars/avatar-1.png'
import avatar2 from '@images/avatars/avatar-2.png'
import avatar3 from '@images/avatars/avatar-3.png'
import avatar4 from '@images/avatars/avatar-4.png'
import avatar5 from '@images/avatars/avatar-5.png'
import avatar6 from '@images/avatars/avatar-6.png'
import avatar7 from '@images/avatars/avatar-7.png'
import avatar8 from '@images/avatars/avatar-8.png'

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

type Permission = 'Owner' | 'Can Edit' | 'Can Comment' | 'Can View'

interface Member {
  avatar: string
  name: string
  email: string
  permission: Permission
}

const membersList: Member[] = [
  {
    avatar: avatar1,
    name: 'Lester Palmer',
    email: 'jerrod98@gmail.com',
    permission: 'Can Edit',
  },
  {
    avatar: avatar2,
    name: 'Mattie Blair',
    email: 'prudence.boehm@yahoo.com',
    permission: 'Owner',
  },
  {
    avatar: avatar3,
    name: 'Marvin Wheeler',
    email: 'rumet@jujpejah.net',
    permission: 'Can Comment',
  },
  {
    avatar: avatar4,
    name: 'Nannie Ford',
    email: 'negza@nuv.io',
    permission: 'Can View',
  },
  {
    avatar: avatar5,
    name: 'Julian Murphy',
    email: 'lunebame@umdomgu.net',
    permission: 'Can Edit',
  },
  {
    avatar: avatar6,
    name: 'Sophie Gilbert',
    email: 'ha@sugit.gov',
    permission: 'Can View',
  },
  {
    avatar: avatar7,
    name: 'Chris Watkins',
    email: 'zokap@mak.org',
    permission: 'Can Comment',
  },
  {
    avatar: avatar8,
    name: 'Adelaide Nichols',
    email: 'ujinomu@jigo.com',
    permission: 'Can Edit',
  },
]
</script>

<template>
  <VDialog
    :model-value="props.isDialogVisible"
    :width="$vuetify.display.smAndDown ? 'auto' : 900"
    @update:model-value="dialogVisibleUpdate"
  >

