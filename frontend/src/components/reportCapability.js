export const getReportPreflightBlockReason = (payload, t) => {
  if (!t) {
    return ''
  }

  const capabilities = payload?.summary?.capabilities || payload?.data?.summary?.capabilities
  if (!capabilities || typeof capabilities !== 'object') {
    return ''
  }

  const reportTools = capabilities.graph_report_tools
  if (!reportTools || reportTools.ready !== false) {
    return ''
  }

  if (reportTools.requires_zep && capabilities.direct_llm?.ready) {
    return t('apiConfig.diagnostics.zepMissingNote')
  }

  if (reportTools.requires_existing_simulation) {
    return t('apiConfig.diagnostics.capabilityNeedsExistingSimulation')
  }

  return t('apiConfig.diagnostics.capabilityNeedsBackendConfig')
}
