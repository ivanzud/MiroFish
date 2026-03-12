import test from 'node:test'
import assert from 'node:assert/strict'

import { getStep5RecoveryState } from '../src/components/step5Recovery.js'

test('returns null when the interview environment is still alive', () => {
  assert.equal(
    getStep5RecoveryState({
      simulation: {
        simulation_id: 'sim-running',
        runner_status: 'running',
        current_round: 2,
        total_rounds: 12,
      },
      envStatus: {
        env_alive: true,
      },
    }),
    null,
  )
})

test('returns the Step 3 replay route when offline state is recoverable', () => {
  assert.deepEqual(
    getStep5RecoveryState({
      simulation: {
        simulation_id: 'sim-failed',
        runner_status: 'failed',
        current_round: 3,
        total_rounds: 12,
      },
      envStatus: {
        env_alive: false,
      },
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

test('returns null when no replayable simulation state exists', () => {
  assert.equal(
    getStep5RecoveryState({
      simulation: {
        simulation_id: 'sim-idle',
        runner_status: 'idle',
        current_round: 0,
        total_rounds: 0,
      },
      envStatus: {
        env_alive: false,
      },
    }),
    null,
  )
})
