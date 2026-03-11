import { createI18n } from 'vue-i18n'
import en from './locales/en'
import zh from './locales/zh'

const LOCALE_KEY = 'mirofish-locale'

export const getStoredLocale = () => {
  if (typeof window === 'undefined') {
    return 'zh'
  }

  try {
    const locale = window.localStorage.getItem(LOCALE_KEY)
    return locale === 'en' || locale === 'zh' ? locale : 'zh'
  } catch {
    return 'zh'
  }
}

export const setStoredLocale = (locale) => {
  if (typeof window === 'undefined') {
    return
  }

  try {
    window.localStorage.setItem(LOCALE_KEY, locale)
  } catch {
    // Ignore storage failures and keep the in-memory locale.
  }
}

export default createI18n({
  legacy: false,
  locale: getStoredLocale(),
  fallbackLocale: 'zh',
  messages: {
    en,
    zh,
  },
})
