import type { App } from 'vue'
import { createI18n } from 'vue-i18n'
import ar from '@/locales/ar.json'
import en from '@/locales/en.json'
import fr from '@/locales/fr.json'

const supported = ['fr', 'en', 'ar']

const detectLocale = () => {
  const browserLang = navigator.language?.split('-')[0]?.toLowerCase()
  if (browserLang && supported.includes(browserLang))
    return browserLang
  return 'fr'
}

const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'fr',
  messages: { fr, en, ar },
})

export default function (app: App) {
  app.use(i18n)
}
