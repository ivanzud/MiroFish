export const buildBackendDiagnosticModel = (payload, t) => {
  const none = t('common.none')
  const summary = payload?.summary || {}
  const validation = payload?.validation || {}
  const llm = summary.llm || {}
  const capabilities = summary.capabilities || {}
  const sources = llm.sources || {}
  const validationErrors = Array.isArray(validation.errors) ? validation.errors : []
  const usesOpenAIAliases = Boolean(sources.uses_openai_aliases)
  const usesProjectAliases = Boolean(sources.uses_project_aliases)
  const baseUrlConflict = sources.base_url_conflict || null
  const hasBaseUrlConflict = Boolean(baseUrlConflict?.has_conflict)
  const hasZepMissingError = validationErrors.some((message) =>
    typeof message === 'string' && message.includes('ZEP_API_KEY'),
  )
  const llmBlockingErrors = validationErrors.filter((message) =>
    !(typeof message === 'string' && message.includes('ZEP_API_KEY')),
  )
  const isConfigured = llm.configured && llmBlockingErrors.length === 0 && !hasBaseUrlConflict
  const directLlmReady = Boolean(capabilities.direct_llm?.ready)
  const graphBuildReady = Boolean(capabilities.graph_build?.ready)
  const reportToolsReady = Boolean(capabilities.graph_report_tools?.ready)
  const step5Ready = Boolean(capabilities.existing_simulation_interaction?.ready)

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

  const capabilityValue = (capability) => {
    if (!capability || typeof capability !== 'object') {
      return none
    }
    if (capability.ready) {
      if (capability.requires_existing_simulation) {
        return t('apiConfig.diagnostics.capabilityReadyExistingSimulation')
      }
      return t('apiConfig.diagnostics.capabilityReady')
    }
    if (capability.requires_zep) {
      return t('apiConfig.diagnostics.capabilityNeedsZep')
    }
    if (capability.requires_existing_simulation) {
      return t('apiConfig.diagnostics.capabilityNeedsExistingSimulation')
    }
    return t('apiConfig.diagnostics.capabilityNeedsBackendConfig')
  }

  const nextSteps = []
  if (directLlmReady && hasZepMissingError && !graphBuildReady && !reportToolsReady) {
    nextSteps.push(t('apiConfig.diagnostics.nextStepOpenStep2'))
    if (step5Ready) {
      nextSteps.push(t('apiConfig.diagnostics.nextStepReuseStep5'))
    }
    nextSteps.push(t('apiConfig.diagnostics.nextStepWaitForNonZep'))
  }

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
      : isConfigured && hasZepMissingError
      ? t('apiConfig.diagnostics.zepMissingNote')
      : '',
    nextSteps,
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
      {
        label: t('apiConfig.diagnostics.directLlmLabel'),
        value: capabilityValue(capabilities.direct_llm),
      },
      {
        label: t('apiConfig.diagnostics.graphBuildLabel'),
        value: capabilityValue(capabilities.graph_build),
      },
      {
        label: t('apiConfig.diagnostics.reportToolsLabel'),
        value: capabilityValue(capabilities.graph_report_tools),
      },
      {
        label: t('apiConfig.diagnostics.step5Label'),
        value: capabilityValue(capabilities.existing_simulation_interaction),
      },
    ],
  }
}
