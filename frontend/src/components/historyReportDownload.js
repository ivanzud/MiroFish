const trimTrailingSlash = (value) => (value || '').replace(/\/+$/, '')

const sanitizeFilenamePart = (value) =>
  (value || '')
    .trim()
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')

export const buildHistoryReportDownloadUrl = (reportId, baseURL = '') => {
  if (!reportId) {
    return ''
  }

  return `${trimTrailingSlash(baseURL)}/api/report/${encodeURIComponent(reportId)}/download`
}

export const buildHistoryReportDownloadFilename = (reportId, simulationId) => {
  const reportPart = sanitizeFilenamePart(reportId)
  if (!reportPart) {
    return ''
  }

  const simulationPart = sanitizeFilenamePart(simulationId)
  return simulationPart
    ? `mirofish-report-${reportPart}--simulation-${simulationPart}.md`
    : `mirofish-report-${reportPart}.md`
}

export const triggerHistoryReportDownload = (
  reportId,
  {
    simulationId = '',
    baseURL = '',
    documentRef = typeof document !== 'undefined' ? document : null,
  } = {}
) => {
  const href = buildHistoryReportDownloadUrl(reportId, baseURL)
  const downloadName = buildHistoryReportDownloadFilename(reportId, simulationId)
  if (!href || !documentRef?.createElement) {
    return false
  }

  const anchor = documentRef.createElement('a')
  anchor.href = href
  anchor.download = downloadName || `${reportId}.md`
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
