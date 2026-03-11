export const buildBackendDiagnosticModel = (payload, t) => {
  const none = t('common.none')
  const summary = payload?.summary || {}
  const validation = payload?.validation || {}
  const llm = summary.llm || {}
  const sources = llm.sources || {}

  let resolvedSource = t('apiConfig.diagnostics.sourceUnknown')
  if (sources.uses_openai_aliases) {
    resolvedSource = t('apiConfig.diagnostics.sourceOpenAIAliases')
  } else if (sources.uses_project_aliases) {
    resolvedSource = t('apiConfig.diagnostics.sourceProjectAliases')
  }

  const resolvedEnvVars = [
    sources.api_key_env,
    sources.base_url_env,
    sources.model_env,
  ].filter(Boolean).join(' / ') || none

  return {
    tone: llm.configured && validation.is_valid !== false ? 'ready' : 'warning',
    headline: llm.configured && validation.is_valid !== false
      ? t('apiConfig.diagnostics.configured')
      : t('apiConfig.diagnostics.incomplete'),
    rows: [
      {
        label: t('apiConfig.diagnostics.modeLabel'),
        value: llm.backend_mode === 'openai_compatible'
          ? t('apiConfig.diagnostics.modeOpenAICompatible')
          : (llm.backend_mode || none),
      },
      {
        label: t('apiConfig.diagnostics.sourceLabel'),
        value: resolvedSource,
      },
      {
        label: t('apiConfig.diagnostics.envLabel'),
        value: resolvedEnvVars,
      },
      {
        label: t('apiConfig.diagnostics.baseUrlLabel'),
        value: llm.base_url || none,
      },
      {
        label: t('apiConfig.diagnostics.modelLabel'),
        value: llm.model || none,
      },
    ],
  }
}
