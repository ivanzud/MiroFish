import test from 'node:test'
import assert from 'node:assert/strict'

import { buildVerificationReferenceBundle } from '../src/components/verificationBundle.js'

test('buildVerificationReferenceBundle includes stable report and simulation references', () => {
  assert.equal(
    buildVerificationReferenceBundle({
      simulationId: 'sim_123',
      reportId: 'report_456',
      timestamp: '2026-03-12T03:50:00Z',
    }),
    [
      'MiroFish verification reference',
      'simulation_id: sim_123',
      'report_id: report_456',
      'timestamp: 2026-03-12T03:50:00Z',
      'report_markdown_path: backend/uploads/reports/report_456/full_report.md',
    ].join('\n')
  )
})

test('buildVerificationReferenceBundle omits blank optional fields', () => {
  assert.equal(
    buildVerificationReferenceBundle({
      simulationId: ' sim_123 ',
      reportId: '   ',
      timestamp: '',
    }),
    [
      'MiroFish verification reference',
      'simulation_id: sim_123',
    ].join('\n')
  )
})
