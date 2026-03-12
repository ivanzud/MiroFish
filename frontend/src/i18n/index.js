import { createI18n } from 'vue-i18n'
import en from './locales/en.js'
import zh from './locales/zh.js'

const LOCALE_KEY = 'mirofish-locale'
const DEFAULT_LOCALE = 'zh'

export const normalizeLocale = (locale) => {
  if (typeof locale !== 'string') {
    return null
  }

  const normalized = locale.trim().toLowerCase()
  if (normalized.startsWith('zh')) {
    return 'zh'
  }
  if (normalized.startsWith('en')) {
    return 'en'
  }
  return null
}

export const resolveBrowserLocale = (browserLocale) => normalizeLocale(browserLocale) || DEFAULT_LOCALE

export const getStoredLocale = () => {
  if (typeof window === 'undefined') {
    return DEFAULT_LOCALE
  }

  try {
    const locale = window.localStorage.getItem(LOCALE_KEY)
    const storedLocale = normalizeLocale(locale)
    if (storedLocale) {
      return storedLocale
    }

    return resolveBrowserLocale(window.navigator?.language)
  } catch {
    return resolveBrowserLocale(window.navigator?.language)
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
  fallbackLocale: DEFAULT_LOCALE,
  messages: {
    en,
    zh,
  },
})
