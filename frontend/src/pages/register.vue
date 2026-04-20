<script setup lang="ts">
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import { useAuth } from '@/composables/useAuth'

definePage({
  meta: {
    layout: 'blank',
    public: true,
  },
})

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const isPasswordVisible = ref(false)
const isConfirmPasswordVisible = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const router = useRouter()
const { register, extractErrorMessage } = useAuth()

const validateForm = () => {
  const firstName = form.value.firstName.trim()
  const lastName = form.value.lastName.trim()
  const email = form.value.email.trim()
  const password = form.value.password

  if (!firstName || !lastName) {
    errorMessage.value = 'First name and last name are required.'
    return false
  }

  if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
    errorMessage.value = 'Enter a valid email address.'
    return false
  }

  if (password.length < 8) {
    errorMessage.value = 'Password must be at least 8 characters long.'
    return false
  }

  if (password !== form.value.confirmPassword) {
    errorMessage.value = 'Passwords do not match.'
    return false
  }

  form.value.firstName = firstName
  form.value.lastName = lastName
  form.value.email = email

  return true
}

const handleRegister = async () => {
  errorMessage.value = ''
  if (!validateForm())
    return

  isLoading.value = true
  try {
    await register({
      email: form.value.email,
      first_name: form.value.firstName,
      last_name: form.value.lastName,
      phone: form.value.phone,
      password: form.value.password,
      password_confirm: form.value.confirmPassword,
    })

    await router.replace('/')
  }
  catch (error: unknown) {
    errorMessage.value = extractErrorMessage(error)
  }
  finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="register-screen">
    <VCard class="register-card section-card">
      <VCardText class="pa-8 pa-md-10">
        <p class="page-kicker">
          Join Planova
        </p>
        <h1 class="text-h3 mb-2">
          Create your ticketing account
        </h1>
        <p class="text-medium-emphasis mb-6">
          Register in a few seconds and start booking or managing events with a clean, modern experience.
        </p>

        <VForm @submit.prevent="handleRegister">
          <div class="soft-grid register-grid">
            <VAlert
              v-if="errorMessage"
              type="error"
              variant="tonal"
            >
              {{ errorMessage }}
            </VAlert>

            <VRow>
              <VCol cols="12" md="6">
                <AppTextField
                  v-model="form.firstName"
                  label="First name"
                  prepend-inner-icon="tabler-user"
                  placeholder="Amina"
                />
              </VCol>
              <VCol cols="12" md="6">
                <AppTextField
                  v-model="form.lastName"
                  label="Last name"
                  prepend-inner-icon="tabler-user-circle"
                  placeholder="Ben Ali"
                />
              </VCol>
              <VCol cols="12" md="6">
                <AppTextField
                  v-model="form.email"
                  label="Email"
                  type="email"
                  prepend-inner-icon="tabler-mail"
                  placeholder="you@planova.com"
                />
              </VCol>
              <VCol cols="12" md="6">
                <AppTextField
                  v-model="form.phone"
                  label="Phone"
                  prepend-inner-icon="tabler-phone"
                  placeholder="+216 00 000 000"
                />
              </VCol>
              <VCol cols="12" md="6">
                <AppTextField
                  v-model="form.password"
                  label="Password"
                  :type="isPasswordVisible ? 'text' : 'password'"
                  prepend-inner-icon="tabler-lock"
                  :append-inner-icon="isPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
                  @click:append-inner="isPasswordVisible = !isPasswordVisible"
                />
              </VCol>
              <VCol cols="12" md="6">
                <AppTextField
                  v-model="form.confirmPassword"
                  label="Confirm password"
                  :type="isConfirmPasswordVisible ? 'text' : 'password'"
                  prepend-inner-icon="tabler-shield-lock"
                  :append-inner-icon="isConfirmPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
                  @click:append-inner="isConfirmPasswordVisible = !isConfirmPasswordVisible"
                />
              </VCol>
            </VRow>

            <VBtn
              block
              size="large"
              type="submit"
              :loading="isLoading"
            >
              Créer mon compte
            </VBtn>

            <div class="text-center text-medium-emphasis">
              Already have an account?
              <RouterLink
                class="text-primary text-decoration-none ms-1"
                to="/login"
              >
                Sign in
              </RouterLink>
            </div>
          </div>
        </VForm>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.register-screen {
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at top left, rgba(var(--v-theme-primary), 0.14), transparent 20%),
    radial-gradient(circle at bottom right, rgba(var(--v-theme-info), 0.12), transparent 22%),
    rgb(var(--v-theme-background));
}

.register-card {
  inline-size: min(860px, 100%);
}

.register-grid {
  gap: 1rem;
}
</style>
