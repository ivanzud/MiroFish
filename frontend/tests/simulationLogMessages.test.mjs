import test from 'node:test'
import assert from 'node:assert/strict'

import {
  formatPrepareProgressLog,
  formatSimulationPidLog,
  formatSimulationRoundLog,
  getPrepareStageLabel,
} from '../src/components/simulationLogMessages.js'

const t = (key, params = {}) => `${key}:${JSON.stringify(params)}`

test('prepare-stage helpers localize known stage codes', () => {
  assert.equal(
    getPrepareStageLabel('generating_profiles', '生成Agent人设', t),
    'step2.logs.stageLabels.generatingProfiles:{}'
  )

  assert.equal(
    getPrepareStageLabel('custom_stage', 'Custom label', t),
    'Custom label'
  )
})

test('prepare progress log keeps stage counts and item text', () => {
  assert.equal(
    formatPrepareProgressLog(
      {
        current_stage: 'generating_config',
        current_stage_name: '生成模拟配置',
        current_item: 2,
        total_items: 5,
        item_description: 'Building recommendation config',
        stage_index: 2,
        total_stages: 3,
      },
      t
    ),
    'step2.logs.progressStageWithItems:{"current":2,"total":5,"stage":"step2.logs.stageLabels.generatingConfig:{}","item":"Building recommendation config","index":2,"stages":3}'
  )

  assert.equal(
    formatPrepareProgressLog(
      {
        current_stage: 'copying_scripts',
        current_stage_name: '准备模拟脚本',
        current_item: 0,
        total_items: 0,
        item_description: 'Copying runtime files',
        stage_index: 3,
        total_stages: 3,
      },
      t
    ),
    'step2.logs.progressStageWithoutItems:{"current":0,"total":0,"stage":"step2.logs.stageLabels.copyingScripts:{}","item":"Copying runtime files","index":3,"stages":3}'
  )
})

test('simulation log helpers localize pid and per-platform round status', () => {
  assert.equal(
    formatSimulationPidLog(4321, t),
    'step3.pidLog:{"pid":4321}'
  )

  assert.equal(
    formatSimulationRoundLog(
      {
        platform: 'twitter',
        currentRound: 4,
        totalRounds: 12,
        simulatedHours: 2,
        actionsCount: 18,
      },
      t
    ),
    'step3.roundProgressLog:{"platform":"step3.platformNames.twitter:{}","currentRound":4,"totalRounds":12,"simulatedHours":2,"actionsCount":18}'
  )
})
