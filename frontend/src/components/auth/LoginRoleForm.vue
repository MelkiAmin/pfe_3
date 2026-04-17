<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
  rememberMe: true,
})

const isPasswordVisible = ref(false)
const formError = ref('')

const onSubmit = async () => {
  formError.value = ''
  try {
    const user = await authStore.login({
      email: form.email,
      password: form.password,
      rememberMe: form.rememberMe,
    })

    const redirect = typeof route.query.redirect === 'string'
      ? route.query.redirect
      : authStore.dashboardRouteByRole(user.role)

    await router.replace(redirect)
  }
  catch (error: any) {
    formError.value = error?.message || authStore.error || 'Erreur de connexion.'
  }
}
</script>

<template>
  <VForm @submit.prevent="onSubmit">
    <VRow>
      <VCol
        v-if="formError"
        cols="12"
      >
        <VAlert
          type="error"
          variant="tonal"
        >
          {{ formError }}
        </VAlert>
      </VCol>

      <VCol cols="12">
        <AppTextField
          v-model="form.email"
          :label="$t('auth.email')"
          type="email"
          autocomplete="email"
          required
        />
      </VCol>

      <VCol cols="12">
        <AppTextField
          v-model="form.password"
          :label="$t('auth.password')"
          :type="isPasswordVisible ? 'text' : 'password'"
          autocomplete="current-password"
          :append-inner-icon="isPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
          required
          @click:append-inner="isPasswordVisible = !isPasswordVisible"
        />
      </VCol>

      <VCol cols="12">
        <VCheckbox
          v-model="form.rememberMe"
          :label="$t('auth.remember_me')"
        />
      </VCol>

      <VCol cols="12">
        <VBtn
          block
          type="submit"
          :loading="authStore.loading"
        >
          {{ $t('auth.sign_in') }}
        </VBtn>
      </VCol>
    </VRow>
  </VForm>
</template>
