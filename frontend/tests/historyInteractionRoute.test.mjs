import test from 'node:test'
import assert from 'node:assert/strict'

import { buildInteractionRoute } from '../src/components/interactionRoute.js'

test('history interaction prefers the report-backed Step 5 route when available', () => {
  assert.deepEqual(buildInteractionRoute({ reportId: 'report_123', simulationId: 'sim_456' }), {
    name: 'Interaction',
    params: { reportId: 'report_123' },
  })
})

test('history interaction falls back to the simulation-only Step 5 route', () => {
  assert.deepEqual(buildInteractionRoute({ reportId: '', simulationId: 'sim_456' }), {
    name: 'InteractionSimulation',
    params: { simulationId: 'sim_456' },
  })
})
