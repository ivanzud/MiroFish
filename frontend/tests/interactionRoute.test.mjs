import test from 'node:test'
import assert from 'node:assert/strict'

import { buildInteractionRoute } from '../src/components/interactionRoute.js'

test('buildInteractionRoute prefers report routes when a report id exists', () => {
  assert.deepEqual(buildInteractionRoute({ reportId: 'report_123', simulationId: 'sim_456' }), {
    name: 'Interaction',
    params: { reportId: 'report_123' },
  })
})

test('buildInteractionRoute falls back to simulation-only interaction routes', () => {
  assert.deepEqual(buildInteractionRoute({ simulationId: 'sim_456' }), {
    name: 'InteractionSimulation',
    params: { simulationId: 'sim_456' },
  })
})

test('buildInteractionRoute returns null when no usable identifiers exist', () => {
  assert.equal(buildInteractionRoute({ reportId: '   ', simulationId: '' }), null)
})
