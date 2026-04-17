<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { useGenerateImageVariant } from '@core/composable/useGenerateImageVariant'
import authV2RegisterIllustrationBorderedDark from '@images/pages/auth-v2-register-illustration-bordered-dark.png'
import authV2RegisterIllustrationBorderedLight from '@images/pages/auth-v2-register-illustration-bordered-light.png'
import authV2RegisterIllustrationDark from '@images/pages/auth-v2-register-illustration-dark.png'
import authV2RegisterIllustrationLight from '@images/pages/auth-v2-register-illustration-light.png'
import authV2MaskDark from '@images/pages/misc-mask-dark.png'
import authV2MaskLight from '@images/pages/misc-mask-light.png'
import { VNodeRenderer } from '@layouts/components/VNodeRenderer'
import { themeConfig } from '@themeConfig'

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

const authThemeImg = useGenerateImageVariant(
  authV2RegisterIllustrationLight,
  authV2RegisterIllustrationDark,
  authV2RegisterIllustrationBorderedLight,
  authV2RegisterIllustrationBorderedDark,
  true)

const authThemeMask = useGenerateImageVariant(authV2MaskLight, authV2MaskDark)

const validateForm = () => {
  const firstName = form.value.firstName.trim()
  const lastName = form.value.lastName.trim()
  const email = form.value.email.trim()
  const password = form.value.password

  if (!firstName || !lastName) {
    errorMessage.value = 'First name and last name are required.'
    return false
  }

  if (!email) {
    errorMessage.value = 'Email is required.'
    return false
  }

  if (!/^\S+@\S+\.\S+$/.test(email)) {
    errorMessage.value = 'Enter a valid email address.'
    return false
  }

  if (password.length < 8) {
    errorMessage.value = 'Password must be at least 8 characters long.'
    return false
  }

  if (/^\d+$/.test(password)) {
    errorMessage.value = 'Password cannot be entirely numeric.'
    return false
  }

  if (password.toLowerCase().includes(firstName.toLowerCase()) || password.toLowerCase().includes(lastName.toLowerCase())) {
    errorMessage.value = 'Password is too similar to your name.'
    return false
  }

  if (['password', 'password123', '12345678', 'qwerty123'].includes(password.toLowerCase())) {
    errorMessage.value = 'Choose a less common password.'
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
  <a href="javascript:void(0)">
    <div class="auth-logo d-flex align-center gap-x-3">
      <VNodeRenderer :nodes="themeConfig.app.logo" />
      <h1 class="auth-title">
        {{ themeConfig.app.title }}
      </h1>
    </div>
  </a>

  <VRow
    no-gutters
    class="auth-wrapper bg-surface"
  >
    <VCol
      md="8"
      class="d-none d-md-flex"
    >
      <div class="position-relative bg-background w-100 me-0">
        <div
          class="d-flex align-center justify-center w-100 h-100"
          style="padding-inline: 6.25rem;"
        >
          <VImg
            max-width="613"
            :src="authThemeImg"
            class="auth-illustration mt-16 mb-2"
          />
        </div>

        <img
          class="auth-footer-mask flip-in-rtl"
          :src="authThemeMask"
          alt="auth-footer-mask"
          height="280"
          width="100"
        >
      </div>
    </VCol>

    <VCol
      cols="12"
      md="4"
      class="auth-card-v2 d-flex align-center justify-center"
    >
      <VCard
        flat
        :max-width="500"
        class="mt-12 mt-sm-0 pa-6"
      >
        <VCardText>
          <h4 class="text-h4 mb-1">
            Create your account
          </h4>
          <p class="mb-0">
            Register and start using {{ themeConfig.app.title }}
          </p>
        </VCardText>

        <VCardText>
          <VForm @submit.prevent="handleRegister">
            <VRow>
              <VCol
                v-if="errorMessage"
                cols="12"
              >
                <VAlert
                  type="error"
                  variant="tonal"
                >
                  {{ errorMessage }}
                </VAlert>
              </VCol>

              <VCol cols="12">
                <AppTextField
                  v-model="form.firstName"
                  label="First name"
                  placeholder="John"
                />
              </VCol>

              <VCol cols="12">
                <AppTextField
                  v-model="form.lastName"
                  label="Last name"
                  placeholder="Doe"
                />
              </VCol>

              <VCol cols="12">
                <AppTextField
                  v-model="form.email"
                  label="Email"
                  type="email"
                  placeholder="johndoe@email.com"
                />
              </VCol>

              <VCol cols="12">
                <AppTextField
                  v-model="form.phone"
                  label="Phone (optional)"
                  placeholder="+1 555 123 4567"
                />
              </VCol>

              <VCol cols="12">
                <AppTextField
                  v-model="form.password"
                  label="Password"
                  placeholder="············"
                  :type="isPasswordVisible ? 'text' : 'password'"
                  autocomplete="new-password"
                  :append-inner-icon="isPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
                  @click:append-inner="isPasswordVisible = !isPasswordVisible"
                />
              </VCol>

              <VCol cols="12">
                <AppTextField
                  v-model="form.confirmPassword"
                  label="Confirm password"
                  placeholder="············"
                  :type="isConfirmPasswordVisible ? 'text' : 'password'"
                  autocomplete="new-password"
                  :append-inner-icon="isConfirmPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
                  @click:append-inner="isConfirmPasswordVisible = !isConfirmPasswordVisible"
                />
              </VCol>

              <VCol cols="12">
                <VBtn
                  block
                  type="submit"
                  :loading="isLoading"
                >
                  Register
                </VBtn>
              </VCol>

              <VCol
                cols="12"
                class="text-body-1 text-center"
              >
                <span class="d-inline-block">
                  Already have an account?
                </span>
                <RouterLink
                  class="text-primary ms-1 d-inline-block text-body-1"
                  to="/login"
                >
                  Sign in
                </RouterLink>
              </VCol>
            </VRow>
          </VForm>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>

<style lang="scss">
@use "@core/scss/template/pages/page-auth";
</style>
