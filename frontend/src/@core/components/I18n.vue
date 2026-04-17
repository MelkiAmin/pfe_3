<script setup lang="ts">
import type { I18nLanguage } from '@layouts/types'

interface Props {
  languages: I18nLanguage[]
  location?: any
}

const props = withDefaults(defineProps<Props>(), {
  location: 'bottom end',
})

const { locale } = useI18n({ useScope: 'global' })
</script>

<template>
  <IconBtn>
    <VIcon icon="tabler-language" />

