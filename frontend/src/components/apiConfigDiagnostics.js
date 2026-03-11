export const buildBackendDiagnosticModel = (payload, t) => {
  const none = t('common.none')
  const summary = payload?.summary || {}
  const validation = payload?.validation || {}
  const llm = summary.llm || {}
  const sources = llm.sources || {}
  const usesOpenAIAliases = Boolean(sources.uses_openai_aliases)
  const usesProjectAliases = Boolean(sources.uses_project_aliases)
  const baseUrlConflict = sources.base_url_conflict || null
  const hasBaseUrlConflict = Boolean(baseUrlConflict?.has_conflict)
  const isConfigured = llm.configured && validation.is_valid !== false && !hasBaseUrlConflict

  let resolvedSource = t('apiConfig.diagnostics.sourceUnknown')
  if (usesOpenAIAliases && usesProjectAliases) {
    resolvedSource = t('apiConfig.diagnostics.sourceMixedAliases')
  } else if (usesOpenAIAliases) {
    resolvedSource = t('apiConfig.diagnostics.sourceOpenAIAliases')
  } else if (usesProjectAliases) {
    resolvedSource = t('apiConfig.diagnostics.sourceProjectAliases')
  }

  const resolvedEnvVars = [
    sources.api_key_env,
    sources.base_url_env,
    sources.model_env,
  ].filter(Boolean).join(' / ') || none

  return {
    tone: isConfigured ? 'ready' : 'warning',
    headline: hasBaseUrlConflict
      ? t('apiConfig.diagnostics.baseUrlConflictTitle')
      : isConfigured
      ? (usesOpenAIAliases
        ? t('apiConfig.diagnostics.configuredOpenAI')
        : t('apiConfig.diagnostics.configured'))
      : t('apiConfig.diagnostics.incomplete'),
    note: hasBaseUrlConflict
      ? t('apiConfig.diagnostics.baseUrlConflictNote', {
        selectedEnv: baseUrlConflict.selected_env || none,
        selectedValue: baseUrlConflict.selected_value || none,
        configuredEnvNames: (baseUrlConflict.configured_envs || [])
          .map((entry) => entry.name)
          .join(' / ') || none,
      })
      : '',
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
