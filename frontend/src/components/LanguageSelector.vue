<template>
  <div class="language-selector" :class="{ light }">
    <button class="lang-btn" :class="{ active: locale === 'zh' }" @click="setLocale('zh')">
      {{ t('nav.zh') }}
    </button>
    <span class="lang-sep">/</span>
    <button class="lang-btn" :class="{ active: locale === 'en' }" @click="setLocale('en')">
      {{ t('nav.en') }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getStoredLocale, setStoredLocale } from '../i18n'

const props = defineProps({
  light: {
    type: Boolean,
    default: false,
  },
})

const { locale, t } = useI18n()

const syncDocumentLanguage = (value) => {
  document.documentElement.lang = value === 'en' ? 'en' : 'zh-CN'
}

const setLocale = (value) => {
  locale.value = value
  setStoredLocale(value)
  syncDocumentLanguage(value)
}

const light = computed(() => props.light)

syncDocumentLanguage(getStoredLocale())
</script>

<style scoped>
.language-selector {
  display: flex;
  align-items: center;
  gap: 4px;
}

.lang-btn {
  background: none;
  border: none;
  padding: 4px 8px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #000;
  cursor: pointer;
  transition: color 0.2s;
}

.lang-btn:hover {
  color: #333;
}

.lang-btn.active {
  font-weight: 700;
}

.lang-sep {
  color: #333;
  font-size: 0.75rem;
}

.language-selector.light .lang-btn,
.language-selector.light .lang-sep {
  color: #000;
}
</style>
