import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildSimulationReplayRoute,
  hasReplayableSimulationState,
} from '../src/components/historyPlayback.js'
import {
  isReplayOnlyRoute,
  shouldAutoStartSimulation,
} from '../src/components/simulationReplay.js'

test('history playback detects replayable simulation states', () => {
  assert.equal(hasReplayableSimulationState({ runner_status: 'idle', current_round: 0, total_rounds: 0 }), false)
  assert.equal(hasReplayableSimulationState({ runner_status: 'completed', current_round: 12, total_rounds: 12 }), true)
  assert.equal(hasReplayableSimulationState({ runner_status: 'failed', current_round: 3, total_rounds: 12 }), true)
  assert.equal(hasReplayableSimulationState({ runner_status: 'idle', current_round: 2, total_rounds: 12 }), true)
})

test('history playback builds a replay-only Step 3 route', () => {
  assert.deepEqual(buildSimulationReplayRoute('sim_123'), {
    name: 'SimulationRun',
    params: { simulationId: 'sim_123' },
    query: { replay: '1' },
  })
})

test('simulation replay helpers block auto-start in replay-only mode', () => {
  assert.equal(isReplayOnlyRoute('1'), true)
  assert.equal(isReplayOnlyRoute('true'), true)
  assert.equal(isReplayOnlyRoute(undefined), false)

  assert.equal(shouldAutoStartSimulation({ replayOnly: true, resumed: false }), false)
  assert.equal(shouldAutoStartSimulation({ replayOnly: false, resumed: true }), false)
  assert.equal(shouldAutoStartSimulation({ replayOnly: false, resumed: false }), true)
})
