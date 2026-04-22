<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/http/axios'

const authStore = useAuthStore()

const props = defineProps<{
  mode?: 'create' | 'edit'
  initialData?: Record<string, any>
}>()

const emit = defineEmits<{
  submit: [data: FormData]
  cancel: []
}>()

const dialog = ref(false)
const loading = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

const form = ref({
  title: '',
  description: '',
  category: '',
  start_date: '',
  start_time: '',
  end_date: '',
  end_time: '',
  venue_name: '',
  city: '',
  is_free: false,
  price: 0,
})

const categories = ref([
  { title: 'Concert', value: 'concert' },
  { title: 'Sport', value: 'sport' },
  { title: 'Business', value: 'business' },
  { title: 'Culture', value: 'culture' },
  { title: 'Technologie', value: 'technologie' },
  { title: 'Food', value: 'food' },
  { title: 'Festival', value: 'festival' },
])

const errors = ref<Record<string, string>>({})
const imagePreview = ref<string | null>(null)
const imageFile = ref<File | null>(null)

const isOrganizer = computed(() => authStore.role === 'organizer')
const isEditing = computed(() => props.mode === 'edit')

const open = () => {
  resetForm()
  dialog.value = true
}

const close = () => {
  dialog.value = false
  showSuccess.value = false
  resetForm()
}

const resetForm = () => {
  if (props.initialData) {
    form.value = {
      title: props.initialData.title || '',
      description: props.initialData.description || '',
      category: props.initialData.category?.value || props.initialData.category || '',
      start_date: props.initialData.start_date ? props.initialData.start_date.split('T')[0] : '',
      start_time: props.initialData.start_date ? props.initialData.start_date.split('T')[1]?.slice(0, 5) : '',
      end_date: props.initialData.end_date ? props.initialData.end_date.split('T')[0] : '',
      end_time: props.initialData.end_date ? props.initialData.end_date.split('T')[1]?.slice(0, 5) : '',
      venue_name: props.initialData.venue_name || '',
      city: props.initialData.city || '',
      is_free: props.initialData.is_free || false,
      price: props.initialData.price || 0,
    }
    imagePreview.value = props.initialData.cover_image || null
  } else {
    form.value = {
      title: '',
      description: '',
      category: '',
      start_date: '',
      start_time: '',
      end_date: '',
      end_time: '',
      venue_name: '',
      city: '',
      is_free: false,
      price: 0,
    }
  }
  imagePreview.value = null
  imageFile.value = null
  errors.value = {}
}

const handleImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  if (!file.type.startsWith('image/')) {
    errors.value.image = 'Veuillez sélectionner une image'
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    errors.value.image = "L'image ne doit pas dépasser 5MB"
    return
  }

  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
  delete errors.value.image
}

const removeImage = () => {
  imageFile.value = null
  imagePreview.value = null
}

const validate = () => {
  errors.value = {}

  if (!form.value.title.trim()) {
    errors.value.title = 'Le titre est requis'
  }

  if (!form.value.description.trim()) {
    errors.value.description = 'La description est requise'
  }

  if (!form.value.start_date) {
    errors.value.start_date = 'La date de début est requise'
  }

  if (!form.value.start_time) {
    errors.value.start_time = "L'heure de début est requise"
  }

  if (!form.value.city.trim()) {
    errors.value.city = 'La ville est requise'
  }

  if (!form.value.is_free && form.value.price <= 0) {
    errors.value.price = 'Le prix doit être supérieur à 0'
  }

  return Object.keys(errors.value).length === 0
}

const submit = async () => {
  if (!validate() || !isOrganizer.value) return

  loading.value = true
  errors.value.submit = ''

  try {
    const formData = new FormData()

    formData.append('title', form.value.title)
    formData.append('description', form.value.description)
    formData.append('category', form.value.category)
    formData.append('start_date', `${form.value.start_date}T${form.value.start_time}:00`)
    
    const endDate = form.value.end_date || form.value.start_date
    const endTime = form.value.end_time || form.value.start_time
    formData.append('end_date', `${endDate}T${endTime}:00`)
    
    formData.append('venue_name', form.value.venue_name)
    formData.append('city', form.value.city)
    formData.append('is_free', String(form.value.is_free))
    
    const price = form.value.is_free ? '0' : String(form.value.price || 0)
    formData.append('ticket_price', price)
    formData.append('ticket_quantity', '100')

    if (imageFile.value) {
      formData.append('cover_image', imageFile.value)
    }

    console.log('[EventForm] Submitting event with payload:', {
      title: form.value.title,
      description: form.value.description,
      category: form.value.category,
      start_date: form.value.start_date,
      start_time: form.value.start_time,
      city: form.value.city,
      is_free: form.value.is_free,
      ticket_price: price,
      has_image: !!imageFile.value,
    })

    const url = props.initialData?.id 
      ? `/events/${props.initialData.id}/` 
      : '/events/'

    const { data, error: axiosError, response } = props.initialData?.id 
      ? await apiClient.put(url, formData).then(r => [r, null, null]).catch(e => [null, e, e?.response])
      : await apiClient.post(url, formData).then(r => [r, null, null]).catch(e => [null, e, e?.response])

    if (axiosError) {
      console.error('[EventForm] Backend error response:', response?.data)
      console.error('[EventForm] Full error:', axiosError)
      
      const backendErrors = response?.data
      if (backendErrors) {
        const errorMessages = Object.entries(backendErrors)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' | ')
        errors.value.submit = errorMessages || "Une erreur est survenue, veuillez réessayer."
      } else {
        errors.value.submit = "Une erreur est survenue, veuillez réessayer."
      }
      return
    }
    
    console.log('[EventForm] Event created successfully:', data)
    
    successMessage.value = isEditing.value
      ? 'Les modifications ont été enregistrées avec succès.'
      : "Votre événement a été soumis avec succès et est en attente de validation par l'administrateur."
    
    showSuccess.value = true
    
    emit('submit', data)

    setTimeout(() => {
      close()
    }, 2500)
  }
  catch (error: any) {
    console.error('[EventForm] Unexpected error:', error)
    errors.value.submit = "Une erreur est survenue, veuillez réessayer."
  }
  finally {
    loading.value = false
  }
}

defineExpose({ open, close })
</script>

<template>
  <VDialog
    v-model="dialog"
    max-width="650"
    persistent
  >
    <VCard class="event-form-card">
      <VCardTitle class="d-flex align-center justify-space-between pa-5 pa-md-6">
        <div class="d-flex align-center gap-3">
          <VAvatar :color="isEditing ? 'info' : 'primary'" size="42">
            <VIcon :icon="isEditing ? 'tabler-edit' : 'tabler-plus'" />
          </VAvatar>
          <div>
            <span class="text-h5">{{ isEditing ? 'Modifier' : 'Créer' }} un événement</span>
            <p class="text-caption text-medium-emphasis mb-0">
              {{ isEditing ? 'Mettez à jour les détails' : 'Remplissez les détails de votre événement' }}
            </p>
          </div>
        </div>
        <IconBtn @click="close">
          <VIcon icon="tabler-x" />
        </IconBtn>
      </VCardTitle>

      <VDivider />

      <VCardText class="pa-5 pa-md-6">
        <VAlert
          v-if="showSuccess"
          type="success"
          variant="tonal"
          class="mb-4"
        >
          <div class="d-flex align-center gap-2">
            <VIcon icon="tabler-check" />
            <span>{{ successMessage }}</span>
          </div>
        </VAlert>

        <VAlert
          v-if="!isOrganizer"
          type="warning"
          variant="tonal"
          class="mb-4"
        >
          <div class="d-flex align-center gap-2">
            <VIcon icon="tabler-alert-triangle" />
            <span>Seuls les organisateur peuvent créer des événements</span>
          </div>
        </VAlert>

        <VForm @submit.prevent="submit">
          <VRow>
            <VCol cols="12">
              <VTextField
                v-model="form.title"
                label="Titre de l'événement"
                placeholder="Ex: Concert Jazz Night"
                :error="!!errors.title"
                :error-messages="errors.title"
                :disabled="!isOrganizer"
                required
              />
            </VCol>

            <VCol cols="12">
              <VTextarea
                v-model="form.description"
                label="Description"
                placeholder="Décrivez votre événement en détail..."
                rows="4"
                :error="!!errors.description"
                :error-messages="errors.description"
                :disabled="!isOrganizer"
                required
              />
            </VCol>

            <VCol cols="12" md="6">
              <VSelect
                v-model="form.category"
                label="Catégorie"
                :items="categories"
                :disabled="!isOrganizer"
                placeholder="Sélectionnez une catégorie"
              />
            </VCol>

            <VCol cols="12" md="6">
              <div class="image-upload-container">
                <label class="image-upload-label">
                  <input
                    type="file"
                    accept="image/*"
                    class="image-input"
                    :disabled="!isOrganizer"
                    @change="handleImageSelect"
                  >
                  <div v-if="imagePreview" class="image-preview-wrapper">
                    <img
                      :src="imagePreview"
                      alt="Preview"
                      class="image-preview"
                    >
                    <button
                      v-if="isOrganizer"
                      type="button"
                      class="remove-image-btn"
                      @click.stop="removeImage"
                    >
                      <VIcon icon="tabler-x" size="16" />
                    </button>
                  </div>
                  <div v-else class="image-upload-placeholder">
                    <VIcon icon="tabler-cloud-upload" size="32" />
                    <span>Photo de couverture</span>
                    <span class="image-hint">JPG, PNG - Max 5MB</span>
                  </div>
                </label>
                <p v-if="errors.image" class="text-error text-caption mt-1">
                  {{ errors.image }}
                </p>
              </div>
            </VCol>

            <VCol cols="12" md="6">
              <VTextField
                v-model="form.start_date"
                label="Date de début"
                type="date"
                :error="!!errors.start_date"
                :error-messages="errors.start_date"
                :disabled="!isOrganizer"
                required
              />
            </VCol>

            <VCol cols="12" md="6">
              <VTextField
                v-model="form.start_time"
                label="Heure de début"
                type="time"
                :error="!!errors.start_time"
                :error-messages="errors.start_time"
                :disabled="!isOrganizer"
                required
              />
            </VCol>

            <VCol cols="12" md="6">
              <VTextField
                v-model="form.end_date"
                label="Date de fin"
                type="date"
                :disabled="!isOrganizer"
              />
            </VCol>

            <VCol cols="12" md="6">
              <VTextField
                v-model="form.end_time"
                label="Heure de fin"
                type="time"
                :disabled="!isOrganizer"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="form.venue_name"
                label="Lieu/Venue"
                placeholder="Ex: Théâtre municipal de Tunis"
                :disabled="!isOrganizer"
              />
            </VCol>

            <VCol cols="12" md="6">
              <VTextField
                v-model="form.city"
                label="Ville"
                placeholder="Ex: Tunis"
                :error="!!errors.city"
                :error-messages="errors.city"
                :disabled="!isOrganizer"
                required
              />
            </VCol>

            <VCol cols="12" md="6">
              <VSwitch
                v-model="form.is_free"
                label="Événement gratuit"
                color="primary"
                hide-details
                :disabled="!isOrganizer"
              />
              <VTextField
                v-if="!form.is_free"
                v-model.number="form.price"
                label="Prix du billet"
                type="number"
                min="0"
                prefix="DT"
                class="mt-3"
                :error="!!errors.price"
                :error-messages="errors.price"
                :disabled="!isOrganizer"
              />
            </VCol>

            <VCol v-if="errors.submit" cols="12">
              <VAlert type="error" variant="tonal">
                {{ errors.submit }}
              </VAlert>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="pa-5 pa-md-6">
        <VSpacer />
        <VBtn
          variant="text"
          @click="close"
        >
          {{ showSuccess ? 'Fermer' : 'Annuler' }}
        </VBtn>
        <VBtn
          v-if="isOrganizer"
          color="primary"
          :loading="loading"
          :disabled="showSuccess"
          @click="submit"
        >
          <VIcon icon="tabler-check" class="mr-2" />
          {{ isEditing ? 'Enregistrer' : 'Créer l\'événement' }}
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.event-form-card {
  border-radius: 20px;
  overflow: hidden;
}

.image-upload-container {
  height: 100%;
}

.image-upload-label {
  display: block;
  cursor: pointer;
  height: 100%;
}

.image-input {
  display: none;
}

.image-upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 140px;
  border: 2px dashed rgba(var(--v-border-color), 0.5);
  border-radius: 12px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  color: rgba(var(--v-theme-on-surface), 0.6);
  transition: all 0.2s ease;
}

.image-upload-placeholder:hover {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.05);
}

.image-upload-placeholder span {
  font-size: 0.875rem;
}

.image-hint {
  font-size: 0.75rem !important;
  opacity: 0.7;
}

.image-preview-wrapper {
  position: relative;
  height: 140px;
  border-radius: 12px;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.remove-image-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}
</style>