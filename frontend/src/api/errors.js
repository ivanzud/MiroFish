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

const getCapabilityHint = (payload, t) => {
  if (!payload || !t) {
    return ''
  }

  const capabilities = payload?.data?.summary?.capabilities || payload?.summary?.capabilities
  if (!capabilities || typeof capabilities !== 'object') {
    return ''
  }

  const directLlmReady = Boolean(capabilities.direct_llm?.ready)
  const zepBlocked = [capabilities.graph_build, capabilities.graph_report_tools].some((capability) =>
    capability && capability.ready === false && capability.requires_zep,
  )

  if (directLlmReady && zepBlocked) {
    return t('apiConfig.diagnostics.zepMissingNote')
  }

  return ''
}

const appendHint = (message, hint) => {
  if (!hint) {
    return message
  }
  if (!message) {
    return hint
  }
  if (message.includes(hint)) {
    return message
  }
  return `${message} ${hint}`
}

export const formatApiError = ({
  err,
  t,
  resolveBaseURL = () => '',
  locationOrigin = '',
}) => {
  if (!err) return t('process.unknownError')

  if (err.code === 'ECONNABORTED' || String(err.message || '').includes('timeout')) {
    return t('process.requestTimeout')
  }

  if (err.message === 'Network Error') {
    const apiBase = resolveBaseURL() || locationOrigin
    return t('process.backendUnavailable', { apiBase })
  }

  const backendMessage = err.response?.data?.error || err.response?.data?.message
  if (backendMessage) {
    return appendHint(
      localizeBackendConfigMessage(backendMessage, t),
      getCapabilityHint(err.response?.data, t),
    )
  }

  return err.message || t('process.unknownError')
}
