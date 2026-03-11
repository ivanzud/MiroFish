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
  if (backendMessage) return backendMessage

  return err.message || t('process.unknownError')
}
