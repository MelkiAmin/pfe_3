<script setup lang="ts">
import { VForm } from 'vuetify/components/VForm'

interface Permission {
  name: string
  read: boolean
  write: boolean
  create: boolean
}

interface Roles {
  name: string
  permissions: Permission[]
}

interface Props {
  rolePermissions?: Roles
  isDialogVisible: boolean
}
interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
  (e: 'update:rolePermissions', value: Roles): void
}

const props = withDefaults(defineProps<Props>(), {
  rolePermissions: () => ({
    name: '',
    permissions: [],
  }),
})

const emit = defineEmits<Emit>()

const permissions = ref<Permission[]>([
  {
    name: 'User Management',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Content Management',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Disputes Management',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Database Management',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Financial Management',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Reporting',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'API Control',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Repository Management',
    read: false,
    write: false,
    create: false,
  },
  {
    name: 'Payroll',
    read: false,
    write: false,
    create: false,
  },
])

const isSelectAll = ref(false)
const role = ref('')
const refPermissionForm = ref<VForm>()

const checkedCount = computed(() => {
  let counter = 0

  permissions.value.forEach(permission => {
    Object.entries(permission).forEach(([key, value]) => {
      if (key !== 'name' && value)
        counter++
    })
  })

  return counter
})

const isIndeterminate = computed(() => checkedCount.value > 0 && checkedCount.value < (permissions.value.length * 3))

watch(isSelectAll, val => {
  permissions.value = permissions.value.map(permission => ({
    ...permission,
    read: val,
    write: val,
    create: val,
  }))
})

watch(isIndeterminate, () => {
  if (!isIndeterminate.value)
    isSelectAll.value = false
})

watch(permissions, () => {
  if (checkedCount.value === (permissions.value.length * 3))
    isSelectAll.value = true
}, { deep: true })

watch(() => props, () => {
  if (props.rolePermissions && props.rolePermissions.permissions.length) {
    role.value = props.rolePermissions.name
    permissions.value = permissions.value.map(permission => {
      const rolePermission = props.rolePermissions?.permissions.find(item => item.name === permission.name)

      if (rolePermission) {
        return {
          ...permission,
          ...rolePermission,
        }
      }

      return permission
    })
  }
})

const onSubmit = () => {
  const rolePermissions = {
    name: role.value,
    permissions: permissions.value,
  }

  emit('update:rolePermissions', rolePermissions)
  emit('update:isDialogVisible', false)
  isSelectAll.value = false
  refPermissionForm.value?.reset()
}

const onReset = () => {
  emit('update:isDialogVisible', false)
  isSelectAll.value = false
  refPermissionForm.value?.reset()
}
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 900"
    :model-value="props.isDialogVisible"
    @update:model-value="onReset"
  >

