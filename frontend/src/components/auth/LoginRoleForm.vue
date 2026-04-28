<script setup lang="ts">
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
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

const demoAccounts: { title: string; email: string; password: string }[] = [
  { title: 'Admin', email: 'admin@planova.com', password: 'admin123' },
  { title: 'Organisateur', email: 'organisateur@planova.com', password: 'org123' },
  { title: 'Utilisateur', email: 'user@planova.com', password: 'user123' },
]

const fillAccount = (account: { title: string; email: string; password: string }) => {
  form.email = account.email
  form.password = account.password
}

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
    console.error('[Login] Error response:', error.response?.data)
    const backendDetail = error.response?.data?.detail
    const backendStatus = error.response?.data?.status
    if (backendDetail) {
      formError.value = backendDetail
    } else if (backendStatus) {
      formError.value = error.response?.data?.message || authStore.error || 'Erreur de connexion.'
    } else {
      formError.value = error?.message || authStore.error || 'Erreur de connexion.'
    }
  }
}

const showForgotPassword = ref(false)
const resetEmail = ref('')
const resetLoading = ref(false)
const resetSuccess = ref(false)
const resetError = ref('')

const handleForgotPassword = async () => {
  if (!resetEmail.value) {
    resetError.value = 'Veuillez entrer votre adresse email.'
    return
  }

  resetLoading.value = true
  resetError.value = ''
  try {
    await authStore.requestPasswordReset(resetEmail.value)
    resetSuccess.value = true
  }
  catch (error: any) {
    console.error('[ForgotPassword] Error response:', error.response?.data)
    const backendDetail = error.response?.data?.detail
    resetError.value = backendDetail || 'Échec de l\'envoi de l\'email de réinitialisation. Veuillez réessayer.'
  }
  finally {
    resetLoading.value = false
  }
}
</script>

<template>
  <VForm @submit.prevent="onSubmit">
    <div class="soft-grid auth-form-grid">
      <VAlert
        v-if="formError"
        type="error"
        variant="tonal"
      >
        {{ formError }}
      </VAlert>

      <AppTextField
        v-model="form.email"
        :label="$t('auth.email')"
        type="email"
        autocomplete="email"
        prepend-inner-icon="tabler-mail"
        required
      />

      <AppTextField
        v-model="form.password"
        :label="$t('auth.password')"
        :type="isPasswordVisible ? 'text' : 'password'"
        autocomplete="current-password"
        prepend-inner-icon="tabler-lock"
        :append-inner-icon="isPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
        required
        @click:append-inner="isPasswordVisible = !isPasswordVisible"
      />

      <div class="d-flex align-center justify-space-between flex-wrap gap-3">
        <VCheckbox
          v-model="form.rememberMe"
          :label="$t('auth.remember_me')"
          hide-details
        />
        <a
          href="#"
          class="text-primary text-body-2 text-decoration-none"
          @click.prevent="showForgotPassword = true"
        >
          Forgot password?
        </a>
      </div>

      <VBtn
        block
        size="large"
        type="submit"
        :loading="authStore.loading"
        :disabled="authStore.loading"
      >
        Se connecter
      </VBtn>

      <div class="text-center text-body-2">
        Vous n'avez pas de compte ?
        <RouterLink
          to="/register"
          class="text-primary text-decoration-none font-weight-bold"
        >
          S'inscrire
        </RouterLink>
      </div>

      <div class="demo-box">
        <div class="demo-box__header">
          <span>Comptes de démonstration</span>
          <span class="text-medium-emphasis">Cliquez pour remplir</span>
        </div>

        <button
          v-for="account in demoAccounts"
          :key="account.email"
          type="button"
          class="demo-account"
          @click="fillAccount(account)"
        >
          <div>
            <div class="font-weight-bold">
              {{ account.title }}
            </div>
            <div class="text-medium-emphasis text-body-2">
              {{ account.email }}
            </div>
          </div>
          <span class="demo-password">{{ account.password }}</span>
        </button>
      </div>
    </div>
  </VForm>

  <!-- Forgot Password Dialog -->
  <VDialog v-model="showForgotPassword" max-width="450">
    <VCard>
      <VCardItem class="text-center pa-6">
        <VAvatar color="primary" size="64" class="mb-4">
          <VIcon icon="tabler-key" size="32" />
        </VAvatar>
        <VCardTitle class="text-h5">Reset password</VCardTitle>
        <VCardText class="text-medium-emphasis">
          Enter your email address and we'll send you a code to reset your password.
        </VCardText>
      </VCardItem>

      <VCardText class="pa-6 pt-0">
        <VAlert
          v-if="resetError"
          type="error"
          variant="tonal"
          class="mb-4"
        >
          {{ resetError }}
        </VAlert>

        <VAlert
          v-if="resetSuccess"
          type="success"
          variant="tonal"
          class="mb-4"
        >
          Password reset code sent to your email!
        </VAlert>

        <AppTextField
          v-if="!resetSuccess"
          v-model="resetEmail"
          label="Adresse email"
          type="email"
          prepend-inner-icon="tabler-mail"
        />
      </VCardText>

      <VCardActions class="justify-center pb-6">
        <VBtn
          variant="text"
          @click="showForgotPassword = false"
        >
          Annuler
        </VBtn>
        <VBtn
          v-if="!resetSuccess"
          color="primary"
          :loading="resetLoading"
          @click="handleForgotPassword"
        >
          Envoyer le code
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.auth-form-grid {
  gap: 1rem;
}

.demo-box {
  padding: 1rem;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 20px;
  background: rgba(var(--v-theme-primary), 0.04);
}

.demo-box__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
  font-size: 0.9rem;
  font-weight: 700;
}

.demo-account {
  display: flex;
  align-items: center;
  justify-content: space-between;
  inline-size: 100%;
  margin-top: 0.7rem;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 16px;
  background: rgba(var(--v-theme-surface), 0.94);
  text-align: left;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.demo-account:hover {
  transform: translateY(-2px);
  border-color: rgba(var(--v-theme-primary), 0.2);
}

.demo-password {
  font-size: 0.84rem;
  font-weight: 700;
  color: rgb(var(--v-theme-primary));
}
</style>
