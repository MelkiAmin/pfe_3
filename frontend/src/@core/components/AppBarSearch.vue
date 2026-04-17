<script setup lang="ts" generic="T extends unknown">
import { PerfectScrollbar } from 'vue3-perfect-scrollbar'
import { VList, VListItem } from 'vuetify/components/VList'

interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
  (e: 'search', value: string): void
}

interface Props {
  isDialogVisible: boolean
  searchResults: T[]
  isLoading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const { ctrl_k, meta_k } = useMagicKeys({
  passive: false,
  onEventFired(e) {
    if (e.ctrlKey && e.key === 'k' && e.type === 'keydown')
      e.preventDefault()
  },
})

const refSearchList = ref<VList>()
const refSearchInput = ref<HTMLInputElement>()
const searchQueryLocal = ref('')

watch([
  ctrl_k, meta_k,
], () => {
  emit('update:isDialogVisible', true)
})

const clearSearchAndCloseDialog = () => {
  searchQueryLocal.value = ''
  emit('update:isDialogVisible', false)
}

const getFocusOnSearchList = (e: KeyboardEvent) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    refSearchList.value?.focus('next')
  }
  else if (e.key === 'ArrowUp') {
    e.preventDefault()
    refSearchList.value?.focus('prev')
  }
}

const dialogModelValueUpdate = (val: boolean) => {
  searchQueryLocal.value = ''
  emit('update:isDialogVisible', val)
}

watch(
  () => props.isDialogVisible,
  () => { searchQueryLocal.value = '' },
)
</script>

<template>
  <VDialog
    max-width="600"
    :model-value="props.isDialogVisible"
    :height="$vuetify.display.smAndUp ? '531' : '100%'"
    :fullscreen="$vuetify.display.width < 600"
    class="app-bar-search-dialog"
    @update:model-value="dialogModelValueUpdate"
    @keyup.esc="clearSearchAndCloseDialog"
  >
    <VCard
      height="100%"
      width="100%"
      class="position-relative"
    >
      <VCardText
        class="px-4"
        style="padding-block: 1rem 1.2rem;"
      >

