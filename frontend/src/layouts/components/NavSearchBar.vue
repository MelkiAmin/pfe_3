<script setup lang="ts">
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'

const search = ref('')
</script>

<template>
  <AppTextField
    v-model="search"
    placeholder="Search"
    density="compact"
    prepend-inner-icon="tabler-search"
    hide-details
  />
</template>
