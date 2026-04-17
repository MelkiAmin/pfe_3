<script setup lang="ts">
import laptopGirl from '@images/illustrations/laptop-girl.png'

const props = defineProps<{
  isDialogVisible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:isDialogVisible', val: boolean): void
  (e: 'updatedData', val: unknown): void
}>()

const currentStep = ref(0)

const createApp = [
  {
    icon: 'tabler-file-text',
    title: 'DETAILS',
    subtitle: 'Enter Details',
  },
  {
    icon: 'tabler-id',
    title: 'FRAMEWORKS',
    subtitle: 'Select Framework',
  },
  {
    icon: 'tabler-database',
    title: 'DATABASE',
    subtitle: 'Select Database',
  },
  {
    icon: 'tabler-credit-card',
    title: 'BILLING',
    subtitle: 'Payment Details',
  },
  {
    icon: 'tabler-check',
    title: 'SUBMIT',
    subtitle: 'Submit',
  },
]

const categories = [
  {
    icon: 'tabler-file-text',
    color: 'info',
    title: 'CRM Application',
    subtitle: 'Scales with any business',
    slug: 'crm-application',
  },
  {
    icon: 'tabler-shopping-cart',
    color: 'success',
    title: 'Ecommerce Platforms',
    subtitle: 'Grow Your Business With App',
    slug: 'ecommerce-application',
  },
  {
    icon: 'tabler-device-laptop',
    color: 'error',
    title: 'Online Learning platform',
    subtitle: 'Start learning today',
    slug: 'online-learning-application',
  },
]

const frameworks = [
  {
    icon: 'tabler-brand-react-native',
    color: 'info',
    title: 'React Native',
    subtitle: 'Create truly native apps',
    slug: 'react-framework',
  },
  {
    icon: 'tabler-brand-angular',
    color: 'error',
    title: 'Angular',
    subtitle: 'Most suited for your application',
    slug: 'angular-framework',
  },
  {
    icon: 'tabler-brand-vue',
    color: 'success',
    title: 'Vue',
    subtitle: 'JS web frameworks',
    slug: 'js-framework',
  },
  {
    icon: 'tabler-brand-html5',
    color: 'warning',
    title: 'HTML',
    subtitle: 'Progressive Framework',
    slug: 'html-framework',
  },
]

const databases = [
  {
    icon: 'tabler-brand-firebase',
    color: 'error',
    title: 'Firebase',
    subtitle: 'Cloud Firestore',
    slug: 'firebase-database',
  },
  {
    icon: 'tabler-brand-amazon',
    color: 'warning',
    title: 'AWS',
    subtitle: 'Amazon Fast NoSQL Database',
    slug: 'aws-database',
  },
  {
    icon: 'tabler-database',
    color: 'info',
    title: 'MySQL',
    subtitle: 'Basic MySQL database',
    slug: 'mysql-database',
  },
]

const createAppData = ref({
  category: 'crm-application',
  framework: 'js-framework',
  database: 'firebase-database',
  cardNumber: null,
  cardName: '',
  cardExpiry: '',
  cardCvv: '',
  isSave: true,
})

const dialogVisibleUpdate = (val: boolean) => {
  emit('update:isDialogVisible', val)
  currentStep.value = 0
}

watch(() => props, () => {
  if (!props.isDialogVisible)
    currentStep.value = 0
})

const onSubmit = () => {

  alert('submitted...!!')
  emit('updatedData', createAppData.value)
}
</script>

<template>
  <VDialog
    :model-value="props.isDialogVisible"
    max-width="900"
    min-height="590"
    @update:model-value="dialogVisibleUpdate"
  >

