<template>
  <div class="api-endpoint-control" :class="{ compact }">
    <button
      class="toggle-btn"
      type="button"
      @click="expanded = !expanded"
      :aria-expanded="expanded ? 'true' : 'false'"
    >
      <span>{{ t('apiConfig.trigger') }}</span>
      <span class="toggle-value">{{ activeBaseURL || t('apiConfig.autoMode') }}</span>
    </button>

    <div v-if="expanded" class="panel">
      <div class="panel-header">
        <span class="panel-title">{{ t('apiConfig.title') }}</span>
        <span class="panel-mode">{{ overrideBaseURL ? t('apiConfig.customMode') : t('apiConfig.autoMode') }}</span>
      </div>

      <p class="panel-copy">{{ t('apiConfig.description') }}</p>

      <label class="input-label" for="api-base-url-input">{{ t('apiConfig.inputLabel') }}</label>
      <input
        id="api-base-url-input"
        v-model="draftBaseURL"
        class="endpoint-input"
        type="text"
        :placeholder="t('apiConfig.placeholder')"
        autocapitalize="off"
        autocomplete="off"
        spellcheck="false"
      />

      <div class="actions">
        <button class="save-btn" type="button" @click="save">{{ t('apiConfig.save') }}</button>
        <button class="reset-btn" type="button" @click="reset">{{ t('apiConfig.reset') }}</button>
      </div>

      <p class="current-endpoint">
        {{ t('apiConfig.current') }} <span>{{ activeBaseURL || t('apiConfig.autoMode') }}</span>
      </p>
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  clearStoredBaseURL,
  getStoredBaseURL,
  normalizeBaseURL,
  resolveBaseURL,
  setStoredBaseURL,
} from '../api/baseUrl'

const props = defineProps({
  compact: {
    type: Boolean,
    default: false,
  },
})

const { t } = useI18n()
const expanded = ref(false)
const message = ref('')
const overrideBaseURL = ref(getStoredBaseURL())
const draftBaseURL = ref(overrideBaseURL.value)

const activeBaseURL = computed(() => {
  return resolveBaseURL({
    runtimeBaseURL: overrideBaseURL.value,
    envBaseURL: import.meta.env.VITE_API_BASE_URL,
    location: typeof window !== 'undefined' ? window.location : undefined,
  })
})

const save = () => {
  const normalizedValue = normalizeBaseURL(draftBaseURL.value)
  if (normalizedValue && !/^https?:\/\//i.test(normalizedValue)) {
    message.value = t('apiConfig.invalid')
    return
  }

  const savedValue = setStoredBaseURL(normalizedValue)
  overrideBaseURL.value = savedValue
  draftBaseURL.value = savedValue
  message.value = savedValue ? t('apiConfig.saved') : t('apiConfig.autoSaved')
}

const reset = () => {
  clearStoredBaseURL()
  overrideBaseURL.value = ''
  draftBaseURL.value = ''
  message.value = t('apiConfig.resetDone')
}
</script>

<style scoped>
.api-endpoint-control {
  position: relative;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  max-width: 100%;
  padding: 10px 14px;
  border: 1px solid #000;
  background: #fff;
  color: #000;
  font-size: 12px;
  cursor: pointer;
}

.toggle-value {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #666;
}

.compact .toggle-btn {
  padding: 8px 12px;
}

.panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  z-index: 30;
  width: min(360px, 90vw);
  padding: 16px;
  border: 1px solid #000;
  background: #fff;
  box-shadow: 8px 8px 0 #000;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.panel-title {
  font-size: 13px;
  font-weight: 700;
}

.panel-mode {
  font-size: 11px;
  color: #666;
}

.panel-copy,
.current-endpoint,
.message,
.input-label {
  font-size: 12px;
  line-height: 1.5;
}

.input-label {
  display: block;
  margin: 12px 0 6px;
  font-weight: 700;
}

.endpoint-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #000;
  font: inherit;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.save-btn,
.reset-btn {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #000;
  font: inherit;
  cursor: pointer;
}

.save-btn {
  background: #000;
  color: #fff;
}

.reset-btn {
  background: #fff;
  color: #000;
}

.current-endpoint {
  margin-top: 12px;
}

.current-endpoint span,
.message {
  word-break: break-all;
}

.message {
  margin-top: 8px;
  color: #666;
}

@media (max-width: 720px) {
  .panel {
    left: 0;
    right: auto;
    width: min(360px, calc(100vw - 32px));
  }

  .toggle-btn {
    width: 100%;
    justify-content: space-between;
  }

  .toggle-value {
    max-width: 160px;
  }
}
</style>
