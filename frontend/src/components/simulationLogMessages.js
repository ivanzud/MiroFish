export function getPrepareStageLabel(stage, fallbackLabel, t) {
  if (!stage) {
    return fallbackLabel || ''
  }

  const keyMap = {
    generating_profiles: 'step2.logs.stageLabels.generatingProfiles',
    generating_config: 'step2.logs.stageLabels.generatingConfig',
    copying_scripts: 'step2.logs.stageLabels.copyingScripts',
  }

  const key = keyMap[stage]
  return key ? t(key) : (fallbackLabel || stage)
}

export function formatPrepareProgressLog(detail, t) {
  if (!detail?.item_description) {
    return ''
  }

  const stageLabel = getPrepareStageLabel(detail.current_stage, detail.current_stage_name, t)
  const params = {
    current: detail.current_item,
    total: detail.total_items,
    stage: stageLabel,
    item: detail.item_description,
    index: detail.stage_index,
    stages: detail.total_stages,
  }

  if (detail.total_items > 0) {
    return t('step2.logs.progressStageWithItems', params)
  }

  return t('step2.logs.progressStageWithoutItems', params)
}

export function formatSimulationPidLog(pid, t) {
  return t('step3.pidLog', { pid: pid || '-' })
}

export function formatSimulationRoundLog(
  { platform, currentRound, totalRounds, simulatedHours, actionsCount },
  t
) {
  const platformLabel = t(`step3.platformNames.${platform}`)
  return t('step3.roundProgressLog', {
    platform: platformLabel,
    currentRound,
    totalRounds,
    simulatedHours: simulatedHours || 0,
    actionsCount: actionsCount || 0,
  })
}
