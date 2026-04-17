<script setup lang="ts">
import FlatPickr from 'vue-flatpickr-component'
import { useTheme } from 'vuetify'

import { VField, makeVFieldProps } from 'vuetify/lib/components/VField/VField'

import { VInput, makeVInputProps } from 'vuetify/lib/components/VInput/VInput'

import { filterInputAttrs } from 'vuetify/lib/util/helpers'

import { useConfigStore } from '@core/stores/config'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps({
  autofocus: Boolean,
  counter: [Boolean, Number, String] as PropType<true | number | string>,
  counterValue: Function as PropType<(value: any) => number>,
  prefix: String,
  placeholder: String,
  persistentPlaceholder: Boolean,
  persistentCounter: Boolean,
  suffix: String,
  type: {
    type: String,
    default: 'text',
  },
  modelModifiers: Object as PropType<Record<string, boolean>>,
  ...makeVInputProps({
    density: 'comfortable',
    hideDetails: 'auto',
  }),
  ...makeVFieldProps({
    variant: 'outlined',
    color: 'primary',
  }),
})

const emit = defineEmits<Emit>()

interface Emit {
  (e: 'click:control', val: MouseEvent): true
  (e: 'mousedown:control', val: MouseEvent): true
  (e: 'update:focused', val: MouseEvent): true
  (e: 'update:modelValue', val: string): void
  (e: 'click:clear', el: MouseEvent): void
}

const configStore = useConfigStore()
const attrs = useAttrs()

const [rootAttrs, compAttrs] = filterInputAttrs(attrs)
const inputProps = ref(VInput.filterProps(props))
const fieldProps = ref(VField.filterProps(props))

const refFlatPicker = ref()

const { focused } = useFocus(refFlatPicker)
const isCalendarOpen = ref(false)
const isInlinePicker = ref(false)

if (compAttrs.config && compAttrs.config.inline) {
  isInlinePicker.value = compAttrs.config.inline
  Object.assign(compAttrs, { altInputClass: 'inlinePicker' })
}

compAttrs.config = {
  ...compAttrs.config,
  prevArrow: '<i class="tabler-chevron-left v-icon" style="font-size: 20px; height: 20px; width: 20px;"></i>',
  nextArrow: '<i class="tabler-chevron-right v-icon" style="font-size: 20px; height: 20px; width: 20px;"></i>',
}

const onClear = (el: MouseEvent) => {
  el.stopPropagation()

  nextTick(() => {
    emit('update:modelValue', '')

    emit('click:clear', el)
  })
}

const vuetifyTheme = useTheme()

const vuetifyThemesName = Object.keys(vuetifyTheme.themes.value)

const updateThemeClassInCalendar = () => {

  if (!refFlatPicker.value.fp.calendarContainer)
    return

  vuetifyThemesName.forEach(t => {
    refFlatPicker.value.fp.calendarContainer.classList.remove(`v-theme--${t}`)
  })
  refFlatPicker.value.fp.calendarContainer.classList.add(`v-theme--${vuetifyTheme.global.name.value}`)
}

watch(() => configStore.theme, updateThemeClassInCalendar)

onMounted(() => {
  updateThemeClassInCalendar()
})

const emitModelValue = (val: string) => {
  emit('update:modelValue', val)
}

watch(() => props, () => {
  fieldProps.value = VField.filterProps(props)
  inputProps.value = VInput.filterProps(props)
},
{
  deep: true,
  immediate: true,
})

const elementId = computed (() => {
  const _elementIdToken = fieldProps.id || fieldProps.label || inputProps.value.id

  const _id = useId()

  return _elementIdToken ? `app-picker-field-${_elementIdToken}` : _id
})
</script>

<template>
  <div class="app-picker-field">

