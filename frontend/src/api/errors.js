const MISSING_KEY_RE = /^([A-Z0-9_ /]+)\s*未配置$/
const CONFIG_INCOMPLETE_RE = /^后端配置不完整:\s*(.+)$/

const localizeBackendConfigMessage = (message, t) => {
  if (typeof message !== 'string' || !t) {
    return message
  }

  const normalized = message.trim()
  if (!normalized) {
    return message
  }

  const directMissingMatch = normalized.match(MISSING_KEY_RE)
  if (directMissingMatch) {
    return t('process.missingConfigKey', { name: directMissingMatch[1].trim() })
  }

  const configMatch = normalized.match(CONFIG_INCOMPLETE_RE)
  if (configMatch) {
    const detail = configMatch[1].trim()
    const translatedDetail = localizeBackendConfigMessage(detail, t)
    return t('process.backendConfigIncomplete', { details: translatedDetail })
  }

  return message
}

export const formatApiError = ({ err, t, resolveBaseURL, locationOrigin }) => {
  if (!err) return t('process.unknownError')

  if (err.code === 'ECONNABORTED' || String(err.message || '').includes('timeout')) {
    return t('process.requestTimeout')
  }

  if (err.message === 'Network Error') {
    const apiBase = resolveBaseURL() || locationOrigin
    return t('process.backendUnavailable', { apiBase })
  }

  const backendMessage = err.response?.data?.error || err.response?.data?.message
  if (backendMessage) return localizeBackendConfigMessage(backendMessage, t)

  return err.message || t('process.unknownError')
}
