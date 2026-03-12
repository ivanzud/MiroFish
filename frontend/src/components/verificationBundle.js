const cleanValue = (value) => {
  if (typeof value !== 'string') {
    return ''
  }

  return value.trim()
}

const addLine = (lines, key, value) => {
  const cleaned = cleanValue(value)
  if (cleaned) {
    lines.push(`${key}: ${cleaned}`)
  }
}

export const buildVerificationReferenceBundle = ({
  simulationId = '',
  reportId = '',
  timestamp = '',
} = {}) => {
  const cleanedSimulationId = cleanValue(simulationId)
  const cleanedReportId = cleanValue(reportId)
  if (!cleanedSimulationId && !cleanedReportId) {
    return ''
  }

  const lines = ['MiroFish verification reference']

  addLine(lines, 'simulation_id', cleanedSimulationId)
  addLine(lines, 'report_id', cleanedReportId)
  addLine(lines, 'timestamp', timestamp)

  if (cleanedReportId) {
    lines.push(`report_markdown_path: backend/uploads/reports/${cleanedReportId}/full_report.md`)
  }

  return lines.join('\n')
}
