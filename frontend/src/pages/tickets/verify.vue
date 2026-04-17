<script setup lang="ts">
definePage({ meta: { public: true } })

const code = ref('')
const loading = ref(false)
const result = ref<{ status: 'valid' | 'invalid' | 'used'; message: string } | null>(null)

const verify = async () => {
  loading.value = true
  result.value = {
    status: 'invalid',
    message: 'Ticket verification endpoint is not available yet. Use the ticket check-in API when a scannable ticket ID flow is wired up.',
  }
  loading.value = false
}
</script>

<template>
  <VCard title="Vérifier un billet">
    <VCardText>
      <AppTextField
        v-model="code"
        label="Code QR"
        placeholder="Saisir ou scanner le code"
      />
      <VBtn
        class="mt-3"
        color="primary"
        :loading="loading"
        @click="verify"
      >
        Vérifier
      </VBtn>

      <VAlert
        v-if="result"
        class="mt-4"
        :type="result.status === 'valid' ? 'success' : result.status === 'used' ? 'warning' : 'error'"
        variant="tonal"
      >
        {{ result.message }}
      </VAlert>
    </VCardText>
  </VCard>
</template>
