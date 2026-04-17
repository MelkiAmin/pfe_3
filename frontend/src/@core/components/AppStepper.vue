<script setup lang="ts">
interface Item {
  title: string
  icon?: string | object
  size?: string
  subtitle?: string
}

type Direction = 'vertical' | 'horizontal'

interface Props {
  items: Item[]
  currentStep?: number
  direction?: Direction
  iconSize?: string | number
  isActiveStepValid?: boolean
  align?: 'start' | 'center' | 'end' | 'default'
}

interface Emit {
  (e: 'update:currentStep', value: number): void
}

const props = withDefaults(defineProps<Props>(), {
  currentStep: 0,
  direction: 'horizontal',
  iconSize: 60,
  isActiveStepValid: undefined,
  align: 'default',
})

const emit = defineEmits<Emit>()

const currentStep = ref(props.currentStep || 0)

const activeOrCompletedStepsClasses = computed(() => (index: number) => (
  index < currentStep.value
    ? 'stepper-steps-completed'
    : index === currentStep.value ? 'stepper-steps-active' : ''
))

const isHorizontalAndNotLastStep = computed(() => (index: number) => (
  props.direction === 'horizontal'
  && props.items.length - 1 !== index
))

const isValidationEnabled = computed(() => {
  return props.isActiveStepValid !== undefined
})

watchEffect(() => {

  if (
    props.currentStep !== undefined
    && props.currentStep < props.items.length
    && props.currentStep >= 0
  )
    currentStep.value = props.currentStep

  emit('update:currentStep', currentStep.value)
})
</script>

<template>
  <VSlideGroup
    v-model="currentStep"
    class="app-stepper"
    show-arrows
    :direction="props.direction"
    :class="`app-stepper-${props.align} ${props.items[0].icon ? 'app-stepper-icons' : ''}`"
  >
    <VSlideGroupItem
      v-for="(item, index) in props.items"
      :key="item.title"
      :value="index"
    >
      <div
        class="cursor-pointer app-stepper-step pa-1"
        :class="[
          (!props.isActiveStepValid && (isValidationEnabled)) && 'stepper-steps-invalid',
          activeOrCompletedStepsClasses(index),
        ]"
        @click="!isValidationEnabled && emit('update:currentStep', index)"
      >

