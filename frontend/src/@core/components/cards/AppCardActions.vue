<script setup lang="ts">
interface Props {
  collapsed?: boolean
  noActions?: boolean
  actionCollapsed?: boolean
  actionRefresh?: boolean
  actionRemove?: boolean
  loading?: boolean | undefined
  title?: string
}

interface Emit {
  (e: 'collapsed', isContentCollapsed: boolean): void
  (e: 'refresh', stopLoading: () => void): void
  (e: 'trash'): void
  (e: 'initialLoad'): void
  (e: 'update:loading', loading: boolean): void
}

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
  noActions: false,
  actionCollapsed: false,
  actionRefresh: false,
  actionRemove: false,
  loading: undefined,
  title: undefined,
})

const emit = defineEmits<Emit>()

const _loading = ref(false)

const $loading = computed({
  get() {
    return props.loading !== undefined ? props.loading : _loading.value
  },

  set(value: boolean) {
    props.loading !== undefined ? emit('update:loading', value) : _loading.value = value
  },
})

const isContentCollapsed = ref(props.collapsed)
const isCardRemoved = ref(false)

const stopLoading = () => {
  $loading.value = false
}

const triggerCollapse = () => {
  isContentCollapsed.value = !isContentCollapsed.value
  emit('collapsed', isContentCollapsed.value)
}

const triggerRefresh = () => {
  $loading.value = true
  emit('refresh', stopLoading)
}

const triggeredRemove = () => {
  isCardRemoved.value = true
  emit('trash')
}
</script>

<template>
  <VExpandTransition>

