<script setup lang="ts" generic="T extends Record<string, any>">
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'

type Column<T> = {
  key: keyof T | string
  title: string
  sortable?: boolean
}

const props = withDefaults(defineProps<{
  items: T[]
  columns: Column<T>[]
  loading?: boolean
  rowsPerPage?: number
}>(), {
  loading: false,
  rowsPerPage: 10,
})

const search = ref('')
const page = ref(1)
const sortKey = ref<string>('')
const sortDesc = ref(false)

const filteredItems = computed(() => {
  let data = [...props.items]
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter(item =>
      Object.values(item).some(v => String(v).toLowerCase().includes(q)))
  }

  if (sortKey.value) {
    data.sort((a, b) => {
      const va = a[sortKey.value]
      const vb = b[sortKey.value]
      if (va === vb)
        return 0
      return (va > vb ? 1 : -1) * (sortDesc.value ? -1 : 1)
    })
  }

  return data
})

const pageCount = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / props.rowsPerPage)))
const paginatedItems = computed(() => {
  const start = (page.value - 1) * props.rowsPerPage
  return filteredItems.value.slice(start, start + props.rowsPerPage)
})

const toggleSort = (key: string) => {
  if (sortKey.value === key) {
    sortDesc.value = !sortDesc.value
    return
  }
  sortKey.value = key
  sortDesc.value = false
}
</script>

<template>
  <div class="data-table">
    <div class="d-flex justify-space-between align-center mb-3 gap-3">
      <AppTextField
        v-model="search"
        placeholder="Rechercher..."
        prepend-inner-icon="tabler-search"
      />
      <slot name="actions" />
    </div>

    <VTable>
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="String(col.key)"
          >
            <button
              v-if="col.sortable"
              class="sort-btn"
              @click="toggleSort(String(col.key))"
            >
              {{ col.title }}
              <VIcon
                size="14"
                :icon="sortKey === String(col.key) && sortDesc ? 'tabler-chevron-down' : 'tabler-chevron-up'"
              />
            </button>
            <span v-else>{{ col.title }}</span>
          </th>
          <th>
            Actions
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td
            :colspan="columns.length + 1"
            class="text-center py-6"
          >
            Chargement...
          </td>
        </tr>
        <tr
          v-for="item in paginatedItems"
          v-else
          :key="item.id || JSON.stringify(item)"
        >
          <td
            v-for="col in columns"
            :key="String(col.key)"
          >
            <slot
              :name="`cell-${String(col.key)}`"
              :item="item"
            >
              {{ item[col.key as keyof T] }}
            </slot>
          </td>
          <td>
            <slot
              name="row-actions"
              :item="item"
            />
          </td>
        </tr>
      </tbody>
    </VTable>

    <div class="d-flex justify-end mt-3">
      <VPagination
        v-model="page"
        :length="pageCount"
        :total-visible="5"
      />
    </div>
  </div>
</template>

<style scoped>
.sort-btn {
  border: 0;
  background: transparent;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-weight: 600;
}
</style>
