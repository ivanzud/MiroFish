export const resolveReportReferenceValue = (reportId, unavailableLabel) => {
  if (typeof reportId === 'string' && reportId.trim()) {
    return reportId
  }

  return unavailableLabel
}
