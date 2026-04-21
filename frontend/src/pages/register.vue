<script setup lang="ts">
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import { useAuth } from '@/composables/useAuth'

definePage({
  meta: {
    layout: 'blank',
    public: true,
  },
})

type RoleOption = {
  title: string
  subtitle: string
  value: 'attendee' | 'organizer'
  icon: string
  color: string
}

const roles: RoleOption[] = [
  {
    title: 'Participant',
    subtitle: 'Reserve tickets and attend events',
    value: 'attendee',
    icon: 'tabler-ticket',
    color: 'primary',
  },
  {
    title: 'Organisateur',
    subtitle: 'Create and manage events',
    value: 'organizer',
    icon: 'tabler-calendar-plus',
    color: 'info',
  },
]

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  role: 'attendee' as 'attendee' | 'organizer',
})

const isPasswordVisible = ref(false)
const isConfirmPasswordVisible = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showOtpDialog = ref(false)
const otpCode = ref('')
const router = useRouter()
const { register, verifyOtp, extractErrorMessage } = useAuth()

const otpEmail = ref('')

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
  successMessage.value = ''
  if (!validateForm())
    return

  isLoading.value = true
  try {
    const response = await register({
      email: form.value.email,
      first_name: form.value.firstName,
      last_name: form.value.lastName,
      phone: form.value.phone,
      password: form.value.password,
      password_confirm: form.value.confirmPassword,
      role: form.value.role,
    })

    // Check if account is pending (needs admin approval)
    if (response?.status === 'pending') {
      successMessage.value = 'Votre compte est créé avec succès. Vous recevrez un email après validation par un administrateur.'
      setTimeout(() => {
        router.replace('/login')
      }, 3000)
    } else {
      // Show OTP dialog only if account is approved (auto-approved path)
      otpEmail.value = form.value.email
      showOtpDialog.value = true
    }
  }
  catch (error: unknown) {
    errorMessage.value = extractErrorMessage(error)
  }
  finally {
    isLoading.value = false
  }
}

const handleVerifyOtp = async () => {
  if (!otpCode.value || otpCode.value.length !== 6) {
    errorMessage.value = 'Please enter a valid 6-digit code.'
    return
  }

  isLoading.value = true
  try {
    await verifyOtp(otpEmail.value, otpCode.value)
    successMessage.value = 'Account verified! Redirecting to login...'
    setTimeout(() => {
      router.replace('/login')
    }, 2000)
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
          Create your account
        </h1>
        <p class="text-medium-emphasis mb-6">
          Choose your role and start your journey with Planova
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

            <VAlert
              v-if="successMessage"
              type="success"
              variant="tonal"
            >
              {{ successMessage }}
            </VAlert>

            <!-- Role Selection -->
            <div class="role-selection mb-4">
              <div class="text-subtitle-2 mb-2">I want to:</div>
              <VRadioGroup v-model="form.role" inline>
                <div class="role-options">
                  <div
                    v-for="role in roles"
                    :key="role.value"
                    class="role-card"
                    :class="{ 'role-card--selected': form.role === role.value }"
                    @click="form.role = role.value"
                  >
                    <VIcon
                      :icon="role.icon"
                      size="28"
                      :color="role.color"
                      class="mb-2"
                    />
                    <div class="text-subtitle-1 font-weight-bold">{{ role.title }}</div>
                    <div class="text-body-2 text-medium-emphasis">{{ role.subtitle }}</div>
                    <VIcon
                      v-if="form.role === role.value"
                      icon="tabler-check-circle"
                      color="success"
                      class="role-check"
                    />
                  </div>
                </div>
              </VRadioGroup>
            </div>

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
                  label="Phone (optional)"
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
              Create my account
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

    <!-- OTP Verification Dialog -->
    <VDialog v-model="showOtpDialog" max-width="450" persistent>
      <VCard>
        <VCardItem class="text-center pa-6">
          <VAvatar color="primary" size="64" class="mb-4">
            <VIcon icon="tabler-mail" size="32" />
          </VAvatar>
          <VCardTitle class="text-h5">Verify your email</VCardTitle>
          <VCardText class="text-medium-emphasis">
            We've sent a 6-digit code to your email.
            <br>Enter it below to activate your account.
          </VCardText>
        </VCardItem>

        <VCardText class="pa-6 pt-0">
          <AppTextField
            v-model="otpCode"
            label="Verification code"
            placeholder="000000"
            maxlength="6"
            class="otp-input text-center"
          />
        </VCardText>

        <VCardActions class="justify-center pb-6">
          <VBtn
            color="primary"
            size="large"
            :loading="isLoading"
            @click="handleVerifyOtp"
          >
            Verify account
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
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

.role-selection {
  margin-bottom: 1.5rem;
}

.role-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}

.role-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  border: 2px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.role-card:hover {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.04);
}

.role-card--selected {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.08);
}

.role-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.otp-input :deep(input) {
  text-align: center;
  font-size: 1.5rem;
  letter-spacing: 0.5rem;
}
</style>