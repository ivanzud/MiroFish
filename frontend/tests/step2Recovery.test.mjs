import test from 'node:test'
import assert from 'node:assert/strict'

import { getStep2RecoveryState } from '../src/components/step2Recovery.js'

test('returns null when no saved step 3 state exists', () => {
  assert.equal(
    getStep2RecoveryState({
      simulation_id: 'sim-idle',
      runner_status: 'idle',
      current_round: 0,
      total_rounds: 0,
    }),
    null,
  )
})

test('maps failed runs to the restart CTA', () => {
  assert.deepEqual(
    getStep2RecoveryState({
      simulation_id: 'sim-failed',
      runner_status: 'failed',
      current_round: 3,
      total_rounds: 12,
    }),
    {
      noticeKey: 'step2.savedRunFailedNotice',
      actionKey: 'step2.restartPreparedRun',
      route: {
        name: 'SimulationRun',
        params: { simulationId: 'sim-failed' },
        query: { replay: '1' },
      },
    },
  )
})

test('maps running runs to the reopen CTA', () => {
  assert.deepEqual(
    getStep2RecoveryState({
      simulation_id: 'sim-running',
      runner_status: 'running',
      current_round: 2,
      total_rounds: 12,
    }),
    {
      noticeKey: 'step2.savedRunResumeNotice',
      actionKey: 'step2.openSavedRun',
      route: {
        name: 'SimulationRun',
        params: { simulationId: 'sim-running' },
        query: { replay: '1' },
      },
    },
  )
})
