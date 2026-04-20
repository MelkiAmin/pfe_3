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

const demoAccounts = [
  { title: 'Admin', email: 'admin@planova.com', password: 'admin123' },
  { title: 'Organisateur', email: 'organisateur@planova.com', password: 'org123' },
  { title: 'Utilisateur', email: 'user@planova.com', password: 'user123' },
]

const fillAccount = (account: typeof demoAccounts[number]) => {
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
    formError.value = error?.message || authStore.error || 'Erreur de connexion.'
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
        <RouterLink
          to="/register"
          class="text-primary text-body-2 text-decoration-none"
        >
          Create account
        </RouterLink>
      </div>

      <VBtn
        block
        size="large"
        type="submit"
        :loading="authStore.loading"
      >
        Se connecter
      </VBtn>

      <div class="demo-box">
        <div class="demo-box__header">
          <span>Comptes par défaut</span>
          <span class="text-medium-emphasis">Cliquer pour préremplir</span>
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
