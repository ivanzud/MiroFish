const trimTrailingSlash = (value) => (value || '').replace(/\/+$/, '')

export const buildHistoryReportDownloadUrl = (reportId, baseURL = '') => {
  if (!reportId) {
    return ''
  }

  return `${trimTrailingSlash(baseURL)}/api/report/${encodeURIComponent(reportId)}/download`
}

export const triggerHistoryReportDownload = (
  reportId,
  {
    baseURL = '',
    documentRef = typeof document !== 'undefined' ? document : null,
  } = {}
) => {
  const href = buildHistoryReportDownloadUrl(reportId, baseURL)
  if (!href || !documentRef?.createElement) {
    return false
  }

  const anchor = documentRef.createElement('a')
  anchor.href = href
  anchor.download = `${reportId}.md`
  anchor.rel = 'noopener'
  anchor.style.display = 'none'

  const parent = documentRef.body || documentRef.documentElement
  parent?.appendChild?.(anchor)
  anchor.click()

  if (typeof anchor.remove === 'function') {
    anchor.remove()
  } else {
    parent?.removeChild?.(anchor)
  }

  return true
}
