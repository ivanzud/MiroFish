import test from 'node:test'
import assert from 'node:assert/strict'

import { deriveInterviewTimeoutSeconds, resolveTimeoutMs } from '../src/api/timeout.js'

test('resolveTimeoutMs falls back to the default when the env value is invalid', () => {
  assert.equal(resolveTimeoutMs('not-a-number'), 300000)
  assert.equal(resolveTimeoutMs('450000'), 450000)
})

test('deriveInterviewTimeoutSeconds leaves headroom under the client timeout', () => {
  assert.equal(
    deriveInterviewTimeoutSeconds({ requestTimeoutMs: 300000, interviewsCount: 1 }),
    90
  )

  assert.equal(
    deriveInterviewTimeoutSeconds({ requestTimeoutMs: 300000, interviewsCount: 10 }),
    270
  )
})

test('deriveInterviewTimeoutSeconds clamps oversized interview batches to the request budget', () => {
  assert.equal(
    deriveInterviewTimeoutSeconds({ requestTimeoutMs: 120000, interviewsCount: 20 }),
    115
  )
})
