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

      <div class="diagnostics">
        <div class="diagnostics-header">
          <span class="diagnostics-title">{{ t('apiConfig.diagnostics.title') }}</span>
          <button class="diagnostics-refresh" type="button" @click="loadBackendDiagnostics(true)">
            {{ t('apiConfig.diagnostics.refresh') }}
          </button>
        </div>
        <p class="diagnostics-copy">{{ t('apiConfig.diagnostics.description') }}</p>
        <p v-if="backendLoading" class="diagnostics-state">{{ t('apiConfig.diagnostics.loading') }}</p>
        <p v-else-if="backendError" class="diagnostics-state diagnostics-state--error">{{ backendError }}</p>
        <div v-else-if="backendDiagnostic" class="diagnostics-card">
          <span class="diagnostics-badge" :class="`diagnostics-badge--${backendDiagnostic.tone}`">
            {{ backendDiagnostic.headline }}
          </span>
          <p v-if="backendDiagnostic.note" class="diagnostics-state diagnostics-state--warning">
            {{ backendDiagnostic.note }}
          </p>
          <div v-if="backendDiagnostic.nextSteps?.length" class="diagnostics-next-steps">
            <p class="diagnostics-next-steps-title">{{ t('apiConfig.diagnostics.nextStepsTitle') }}</p>
            <ul class="diagnostics-next-steps-list">
              <li
                v-for="step in backendDiagnostic.nextSteps"
                :key="step"
                class="diagnostics-next-step"
              >
                {{ step }}
              </li>
            </ul>
          </div>
          <div class="diagnostics-grid">
            <div v-for="row in backendDiagnostic.rows" :key="row.label" class="diagnostics-row">
              <span class="diagnostics-label">{{ row.label }}</span>
              <span class="diagnostics-value">{{ row.value }}</span>
            </div>
          </div>
        </div>
      </div>

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
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatApiError } from '../api/errors'
import { getBackendConfigStatus } from '../api/graph'
import {
  clearStoredBaseURL,
  getStoredBaseURL,
  normalizeBaseURL,
  resolveBaseURL,
  setStoredBaseURL,
} from '../api/baseUrl'
import { buildBackendDiagnosticModel } from './apiConfigDiagnostics'

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
const backendLoading = ref(false)
const backendError = ref('')
const backendDiagnostic = ref(null)
const backendLoaded = ref(false)

const activeBaseURL = computed(() => {
  return resolveBaseURL({
    runtimeBaseURL: overrideBaseURL.value,
    envBaseURL: import.meta.env.VITE_API_BASE_URL,
    location: typeof window !== 'undefined' ? window.location : undefined,
  })
})

const loadBackendDiagnostics = async (forceRefresh = false) => {
  if (backendLoading.value || (backendLoaded.value && !forceRefresh)) {
    return
  }

  backendLoading.value = true
  backendError.value = ''

  try {
    const response = await getBackendConfigStatus()
    backendDiagnostic.value = buildBackendDiagnosticModel(response.data, t)
    backendLoaded.value = true
  } catch (err) {
    backendError.value = formatApiError({
      err,
      t,
      resolveBaseURL,
      locationOrigin: typeof window !== 'undefined' ? window.location.origin : '',
    })
  } finally {
    backendLoading.value = false
  }
}

watch(expanded, (isExpanded) => {
  if (isExpanded) {
    loadBackendDiagnostics()
  }
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
.input-label,
.diagnostics-copy,
.diagnostics-state,
.diagnostics-next-steps-title,
.diagnostics-next-step,
.diagnostics-label,
.diagnostics-value {
  font-size: 12px;
  line-height: 1.5;
}

.diagnostics {
  margin: 14px 0;
  padding: 12px;
  border: 1px solid #000;
  background: #fafafa;
}

.diagnostics-next-steps {
  margin: 10px 0 12px;
  padding: 10px;
  border: 1px dashed #000;
  background: #fff;
}

.diagnostics-next-steps-title {
  margin: 0 0 6px;
  font-weight: 700;
}

.diagnostics-next-steps-list {
  margin: 0;
  padding-left: 18px;
}

.diagnostics-next-step {
  margin: 0;
}

.diagnostics-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.diagnostics-title {
  font-size: 12px;
  font-weight: 700;
}

.diagnostics-refresh {
  padding: 4px 8px;
  border: 1px solid #000;
  background: #fff;
  font-size: 11px;
  cursor: pointer;
}

.diagnostics-copy,
.diagnostics-state {
  margin-top: 8px;
}

.diagnostics-state--error {
  color: #a40000;
}

.diagnostics-state--warning {
  color: #7a4b00;
}

.diagnostics-card {
  margin-top: 8px;
}

.diagnostics-badge {
  display: inline-flex;
  padding: 4px 8px;
  border: 1px solid #000;
  font-size: 11px;
  font-weight: 700;
}

.diagnostics-badge--ready {
  background: #e6ffed;
}

.diagnostics-badge--warning {
  background: #fff4d6;
}

.diagnostics-grid {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.diagnostics-row {
  display: grid;
  gap: 2px;
}

.diagnostics-label {
  color: #666;
}

.diagnostics-value {
  word-break: break-word;
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
