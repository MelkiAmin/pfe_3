<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiClient } from '@/services/http/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const kycStatus = ref<any>(null)
const kycLoading = ref(false)
const kycForm = ref({ doc_type: 'national_id' })
const kycMsg = ref('')
const kycError = ref('')
const verifyCodeSent = ref(false)
const verifyCode = ref('')
const verifyMsg = ref('')
const verifyError = ref('')
const profileSaving = ref(false)
const profileForm = ref({ first_name: '', last_name: '', phone: '' })
const profileMsg = ref('')

// Load KYC status
const loadKYC = async () => {
  kycLoading.value = true
  try {
    const { data } = await apiClient.get('/kyc/status/')
    kycStatus.value = data
  } catch {}
  finally { kycLoading.value = false }
}

// Email verification
const sendVerificationCode = async () => {
  try {
    await apiClient.post('/auth/email/request-verification/')
    verifyCodeSent.value = true
    verifyMsg.value = 'Code envoyé à votre email.'
  } catch (e: any) {
    verifyError.value = e?.response?.data?.detail || 'Erreur lors de l\'envoi.'
  }
}

const confirmCode = async () => {
  try {
    await apiClient.post('/auth/email/confirm-verification/', { code: verifyCode.value })
    verifyMsg.value = 'Email vérifié avec succès ✓'
    verifyError.value = ''
    verifyCodeSent.value = false
    authStore.bootstrap()
  } catch (e: any) {
    verifyError.value = 'Code invalide ou expiré.'
  }
}

// Profile update
const saveProfile = async () => {
  profileSaving.value = true
  try {
    await apiClient.patch('/auth/profile/', profileForm.value)
    profileMsg.value = 'Profil mis à jour ✓'
    authStore.bootstrap()
  } catch {}
  finally { profileSaving.value = false }
}

const kycStatusColor = (s: string) => ({
  pending: 'warning', approved: 'success', rejected: 'error'
}[s] || 'default')

onMounted(() => {
  loadKYC()
  if (user.value) {
    profileForm.value.first_name = user.value.first_name || ''
    profileForm.value.last_name  = user.value.last_name  || ''
  }
})
</script>

<template>
  <VRow>
    <!-- Profile Card -->
    <VCol cols="12" md="6">
      <VCard title="Mon Profil">
        <VCardText>
          <VForm @submit.prevent="saveProfile">
            <VTextField v-model="profileForm.first_name" label="Prénom" class="mb-3" />
            <VTextField v-model="profileForm.last_name"  label="Nom"    class="mb-3" />
            <VTextField v-model="profileForm.phone"      label="Téléphone" class="mb-3" />
            <VAlert v-if="profileMsg" type="success" variant="tonal" class="mb-3">{{ profileMsg }}</VAlert>
            <VBtn type="submit" color="primary" :loading="profileSaving">Enregistrer</VBtn>
          </VForm>

          <!-- Email verification -->
          <VDivider class="my-4" />
          <h6 class="text-h6 mb-2">Vérification Email</h6>
          <VChip v-if="user?.is_email_verified" color="success" size="small" class="mb-3">
            <VIcon start icon="ri-check-line" /> Email vérifié
          </VChip>
          <template v-else>
            <VAlert type="warning" variant="tonal" class="mb-3">Email non vérifié</VAlert>
            <div v-if="!verifyCodeSent">
              <VBtn size="small" variant="outlined" @click="sendVerificationCode">Envoyer un code de vérification</VBtn>
            </div>
            <div v-else class="d-flex gap-2 align-center">
              <VTextField v-model="verifyCode" label="Code reçu par email" density="compact" />
              <VBtn size="small" color="success" @click="confirmCode">Confirmer</VBtn>
            </div>
            <VAlert v-if="verifyMsg"   type="success" variant="tonal" class="mt-2" size="small">{{ verifyMsg }}</VAlert>
            <VAlert v-if="verifyError" type="error"   variant="tonal" class="mt-2" size="small">{{ verifyError }}</VAlert>
          </template>
        </VCardText>
      </VCard>
    </VCol>

    <!-- KYC Card -->
    <VCol cols="12" md="6">
      <VCard title="Vérification KYC" subtitle="Vérifiez votre identité pour débloquer les retraits">
        <VCardText>
          <VSkeletonLoader v-if="kycLoading" type="paragraph" />
          <template v-else-if="kycStatus">
            <div class="d-flex align-center gap-3 mb-4">
              <VChip :color="kycStatusColor(kycStatus.status)" size="small">
                {{ kycStatus.status }}
              </VChip>
              <span v-if="kycStatus.status === 'approved'" class="text-success text-sm">
                Identité vérifiée ✓
              </span>
              <span v-else-if="kycStatus.status === 'rejected'" class="text-error text-sm">
                {{ kycStatus.rejection_reason || 'Rejeté' }}
              </span>
            </div>

            <template v-if="kycStatus.status !== 'approved'">
              <VSelect
                v-model="kycForm.doc_type"
                label="Type de document"
                :items="[
                  { title: 'Carte d\'identité nationale', value: 'national_id' },
                  { title: 'Passeport', value: 'passport' },
                  { title: 'Permis de conduire', value: 'driver_license' },
                ]"
                class="mb-3"
              />
              <VAlert type="info" variant="tonal" class="mb-3">
                Soumettez vos documents d'identité pour vérification. Le processus prend 1–2 jours ouvrés.
              </VAlert>
              <VAlert v-if="kycMsg"   type="success" variant="tonal" class="mb-2">{{ kycMsg }}</VAlert>
              <VAlert v-if="kycError" type="error"   variant="tonal" class="mb-2">{{ kycError }}</VAlert>
              <VBtn color="primary" variant="outlined" prepend-icon="ri-upload-2-line"
                @click="kycMsg = 'Fonctionnalité de téléversement disponible avec le formulaire complet.'">
                Téléverser les documents
              </VBtn>
            </template>
          </template>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>
