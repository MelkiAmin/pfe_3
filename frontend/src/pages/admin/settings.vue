<script setup lang="ts">
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'

definePage({
  meta: {
    roles: ['admin'],
  },
})

const form = reactive({
  commission: 5,
  paymentTimeout: 30,
  eventVerification: true,
})
const saving = ref(false)
const message = ref('')

const save = async () => {
  saving.value = true
  message.value = 'System settings API is not available in the backend yet.'
  saving.value = false
}
</script>

<template>
  <VCard title="Configuration système">
    <VCardText>
      <VAlert
        v-if="message"
        type="info"
        variant="tonal"
        class="mb-4"
      >
        {{ message }}
      </VAlert>
      <VRow>
        <VCol
          cols="12"
          md="4"
        >
          <AppTextField
            v-model.number="form.commission"
            type="number"
            label="Commission globale (%)"
          />
        </VCol>
        <VCol
          cols="12"
          md="4"
        >
          <AppTextField
            v-model.number="form.paymentTimeout"
            type="number"
            label="Timeout paiement (min)"
          />
        </VCol>
        <VCol
          cols="12"
          md="4"
          class="d-flex align-end"
        >
          <VCheckbox
            v-model="form.eventVerification"
            label="Vérification événement obligatoire"
          />
        </VCol>
      </VRow>
      <VBtn
        color="primary"
        :loading="saving"
        @click="save"
      >
        Enregistrer
      </VBtn>
    </VCardText>
  </VCard>
</template>
