<script setup lang="ts">
import home from '@images/svg/home.svg'
import office from '@images/svg/office.svg'

interface BillingAddress {
  firstName: string | undefined
  lastName: string | undefined
  selectedCountry: string | null
  addressLine1: string
  addressLine2: string
  landmark: string
  contact: string
  country: string | null
  city: string
  state: string
  zipCode: number | null
}
interface Props {
  billingAddress?: BillingAddress
  isDialogVisible: boolean
}
interface Emit {
  (e: 'update:isDialogVisible', value: boolean): void
  (e: 'submit', value: BillingAddress): void
}

const props = withDefaults(defineProps<Props>(), {
  billingAddress: () => ({
    firstName: '',
    lastName: '',
    selectedCountry: null,
    addressLine1: '',
    addressLine2: '',
    landmark: '',
    contact: '',
    country: null,
    city: '',
    state: '',
    zipCode: null,
  }),
})

const emit = defineEmits<Emit>()

const billingAddress = ref<BillingAddress>(structuredClone(toRaw(props.billingAddress)))

const resetForm = () => {
  emit('update:isDialogVisible', false)
  billingAddress.value = structuredClone(toRaw(props.billingAddress))
}

const onFormSubmit = () => {
  emit('update:isDialogVisible', false)
  emit('submit', billingAddress.value)
}

const selectedAddress = ref('Home')

const addressTypes = [
  {
    icon: { icon: home, size: '28' },
    title: 'Home',
    desc: 'Delivery Time (9am - 9pm)',
    value: 'Home',
  },
  {
    icon: { icon: office, size: '28' },
    title: 'Office',
    desc: 'Delivery Time (9am - 5pm)',
    value: 'Office',
  },
]
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 900 "
    :model-value="props.isDialogVisible"
    @update:model-value="val => $emit('update:isDialogVisible', val)"
  >

